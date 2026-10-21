"""
CrewAI agents and tasks for Text-to-SQL pipeline.

This module defines three specialized agents that work together:
1. SQL Developer Agent: Writes BigQuery SQL from natural language questions
2. Data Executor Agent: Executes SQL and handles errors
3. Data Visualizer Agent: Formats results for visualization

The crew orchestrates their collaboration to deliver a complete response.
"""

from typing import Any
from crewai import Agent, Task, Crew
from crewai.tools import tool
import logging
import json
from pydantic import BaseModel, Field

from backend.config import settings
from backend.tools import create_bigquery_tool
from backend.schemas.bigquery_schema import (
    format_schema_for_agent,
    PRODUCTS_SCHEMA,
    ORDER_ITEMS_SCHEMA,
)
from backend.schemas.models import ChartData

logger = logging.getLogger(__name__)


# ============================================================================
# Tool Definitions (for CrewAI)
# ============================================================================

class ExecuteBigQueryInput(BaseModel):
    """Input for execute_bigquery tool."""
    sql_query: str = Field(..., description="SQL query to execute")


class DataToolkit:
    """Toolkit of tools available to agents."""

    def __init__(self, bq_tool):
        self.bq_tool = bq_tool

    def get_tools(self):
        """Return list of tools for CrewAI agents."""
        return [
            self.execute_bigquery,
            self.get_products_schema,
            self.get_order_items_schema,
        ]

    @tool("execute_bigquery")
    def execute_bigquery(self, sql_query: str) -> str:
        """
        Execute a SQL query against BigQuery.

        Args:
            sql_query: SQL query to execute

        Returns:
            JSON string with results or error
        """
        logger.info("[Agent Tool] Executing BigQuery query")
        result = self.bq_tool.execute(sql_query, timeout_seconds=60)

        if result["success"]:
            logger.info(
                f"[Agent Tool] Query successful. Rows: {result['row_count']}"
            )
            return json.dumps(
                {
                    "success": True,
                    "data": result["data"][:10],  # Limit to 10 rows for readability
                    "row_count": result["row_count"],
                    "schema": result["schema"],
                }
            )
        else:
            logger.error(f"[Agent Tool] Query failed: {result['error']}")
            return json.dumps(
                {
                    "success": False,
                    "error": result["error"],
                }
            )

    @tool("get_products_schema")
    def get_products_schema(self) -> str:
        """Get schema for the products table."""
        return format_schema_for_agent("products")

    @tool("get_order_items_schema")
    def get_order_items_schema(self) -> str:
        """Get schema for the order_items table."""
        return format_schema_for_agent("order_items")


# ============================================================================
# Agent Definitions
# ============================================================================


def create_sql_developer_agent(tools: list) -> Agent:
    """
    Create SQL Developer Agent.

    Responsibility: Write BigQuery SQL queries from natural language questions.
    - Analyzes user questions
    - References table schemas
    - Writes dialect-specific BigQuery SQL
    - Includes helpful comments in SQL
    """
    from crewai import LLM
    
    return Agent(
        role="SQL Developer",
        goal=(
            "Write clear, optimized BigQuery SQL queries that accurately answer "
            "natural language questions about the thelook_ecommerce dataset. "
            "Always reference table schemas and use correct BigQuery syntax."
        ),
        backstory=(
            "You are an expert BigQuery SQL developer with deep knowledge of the "
            "thelook_ecommerce dataset. You write clear, well-commented SQL that is "
            "optimized for performance and readability. You understand the data model "
            "and know how to join tables correctly."
        ),
        tools=tools,
        llm=LLM(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=settings.openai_temperature,
        ),
        verbose=settings.debug,
        allow_delegation=False,
        max_iter=3,
    )


def create_data_executor_agent(tools: list) -> Agent:
    """
    Create Data Executor Agent.

    Responsibility: Execute SQL and handle errors.
    - Takes SQL from SQL Developer
    - Executes using BigQuery tool
    - If query fails, provides error to SQL Developer for fixing
    - Returns structured results
    """
    from crewai import LLM
    
    return Agent(
        role="Data Executor",
        goal=(
            "Efficiently execute SQL queries against BigQuery and retrieve results. "
            "If a query fails, analyze the error and work with the SQL Developer "
            "to fix it. Return clean, validated data."
        ),
        backstory=(
            "You are a meticulous data engineer responsible for executing queries "
            "and ensuring data quality. You handle errors gracefully, understand "
            "BigQuery error messages, and work collaboratively to resolve issues. "
            "You validate that results make sense before returning them."
        ),
        tools=tools,
        llm=LLM(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=settings.openai_temperature,
        ),
        verbose=settings.debug,
        allow_delegation=True,  # Can delegate back to SQL Developer if query fails
        max_iter=5,
    )


