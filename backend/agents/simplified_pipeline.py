"""
Simplified Phase 2: Direct BigQuery Tool Integration

This module provides a working Text-to-SQL implementation that:
1. Takes a user query
2. Uses LangChain to generate SQL from the BigQuery schema
3. Validates the SQL is a single read-only query
4. Executes the SQL using BigQueryTool (retrying once with the error fed back
   to the LLM if BigQuery rejects the query)
5. Returns results formatted for visualization

The simplified version focuses on reliability over advanced agent orchestration.
This can be upgraded to full CrewAI multi-agent system in a future iteration.
"""

import asyncio
import logging
import re
import time
from typing import Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

from config import settings
from tools import create_bigquery_tool
from schemas.bigquery_schema import SCHEMAS, format_schema_for_agent
from schemas.models import ChartData

logger = logging.getLogger(__name__)


# Number of times a query rejected by BigQuery is sent back to the LLM to fix
MAX_SQL_FIX_ATTEMPTS = 2

# Max rows returned to the frontend for rendering
MAX_DISPLAY_ROWS = 100

SQL_PROMPT = PromptTemplate(
    input_variables=["user_query", "schemas", "previous_attempt"],
    template="""You are an expert BigQuery SQL developer. Generate a BigQuery SQL query that answers the user's question.

Available Tables:
{schemas}

Relationships:
- order_items.order_id = orders.order_id
- order_items.product_id = products.id
- order_items.user_id = users.id and orders.user_id = users.id

User Question: {user_query}
{previous_attempt}
Requirements:
- Write a single read-only SELECT query (WITH clauses allowed) in GoogleSQL
- Use the exact, fully qualified table paths shown above, wrapped in backticks
- Only use columns listed above
- Revenue means SUM(order_items.sale_price)
- Only filter by date when the question asks about a time period
- All *_at columns are TIMESTAMP. Never compare a TIMESTAMP with a DATE: wrap the
  column in DATE(...) and compare it with DATE values
- TIMESTAMP_SUB/TIMESTAMP_ADD do not accept WEEK, MONTH or YEAR; use DATE_SUB on
  CURRENT_DATE() instead. Recipes:
  - last N days: DATE(created_at) BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL N DAY) AND CURRENT_DATE()
  - last month (previous calendar month):
    DATE(created_at) >= DATE_TRUNC(DATE_SUB(CURRENT_DATE(), INTERVAL 1 MONTH), MONTH)
    AND DATE(created_at) < DATE_TRUNC(CURRENT_DATE(), MONTH)
  - this year: EXTRACT(YEAR FROM created_at) = EXTRACT(YEAR FROM CURRENT_DATE())
- The data contains some future-dated rows, so relative date filters need an
  upper bound of CURRENT_DATE() as in the recipes above
- Give aggregated columns short snake_case aliases (e.g. total_revenue)
- Put the category/date column first and the main numeric measure second
- Order time series chronologically; order rankings by the measure
- Limit results to 1000 rows maximum for performance
- Return ONLY the SQL query, nothing else

SQL Query:""",
)

_SQL_FENCE_RE = re.compile(r"```(?:sql|googlesql|bigquery)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)
_STRING_OR_COMMENT_RE = re.compile(
    r"""
    '(?:\\.|[^'\\])*'      # single-quoted string
    | "(?:\\.|[^"\\])*"    # double-quoted string
    | `[^`]*`              # backtick identifier
    | --[^\n]*             # line comment
    | \#[^\n]*             # hash comment
    | /\*.*?\*/            # block comment
    """,
    re.DOTALL | re.VERBOSE,
)
_ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}(-\d{2})?([T ]\d{2}:\d{2}.*)?$")


def extract_sql(llm_output: str) -> str:
    """
    Pull the SQL statement out of an LLM response.

    Handles fenced code blocks (with or without a language tag), surrounding
    prose, and a trailing semicolon.
    """
    text = llm_output.strip()
    fenced = _SQL_FENCE_RE.search(text)
    if fenced:
        text = fenced.group(1).strip()
    else:
        # No fence: drop any prose before the first SELECT/WITH keyword
        start = re.search(r"\b(SELECT|WITH)\b", text, re.IGNORECASE)
        if start:
            text = text[start.start():]
    return text.strip().rstrip(";").strip()


def validate_read_only_sql(sql: str) -> str | None:
    """
    Check that SQL is a single read-only query.

    The SQL comes from an LLM driven by user input, so it must not be able to
    run DML/DDL or multi-statement scripts against the GCP project.

    Returns:
        An error message, or None if the query is acceptable
    """
    if not sql:
        return "The model did not return a SQL query."

    stripped = _STRING_OR_COMMENT_RE.sub(" ", sql).strip()
    if ";" in stripped:
        return "Only a single SQL statement is allowed."
    first_word = stripped.split(None, 1)[0].upper() if stripped else ""
    if first_word not in ("SELECT", "WITH"):
        return "Only read-only SELECT queries are allowed."
    return None


