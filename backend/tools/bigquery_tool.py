"""
BigQuery tool for executing SQL queries and retrieving results.

This module provides a LangChain-compatible tool that:
- Executes SQL queries against BigQuery
- Handles errors gracefully
- Returns results in structured format
- Supports schema introspection
"""

from typing import Optional, Any
import json
from google.cloud import bigquery
from google.cloud.exceptions import GoogleCloudError, BadRequest
import logging

logger = logging.getLogger(__name__)


class BigQueryTool:
    """
    Tool for executing SQL queries against Google BigQuery.
    
    Handles:
    - Query execution with timeout
    - Error recovery and reporting
    - Result formatting as JSON
    - Schema caching and inspection
    """

    def __init__(self, project_id: str, max_results: int = 10000):
        """
        Initialize BigQuery tool.
        
        Args:
            project_id: GCP project ID
            max_results: Maximum rows to return per query (safety limit)
        
        Raises:
            ValueError: If project_id is empty
        """
        if not project_id:
            raise ValueError("project_id cannot be empty")
        
        self.project_id = project_id
        self.max_results = max_results
        self.client = bigquery.Client(project=project_id)
        self._schema_cache = {}
        
        logger.info(f"[BigQueryTool] Initialized for project: {project_id}")

    def execute(
        self,
        query: str,
        timeout_seconds: int = 60,
        job_config: Optional[dict] = None,
    ) -> dict[str, Any]:
        """
        Execute a SQL query against BigQuery.
        
        Args:
            query: SQL query string
            timeout_seconds: Query timeout in seconds
            job_config: Optional query job configuration
        
        Returns:
            dict with keys:
            - success (bool): Whether query executed successfully
            - data (list): Rows as dicts (empty if failed)
            - row_count (int): Number of rows returned
            - schema (list): Column names
            - error (str): Error message if failed
            - execution_time_ms (float): Query execution time
        
        Examples:
            >>> tool = BigQueryTool("my-project")
            >>> result = tool.execute("SELECT * FROM `project.dataset.table` LIMIT 5")
            >>> if result['success']:
            ...     print(f"Got {result['row_count']} rows")
            ... else:
            ...     print(f"Error: {result['error']}")
        """
        import time
        
        start_time = time.time()
        
        try:
            # Validate query
            if not query or not query.strip():
                return {
                    "success": False,
                    "data": [],
                    "row_count": 0,
                    "schema": [],
                    "error": "Query cannot be empty",
                    "execution_time_ms": 0,
                }

            # Configure query job
            query_config = bigquery.QueryJobConfig()
            if job_config:
                # Apply any custom config
                for key, value in job_config.items():
                    setattr(query_config, key, value)

            logger.info(f"[BigQueryTool] Executing query (timeout: {timeout_seconds}s)")
            logger.debug(f"[BigQueryTool] Query: {query[:200]}...")

            # Execute query
            query_job = self.client.query(query, job_config=query_config)
            results = query_job.result(timeout=timeout_seconds)

            # Extract field names from schema
            field_names = [field.name for field in results.schema]
            
            # Convert results to list of dicts
            rows = []
            for row in results:
                row_dict = {key: value for key, value in zip(field_names, row)}
                rows.append(row_dict)

                # Safety limit
                if len(rows) >= self.max_results:
                    logger.warning(
                        f"[BigQueryTool] Result set truncated at {self.max_results} rows"
                    )
                    break

            execution_time = (time.time() - start_time) * 1000

            logger.info(
                f"[BigQueryTool] Query succeeded. Rows: {len(rows)}, "
                f"Time: {execution_time:.2f}ms"
            )

            return {
                "success": True,
                "data": rows,
                "row_count": len(rows),
                "schema": field_names,
                "error": None,
                "execution_time_ms": execution_time,
            }

        except BadRequest as e:
            # SQL syntax or semantic errors
            error_msg = str(e)
            execution_time = (time.time() - start_time) * 1000
            
            logger.error(f"[BigQueryTool] SQL Error: {error_msg}")
            
            return {
                "success": False,
                "data": [],
                "row_count": 0,
                "schema": [],
                "error": f"SQL Error: {error_msg}",
                "execution_time_ms": execution_time,
            }

        except TimeoutError:
            # Query took too long
            execution_time = (time.time() - start_time) * 1000
            error_msg = f"Query timeout after {timeout_seconds} seconds"
            
            logger.error(f"[BigQueryTool] {error_msg}")
            
            return {
                "success": False,
                "data": [],
                "row_count": 0,
                "schema": [],
                "error": error_msg,
                "execution_time_ms": execution_time,
            }

        except GoogleCloudError as e:
            # GCP API errors
            execution_time = (time.time() - start_time) * 1000
            error_msg = f"BigQuery API Error: {str(e)}"
            
            logger.error(f"[BigQueryTool] {error_msg}")
            
            return {
                "success": False,
                "data": [],
                "row_count": 0,
                "schema": [],
                "error": error_msg,
                "execution_time_ms": execution_time,
            }

        except Exception as e:
            # Unexpected errors
            execution_time = (time.time() - start_time) * 1000
            error_msg = f"Unexpected Error: {type(e).__name__}: {str(e)}"
            
            logger.error(f"[BigQueryTool] {error_msg}")
            
            return {
                "success": False,
                "data": [],
                "row_count": 0,
                "schema": [],
                "error": error_msg,
                "execution_time_ms": execution_time,
            }

    def get_table_schema(self, dataset_id: str, table_id: str) -> dict[str, Any]:
        """
        Retrieve schema for a specific table.
        
        Args:
            dataset_id: BigQuery dataset ID
            table_id: BigQuery table ID
        
        Returns:
            dict with keys:
            - success (bool)
            - schema (list): List of field dicts with name, type, mode
            - error (str): Error message if failed
        
        Example:
            >>> tool = BigQueryTool("my-project")
            >>> schema = tool.get_table_schema("thelook_ecommerce", "products")
        """
        cache_key = f"{dataset_id}.{table_id}"
        
        # Check cache
        if cache_key in self._schema_cache:
            logger.debug(f"[BigQueryTool] Schema cache hit for {cache_key}")
            return self._schema_cache[cache_key]

        try:
            table_id_full = f"{self.project_id}.{dataset_id}.{table_id}"
            table = self.client.get_table(table_id_full)
            
            schema_list = []
            for field in table.schema:
                schema_list.append({
                    "name": field.name,
                    "type": field.field_type,
                    "mode": field.mode,
                    "description": field.description or "",
                })
            
            result = {
                "success": True,
                "schema": schema_list,
                "error": None,
            }
            
            # Cache the result
            self._schema_cache[cache_key] = result
            
            logger.info(f"[BigQueryTool] Retrieved schema for {cache_key}")
            return result

        except Exception as e:
            error_msg = f"Failed to get schema: {str(e)}"
            logger.error(f"[BigQueryTool] {error_msg}")
            
            result = {
                "success": False,
                "schema": [],
                "error": error_msg,
            }
            
            # Cache the error result
            self._schema_cache[cache_key] = result
            return result

    def list_tables(self, dataset_id: str) -> dict[str, Any]:
        """
        List all tables in a dataset.
        
        Args:
            dataset_id: BigQuery dataset ID
        
        Returns:
            dict with keys:
            - success (bool)
            - tables (list): Table IDs
            - error (str): Error message if failed
        """
        try:
            dataset_ref = bigquery.DatasetReference(self.project_id, dataset_id)
            tables = self.client.list_tables(dataset_ref)
            
            table_list = [table.table_id for table in tables]
            
            logger.info(f"[BigQueryTool] Listed {len(table_list)} tables in {dataset_id}")
            
            return {
                "success": True,
                "tables": table_list,
                "error": None,
            }

        except Exception as e:
            error_msg = f"Failed to list tables: {str(e)}"
            logger.error(f"[BigQueryTool] {error_msg}")
            
            return {
                "success": False,
                "tables": [],
                "error": error_msg,
            }


# Create a singleton instance wrapper for LangChain tool integration
def create_bigquery_tool(project_id: str, max_results: int = 10000) -> BigQueryTool:
    """
    Factory function to create BigQuery tool instance.
    
    Args:
        project_id: GCP project ID
        max_results: Maximum rows to return
    
    Returns:
        Configured BigQueryTool instance
    """
    return BigQueryTool(project_id=project_id, max_results=max_results)