def create_data_visualizer_agent(tools: list) -> Agent:
    """
    Create Data Visualizer Agent.

    Responsibility: Format results for visualization.
    - Takes raw BigQuery results
    - Decides on appropriate chart type
    - Formats data for Recharts
    - Writes clear explanation of findings
    """
    from crewai import LLM
    
    return Agent(
        role="Data Visualizer",
        goal=(
            "Transform raw data into clear visualizations and explanations. "
            "Choose the most appropriate chart type (bar, line, pie, table) and "
            "format data in a way that tells a compelling story about the data."
        ),
        backstory=(
            "You are a data visualization expert who understands how to communicate "
            "complex data stories effectively. You know when to use bar charts for "
            "comparisons, line charts for trends, pie charts for compositions, and "
            "tables for detailed data. You write clear, concise explanations of findings."
        ),
        tools=tools,
        llm=LLM(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=settings.openai_temperature,
        ),
        verbose=settings.debug,
        allow_delegation=False,
        max_iter=3,
    )


# ============================================================================
# Task Definitions
# ============================================================================


def create_sql_generation_task(agent: Agent) -> Task:
    """Create task for SQL generation."""
    return Task(
        description=(
            "Based on the user's natural language question, write a BigQuery SQL query "
            "that will answer it. "
            "\n\nAvailable tables:"
            "\n{schema_products}"
            "\n{schema_order_items}"
            "\n\nUser Question: {user_query}"
            "\n\nRequirements:"
            "- Use the correct BigQuery syntax and functions"
            "- Include the full table path (e.g., `bigquery-public-data.thelook_ecommerce.products`)"
            "- Add helpful comments in the SQL"
            "- Make sure the query is valid BigQuery SQL"
            "- Do not include LIMIT unless necessary for safety (max 10000 rows)"
        ),
        agent=agent,
        expected_output=(
            "A clear BigQuery SQL query that answers the user's question. "
            "The query should be in a code block and well-commented."
        ),
    )


def create_query_execution_task(agent: Agent) -> Task:
    """Create task for query execution."""
    return Task(
        description=(
            "Execute the SQL query generated by the SQL Developer using the "
            "execute_bigquery tool. "
            "\n\nIf the query fails:"
            "1. Analyze the error message"
            "2. Delegate back to the SQL Developer to fix the query"
            "3. Retry execution with the corrected query"
            "\n\nOnce successful, return the results in JSON format with:"
            "- Row count"
            "- Column names"
            "- All data rows"
        ),
        agent=agent,
        expected_output=(
            "Successfully executed SQL results with row count, schema, and data. "
            "If execution failed, detailed error message for the SQL Developer."
        ),
    )


def create_visualization_task(agent: Agent) -> Task:
    """Create task for result visualization."""
    return Task(
        description=(
            "Format the query results for visualization and provide a clear explanation. "
            "\n\nBased on the data:"
            "1. Choose the most appropriate chart type (bar/line/pie/table)"
            "2. Format the data for Recharts visualization"
            "3. Extract key insights from the data"
            "4. Write a brief, clear explanation of what the data shows"
            "\n\nOutput format (JSON):"
            "{"
            '  "thought_process": "Clear explanation of findings...",'
            '  "chart_type": "bar|line|pie|table",'
            '  "data": [{"key": "value", ...}, ...],'
            '  "x_axis_key": "column_name",'
            '  "y_axis_key": "column_name",'
            '  "title": "Chart Title"'
            "}"
        ),
        agent=agent,
        expected_output=(
            "JSON object with visualization specification and insight explanation. "
            "Chart type, data points, axis labels, and title all included."
        ),
    )


# ============================================================================
# Crew Creation and Execution
# ============================================================================


