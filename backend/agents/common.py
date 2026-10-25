"""
Building blocks shared by the simplified and multi-agent (CrewAI) pipelines.

Anything that protects the GCP project or shapes the API response lives here
so both pipelines apply exactly the same rules:
- the SQL-writing rules given to the LLM
- extracting SQL from LLM output and the read-only guard
- choosing a chart for a result set
- the plain summary used when no analyst insights are available
"""

import re

from schemas.bigquery_schema import SCHEMAS, format_schema_for_agent
from schemas.models import ChartData


# Max rows returned to the frontend for rendering
MAX_DISPLAY_ROWS = 100

RELATIONSHIPS = """Relationships:
- order_items.order_id = orders.order_id
- order_items.product_id = products.id
- order_items.user_id = users.id and orders.user_id = users.id"""

SQL_RULES = """Requirements:
- Write a single read-only SELECT query (WITH clauses allowed) in GoogleSQL
- Use the exact, fully qualified table paths shown above, wrapped in backticks
- Only use columns listed above
- Give every table an alias and qualify columns with it, e.g.
  FROM `bigquery-public-data.thelook_ecommerce.users` AS u ... u.id
- Revenue means SUM(order_items.sale_price)
- Only filter by date or status when the question asks for it
- For shares/percentages use a window function, e.g.
  ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_total
- For time series return one DATE column, e.g.
  DATE_TRUNC(DATE(created_at), MONTH) AS month, not separate year/month numbers
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
- Limit results to 1000 rows maximum for performance"""

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


def schemas_text() -> str:
    """All table schemas formatted for an LLM prompt."""
    return "\n\n".join(format_schema_for_agent(table) for table in SCHEMAS)


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


def format_chart_data(data: list[dict], schema: list[str]) -> ChartData:
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


def summarize(user_query: str, result: dict, chart: ChartData, corrected: bool) -> str:
    """Build the plain explanation shown above the results."""
    row_count = result["row_count"]
    total_rows = result.get("total_rows") or row_count
    lines = [
        f"Question: {user_query}",
        "",
        "Generated and executed a BigQuery SQL query"
        + (" (automatically corrected after a BigQuery error)." if corrected else "."),
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
