"""
Simplified Phase 2: Direct BigQuery Tool Integration

This module provides a working Text-to-SQL implementation that:
1. Takes a user query
2. Uses LangChain to generate SQL from the BigQuery schema
3. Executes the SQL using BigQueryTool
4. Returns results formatted for visualization

The simplified version focuses on reliability over advanced agent orchestration.
This can be upgraded to full CrewAI multi-agent system in a future iteration.
"""

import logging
import json
from typing import Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from backend.config import settings
from backend.tools import create_bigquery_tool
from backend.schemas.bigquery_schema import format_schema_for_agent
from backend.schemas.models import ChartData

logger = logging.getLogger(__name__)


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
        self.bq_tool = create_bigquery_tool(project_id, max_results=1000)
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=0.3,  # Lower temperature for more precise SQL
            api_key=settings.openai_api_key,
        )
        
        # Schemas for reference
        self.products_schema = format_schema_for_agent("products")
        self.order_items_schema = format_schema_for_agent("order_items")
        
        logger.info(f"[SimplifiedPipeline] Initialized for project: {project_id}")

    async def execute_async(self, user_query: str) -> dict[str, Any]:
        """
        Execute the complete pipeline asynchronously.

        Args:
            user_query: Natural language question

        Returns:
            dict with success status, SQL query, results, and visualization data
        """
        import time
        start_time = time.time()

        try:
            logger.info(f"[Pipeline] Processing query: {user_query[:100]}...")

            # Step 1: Generate SQL from natural language
            sql_query = await self._generate_sql(user_query)
            logger.info(f"[Pipeline] Generated SQL: {sql_query[:100]}...")

            # Step 2: Execute SQL against BigQuery
            result = self.bq_tool.execute(sql_query, timeout_seconds=60)
            
            if not result["success"]:
                return {
                    "success": False,
                    "error": result["error"],
                    "execution_time_ms": (time.time() - start_time) * 1000,
                }

            logger.info(f"[Pipeline] Query executed. Rows: {result['row_count']}")

            # Step 3: Format results for visualization
            chart = self._format_chart_data(result["data"], result["schema"])
            logger.info(f"[Pipeline] Chart type: {chart.chart_type}")

            execution_time = (time.time() - start_time) * 1000

            return {
                "success": True,
                "thought_process": (
                    f"Successfully processed your question: {user_query}\n\n"
                    f"Generated and executed a BigQuery SQL query.\n"
                    f"Retrieved {result['row_count']} rows of data.\n"
                    f"Formatted results as a {chart.chart_type} visualization."
                ),
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
                "execution_time_ms": execution_time,
            }

    async def _generate_sql(self, user_query: str) -> str:
        """
        Generate BigQuery SQL from natural language using LLM.

        Args:
            user_query: Natural language question

        Returns:
            SQL query string
        """
        prompt_template = PromptTemplate(
            input_variables=["user_query", "products_schema", "order_items_schema"],
            template="""You are an expert BigQuery SQL developer. Generate a BigQuery SQL query that answers the user's question.

Available Tables:
{products_schema}

{order_items_schema}

User Question: {user_query}

Requirements:
- Write valid BigQuery SQL using the exact table paths shown above
- Include backticks around table names
- Limit results to 1000 rows maximum for performance
- Make sure the query is optimized and correct
- Return ONLY the SQL query, nothing else

SQL Query:"""
        )

        chain = prompt_template | self.llm
        
        try:
            response = await chain.ainvoke({
                "user_query": user_query,
                "products_schema": self.products_schema,
                "order_items_schema": self.order_items_schema,
            })
            
            # Extract SQL from response
            sql_query = response.content.strip()
            
            # Clean up common issues
            if sql_query.startswith("```sql"):
                sql_query = sql_query[6:]
            if sql_query.startswith("```"):
                sql_query = sql_query[3:]
            if sql_query.endswith("```"):
                sql_query = sql_query[:-3]
            
            sql_query = sql_query.strip()
            
            return sql_query

        except Exception as e:
            logger.error(f"[Pipeline] SQL generation failed: {str(e)}")
            # Fallback query
            return "SELECT * FROM `bigquery-public-data.thelook_ecommerce.products` LIMIT 10"

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
                x_axis_key="value",
                y_axis_key="count",
                title="No Results",
            )

        # Determine chart type based on data shape
        num_rows = len(data)
        num_cols = len(schema) if schema else 0

        # Default: table for complex data or many columns
        if num_cols > 3 or num_rows > 10:
            return ChartData(
                chart_type="table",
                data=data[:100],  # Limit to 100 rows for display
                x_axis_key=schema[0] if schema else "value",
                y_axis_key=schema[1] if len(schema) > 1 else "count",
                title="Query Results (Table View)",
            )

        # Try to detect numeric columns for charts
        numeric_cols = []
        string_cols = []

        for row in data[:5]:  # Sample first 5 rows
            for col in schema:
                value = row.get(col)
                if isinstance(value, (int, float)) and col not in numeric_cols:
                    numeric_cols.append(col)
                elif isinstance(value, str) and col not in string_cols:
                    string_cols.append(col)

        # Choose chart type based on data
        if numeric_cols and string_cols:
            # Bar chart: categories on X-axis, numeric values on Y
            return ChartData(
                chart_type="bar",
                data=data,
                x_axis_key=string_cols[0],
                y_axis_key=numeric_cols[0],
                title="Results (Bar Chart)",
            )
        elif len(numeric_cols) >= 2:
            # Line chart: two numeric dimensions
            return ChartData(
                chart_type="line",
                data=data,
                x_axis_key=numeric_cols[0],
                y_axis_key=numeric_cols[1],
                title="Results (Line Chart)",
            )
        else:
            # Default to table
            return ChartData(
                chart_type="table",
                data=data,
                x_axis_key=schema[0] if schema else "value",
                y_axis_key=schema[1] if len(schema) > 1 else "count",
                title="Query Results",
            )


def create_simplified_pipeline(project_id: str) -> SimplifiedTextToSQLPipeline:
    """
    Factory function to create pipeline instance.

    Args:
        project_id: GCP project ID

    Returns:
        Initialized SimplifiedTextToSQLPipeline
    """
    return SimplifiedTextToSQLPipeline(project_id=project_id)