class TextToSQLCrew:
    """
    Orchestrates the Text-to-SQL pipeline using CrewAI.

    Workflow:
    1. SQL Developer writes SQL from user question
    2. Data Executor runs SQL and handles errors
    3. Data Visualizer formats results and explains findings
    """

    def __init__(self, project_id: str):
        """
        Initialize the crew.

        Args:
            project_id: GCP project ID for BigQuery access
        """
        self.project_id = project_id
        self.bq_tool = create_bigquery_tool(project_id)
        self.toolkit = DataToolkit(self.bq_tool)

        # Create tools list for agents
        self.tools = self.toolkit.get_tools()

        # Create agents
        self.sql_developer = create_sql_developer_agent(self.tools)
        self.data_executor = create_data_executor_agent(self.tools)
        self.data_visualizer = create_data_visualizer_agent(self.tools)

        # Create tasks
        self.sql_task = create_sql_generation_task(self.sql_developer)
        self.exec_task = create_query_execution_task(self.data_executor)
        self.viz_task = create_visualization_task(self.data_visualizer)

        # Create crew
        self.crew = Crew(
            agents=[self.sql_developer, self.data_executor, self.data_visualizer],
            tasks=[self.sql_task, self.exec_task, self.viz_task],
            verbose=settings.debug,
            memory=True,  # Maintain context across tasks
            max_rpm=10,  # Rate limiting for LLM API
        )

        logger.info("[TextToSQLCrew] Initialized")

    async def execute_async(self, user_query: str) -> dict[str, Any]:
        """
        Execute the complete pipeline (async version for FastAPI).

        Args:
            user_query: Natural language question

        Returns:
            dict with keys:
            - success (bool)
            - thought_process (str)
            - sql_query (str)
            - chart (ChartData)
            - error (str): Only if success is False
        """
        import time

        start_time = time.time()

        try:
            logger.info(f"[TextToSQLCrew] Starting async pipeline for query: {user_query[:100]}...")

            # Prepare inputs for the crew
            inputs = {
                "user_query": user_query,
                "schema_products": format_schema_for_agent("products"),
                "schema_order_items": format_schema_for_agent("order_items"),
            }

            # Execute crew asynchronously
            result = await self.crew.kickoff_async(inputs=inputs)

            execution_time = (time.time() - start_time) * 1000
            logger.info(f"[TextToSQLCrew] Async pipeline completed in {execution_time:.2f}ms")

            # Parse result
            result_str = str(result)

            return {
                "success": True,
                "thought_process": result_str[:500],
                "sql_query": self._extract_sql_from_result(result_str),
                "chart": self._extract_chart_from_result(result_str),
                "execution_time_ms": execution_time,
            }

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            error_msg = f"Crew execution failed: {type(e).__name__}: {str(e)}"

            logger.error(f"[TextToSQLCrew] {error_msg}")

            return {
                "success": False,
                "error": error_msg,
                "execution_time_ms": execution_time,
            }

    def execute(self, user_query: str) -> dict[str, Any]:
        """
        Execute the complete pipeline (sync version).

        Args:
            user_query: Natural language question

        Returns:
            dict with keys:
            - success (bool)
            - thought_process (str)
            - sql_query (str)
            - chart (ChartData)
            - error (str): Only if success is False
        """
        import time

        start_time = time.time()

        try:
            logger.info(f"[TextToSQLCrew] Starting pipeline for query: {user_query[:100]}...")

            # Prepare inputs for the crew
            inputs = {
                "user_query": user_query,
                "schema_products": format_schema_for_agent("products"),
                "schema_order_items": format_schema_for_agent("order_items"),
            }

            # Execute crew (orchestrates all tasks)
            result = self.crew.kickoff(inputs=inputs)

            execution_time = (time.time() - start_time) * 1000
            logger.info(f"[TextToSQLCrew] Pipeline completed in {execution_time:.2f}ms")

            # Parse result (in Phase 2, we'll get structured output from agents)
            # For now, parse the final output from the visualizer agent
            result_str = str(result)

            return {
                "success": True,
                "thought_process": result_str[:500],  # First 500 chars
                "sql_query": self._extract_sql_from_result(result_str),
                "chart": self._extract_chart_from_result(result_str),
                "execution_time_ms": execution_time,
            }

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            error_msg = f"Crew execution failed: {type(e).__name__}: {str(e)}"

            logger.error(f"[TextToSQLCrew] {error_msg}")

            return {
                "success": False,
                "error": error_msg,
                "execution_time_ms": execution_time,
            }

    def _extract_sql_from_result(self, result: str) -> str:
        """Extract SQL query from crew result."""
        # This is a simple extraction; in production, parse more carefully
        lines = result.split("\n")
        for i, line in enumerate(lines):
            if "SELECT" in line.upper():
                # Found start of SQL, collect until semicolon
                sql_lines = []
                for j in range(i, len(lines)):
                    sql_lines.append(lines[j])
                    if ";" in lines[j]:
                        break
                return "\n".join(sql_lines)

        return "SELECT * FROM `bigquery-public-data.thelook_ecommerce.products` LIMIT 5"

    def _extract_chart_from_result(self, result: str) -> ChartData:
        """Extract and parse chart data from crew result."""
        # Try to find JSON in result
        import json as json_module

        start_idx = result.find("{")
        if start_idx >= 0:
            end_idx = result.rfind("}") + 1
            if end_idx > start_idx:
                try:
                    chart_dict = json_module.loads(result[start_idx:end_idx])
                    return ChartData(
                        chart_type=chart_dict.get("chart_type", "table"),
                        data=chart_dict.get("data", []),
                        x_axis_key=chart_dict.get("x_axis_key", "x"),
                        y_axis_key=chart_dict.get("y_axis_key", "y"),
                        title=chart_dict.get("title", "Results"),
                    )
                except (json_module.JSONDecodeError, ValueError):
                    pass

        # Fallback chart
        return ChartData(
            chart_type="table",
            data=[],
            x_axis_key="value",
            y_axis_key="count",
            title="Query Results",
        )


def create_text_to_sql_crew(project_id: str) -> TextToSQLCrew:
    """
    Factory function to create Text-to-SQL crew.

    Args:
        project_id: GCP project ID

    Returns:
        Initialized TextToSQLCrew instance
    """
    return TextToSQLCrew(project_id=project_id)