class SimplifiedTextToSQLPipeline:
    """
    Simplified Text-to-SQL pipeline using LangChain for SQL generation
    and BigQuery tool for execution.

    This avoids CrewAI complexity while still providing:
    - Natural language to SQL conversion
    - BigQuery execution
    - Result visualization formatting
    """

    def __init__(self, project_id: str):
        """
        Initialize the pipeline.

        Args:
            project_id: GCP project ID for BigQuery
        """
        self.project_id = project_id
        self.bq_tool = create_bigquery_tool(
            project_id,
            max_results=settings.bq_max_results_rows,
            credentials_path=settings.resolved_credentials_path(),
            max_bytes_billed=settings.bq_max_bytes_billed,
        )
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=0,  # Deterministic output for more precise SQL
            max_tokens=settings.openai_max_tokens,
            api_key=settings.openai_api_key,
            timeout=30,
            max_retries=2,
        )

        # Schemas for reference
        self.schemas = "\n\n".join(format_schema_for_agent(table) for table in SCHEMAS)

        logger.info(f"[SimplifiedPipeline] Initialized for project: {project_id}")

    async def execute_async(self, user_query: str) -> dict[str, Any]:
        """
        Execute the complete pipeline asynchronously.

        Args:
            user_query: Natural language question

        Returns:
            dict with success status, SQL query, results, and visualization data
        """
        start_time = time.time()
        sql_query = ""

        try:
            logger.info(f"[Pipeline] Processing query: {user_query[:100]}...")

            previous_attempt = ""
            for attempt in range(MAX_SQL_FIX_ATTEMPTS + 1):
                # Step 1: Generate SQL from natural language
                sql_query = await self._generate_sql(user_query, previous_attempt)
                logger.info(f"[Pipeline] Generated SQL: {sql_query[:100]}...")

                validation_error = validate_read_only_sql(sql_query)
                if validation_error:
                    return {
                        "success": False,
                        "error": f"Rejected generated SQL: {validation_error}",
                        "sql_query": sql_query,
                        "execution_time_ms": (time.time() - start_time) * 1000,
                    }

                # Step 2: Execute SQL against BigQuery (blocking client, so run
                # it in a worker thread to keep the event loop responsive)
                result = await asyncio.to_thread(
                    self.bq_tool.execute,
                    sql_query,
                    timeout_seconds=settings.bq_query_timeout_seconds,
                )
                if result["success"]:
                    break

                is_sql_error = result["error"].startswith("SQL Error")
                if not is_sql_error or attempt == MAX_SQL_FIX_ATTEMPTS:
                    return {
                        "success": False,
                        "error": result["error"],
                        "sql_query": sql_query,
                        "execution_time_ms": (time.time() - start_time) * 1000,
                    }

                logger.info("[Pipeline] SQL rejected by BigQuery, asking the model to fix it")
                previous_attempt = (
                    "\nA previous attempt failed. Fix the query so it runs.\n"
                    f"Previous SQL:\n{sql_query}\n"
                    f"BigQuery error:\n{result['error'][:1000]}\n"
                )

            logger.info(f"[Pipeline] Query executed. Rows: {result['row_count']}")

            # Step 3: Format results for visualization
            chart = self._format_chart_data(result["data"], result["schema"])
            logger.info(f"[Pipeline] Chart type: {chart.chart_type}")

            execution_time = (time.time() - start_time) * 1000

            return {
                "success": True,
                "thought_process": self._summarize(user_query, result, chart, attempt),
                "sql_query": sql_query,
                "chart": chart,
                "execution_time_ms": execution_time,
            }

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            error_msg = f"Pipeline error: {type(e).__name__}: {str(e)}"
            logger.error(f"[Pipeline] {error_msg}")

            return {
                "success": False,
                "error": error_msg,
                "sql_query": sql_query,
                "execution_time_ms": execution_time,
            }

    def _summarize(self, user_query: str, result: dict, chart: ChartData, attempt: int) -> str:
        """Build the human-readable explanation shown above the results."""
        row_count = result["row_count"]
        total_rows = result.get("total_rows") or row_count
        lines = [
            f"Question: {user_query}",
            "",
            "Generated and executed a BigQuery SQL query"
            + (" (automatically corrected after a BigQuery error)." if attempt else "."),
        ]
        if total_rows > row_count:
            lines.append(f"Retrieved the first {row_count:,} of {total_rows:,} rows.")
        else:
            lines.append(f"Retrieved {row_count:,} row{'s' if row_count != 1 else ''}.")
        if len(chart.data) < row_count:
            lines.append(f"Showing the first {len(chart.data):,} rows below.")
        if row_count:
            view = "table" if chart.chart_type == "table" else f"{chart.chart_type} chart"
            lines.append(f"Displayed as a {view}.")
        return "\n".join(lines)

    async def _generate_sql(self, user_query: str, previous_attempt: str = "") -> str:
        """
        Generate BigQuery SQL from natural language using LLM.

        Args:
            user_query: Natural language question
            previous_attempt: Failed SQL and error to correct, if retrying

        Returns:
            SQL query string

        Raises:
            Exception with specific error message for model not found or other issues
        """
        chain = SQL_PROMPT | self.llm

        try:
            response = await chain.ainvoke({
                "user_query": user_query,
                "schemas": self.schemas,
                "previous_attempt": previous_attempt,
            })

            return extract_sql(response.content)

        except Exception as e:
            error_str = str(e)

            # Detect and provide specific error messages
            if "model" in error_str.lower() and "not found" in error_str.lower():
                # Model not found error from OpenAI API
                model_name = settings.openai_model
                logger.error(f"[Pipeline] SQL generation failed: Model '{model_name}' not found or unavailable")
                raise Exception(
                    f"OpenAI model '{model_name}' is not available. "
                    f"This model may have been deprecated. "
                    f"Please update OPENAI_MODEL in configuration to a valid model like 'gpt-4o-mini' or 'gpt-4o'. "
                    f"Error: {error_str}"
                )
            elif "authentication" in error_str.lower() or "unauthorized" in error_str.lower():
                logger.error(f"[Pipeline] SQL generation failed: Authentication error")
                raise Exception(
                    f"OpenAI API authentication failed. "
                    f"Please check your OPENAI_API_KEY configuration. "
                    f"Error: {error_str}"
                )
            elif "rate" in error_str.lower():
                logger.error(f"[Pipeline] SQL generation failed: Rate limit exceeded")
                raise Exception(
                    f"OpenAI API rate limit exceeded. "
                    f"Please wait a moment and try again. "
                    f"Error: {error_str}"
                )
            else:
                logger.error(f"[Pipeline] SQL generation failed: {error_str}")
                raise Exception(f"Failed to generate SQL: {error_str}")

    def _format_chart_data(self, data: list[dict], schema: list[str]) -> ChartData:
        """
        Format query results for Recharts visualization.

        Args:
            data: List of result rows as dicts
            schema: List of column names

        Returns:
            ChartData with appropriate chart type and formatting
        """
        if not data:
            return ChartData(
                chart_type="table",
                data=[],
                x_axis_key=schema[0] if schema else "value",
                y_axis_key=schema[1] if len(schema) > 1 else "count",
                title="No Results",
            )

        num_rows = len(data)
        num_cols = len(schema)

        def table() -> ChartData:
            return ChartData(
                chart_type="table",
                data=data[:MAX_DISPLAY_ROWS],
                x_axis_key=schema[0],
                y_axis_key=schema[1] if num_cols > 1 else schema[0],
                title="Query Results",
            )

        # Charts only make sense for a label column plus one or two measures
        if num_cols < 2 or num_cols > 3:
            return table()

        # Classify columns by looking at every non-null value. bool is a
        # subclass of int, so exclude it from the numeric check explicitly.
        def column_kind(col: str) -> str:
            values = [row.get(col) for row in data if row.get(col) is not None]
            if not values:
                return "empty"
            if all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in values):
                return "numeric"
            if all(isinstance(v, str) and _ISO_DATE_RE.match(v) for v in values):
                return "date"
            if all(isinstance(v, str) for v in values):
                return "string"
            return "other"

        kinds = {col: column_kind(col) for col in schema}
        numeric_cols = [c for c in schema if kinds[c] == "numeric"]
        date_cols = [c for c in schema if kinds[c] == "date"]
        string_cols = [c for c in schema if kinds[c] == "string"]

        if date_cols and numeric_cols and num_rows <= MAX_DISPLAY_ROWS:
            # Line chart: time series
            return ChartData(
                chart_type="line",
                data=data,
                x_axis_key=date_cols[0],
                y_axis_key=numeric_cols[0],
                title=f"{numeric_cols[0]} over {date_cols[0]}",
            )
        if string_cols and numeric_cols and num_rows <= 30:
            # Bar chart: categories on X-axis, numeric values on Y
            return ChartData(
                chart_type="bar",
                data=data,
                x_axis_key=string_cols[0],
                y_axis_key=numeric_cols[0],
                title=f"{numeric_cols[0]} by {string_cols[0]}",
            )
        if len(numeric_cols) >= 2 and not string_cols and num_rows <= MAX_DISPLAY_ROWS:
            # Line chart: two numeric dimensions (e.g. year vs. revenue)
            return ChartData(
                chart_type="line",
                data=data,
                x_axis_key=numeric_cols[0],
                y_axis_key=numeric_cols[1],
                title=f"{numeric_cols[1]} by {numeric_cols[0]}",
            )
        return table()


def create_simplified_pipeline(project_id: str) -> SimplifiedTextToSQLPipeline:
    """
    Factory function to create pipeline instance.

    Args:
        project_id: GCP project ID

    Returns:
        Initialized SimplifiedTextToSQLPipeline
    """
    return SimplifiedTextToSQLPipeline(project_id=project_id)
