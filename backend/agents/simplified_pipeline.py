"""
Simplified Phase 2: Direct BigQuery Tool Integration

This module provides a working Text-to-SQL implementation that:
1. Takes a user query
2. Uses LangChain to generate SQL from the BigQuery schema
3. Validates the SQL is a single read-only query
4. Executes the SQL using BigQueryTool (retrying with the error fed back
   to the LLM if BigQuery rejects the query)
5. Returns results formatted for visualization

This is the default pipeline (PIPELINE_MODE=simple): one LLM call per
question in the common case. The multi-agent alternative lives in
agents/data_crew.py.
"""

import asyncio
import logging
import time
from typing import Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

from config import settings
from tools import create_bigquery_tool
from agents.common import (
    RELATIONSHIPS,
    SQL_RULES,
    extract_sql,
    format_chart_data,
    schemas_text,
    summarize,
    validate_read_only_sql,
)

logger = logging.getLogger(__name__)


# Number of times a query rejected by BigQuery is sent back to the LLM to fix
MAX_SQL_FIX_ATTEMPTS = 2

SQL_PROMPT = PromptTemplate(
    input_variables=["user_query", "schemas", "previous_attempt"],
    template=f"""You are an expert BigQuery SQL developer. Generate a BigQuery SQL query that answers the user's question.

Available Tables:
{{schemas}}

{RELATIONSHIPS}

User Question: {{user_query}}
{{previous_attempt}}
{SQL_RULES}
- Return ONLY the SQL query, nothing else

SQL Query:""",
)


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
        self.schemas = schemas_text()

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
            chart = format_chart_data(result["data"], result["schema"])
            logger.info(f"[Pipeline] Chart type: {chart.chart_type}")

            execution_time = (time.time() - start_time) * 1000

            return {
                "success": True,
                "thought_process": summarize(user_query, result, chart, corrected=attempt > 0),
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
            raise describe_llm_error(e) from e

    def _format_chart_data(self, data: list[dict], schema: list[str]):
        """Kept for backwards compatibility; see agents.common.format_chart_data."""
        return format_chart_data(data, schema)


def describe_llm_error(e: Exception) -> Exception:
    """Turn an OpenAI/LLM exception into an actionable error message."""
    error_str = str(e)
    lowered = error_str.lower()

    # Detect and provide specific error messages
    if "model" in lowered and "not found" in lowered:
        # Model not found error from OpenAI API
        model_name = settings.openai_model
        logger.error(f"[Pipeline] SQL generation failed: Model '{model_name}' not found or unavailable")
        return Exception(
            f"OpenAI model '{model_name}' is not available. "
            f"This model may have been deprecated. "
            f"Please update OPENAI_MODEL in configuration to a valid model like 'gpt-4o-mini' or 'gpt-4o'. "
            f"Error: {error_str}"
        )
    if "authentication" in lowered or "unauthorized" in lowered:
        logger.error("[Pipeline] SQL generation failed: Authentication error")
        return Exception(
            f"OpenAI API authentication failed. "
            f"Please check your OPENAI_API_KEY configuration. "
            f"Error: {error_str}"
        )
    if "rate" in lowered:
        logger.error("[Pipeline] SQL generation failed: Rate limit exceeded")
        return Exception(
            f"OpenAI API rate limit exceeded. "
            f"Please wait a moment and try again. "
            f"Error: {error_str}"
        )
    logger.error(f"[Pipeline] SQL generation failed: {error_str}")
    return Exception(f"Failed to generate SQL: {error_str}")


def create_simplified_pipeline(project_id: str) -> SimplifiedTextToSQLPipeline:
    """
    Factory function to create pipeline instance.

    Args:
        project_id: GCP project ID

    Returns:
        Initialized SimplifiedTextToSQLPipeline
    """
    return SimplifiedTextToSQLPipeline(project_id=project_id)
