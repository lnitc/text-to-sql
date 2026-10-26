"""
BigQuery tool for executing SQL queries and retrieving results.

This module provides a LangChain-compatible tool that:
- Executes SQL queries against BigQuery
- Handles errors gracefully
- Returns results in structured format
- Supports schema introspection
"""

from typing import Optional, Any
import base64
import datetime
import decimal
import re
from google.cloud import bigquery
from google.cloud.exceptions import GoogleCloudError, BadRequest
import logging

logger = logging.getLogger(__name__)

_REQUEST_URL_RE = re.compile(r"(?:(?:GET|POST|PUT|PATCH|DELETE) )?https?://\S+")
_JOB_DETAILS_RE = re.compile(r"^\s*(?:Location|Job ID):.*$", re.MULTILINE)
_SERVICE_ACCOUNT_RE = re.compile(r"[\w.+-]+@[\w-]+\.iam\.gserviceaccount\.com")


def safe_error_message(error: Exception, project_id: str = "") -> str:
    """
    Describe a BigQuery/Google API error without identifying details.

    Error text is shown to users and sent to the LLM, but str(error) embeds
    the request URL (which contains the GCP project ID), job IDs and, for
    permission errors, the service account email. Full errors are still
    logged server-side.
    """
    # Structured errors carry just the human-readable reason
    errors = getattr(error, "errors", None) or []
    message = errors[0].get("message") if errors and isinstance(errors[0], dict) else None
    if not message:
        message = getattr(error, "message", None) or str(error)

    message = _REQUEST_URL_RE.sub("", message)
    message = _JOB_DETAILS_RE.sub("", message)
    message = _SERVICE_ACCOUNT_RE.sub("<service-account>", message)
    if project_id:
        message = message.replace(project_id, "<project>")
    return " ".join(message.split()).lstrip(": ")


def _to_json_value(value: Any) -> Any:
    """
    Convert BigQuery cell values into JSON/chart-friendly Python types.

    NUMERIC/BIGNUMERIC come back as Decimal (which Pydantic serializes as a
    string, breaking charts), DATE/TIMESTAMP as date/datetime objects, and
    BYTES as bytes. REPEATED/RECORD fields are converted recursively.
    """
    if isinstance(value, decimal.Decimal):
        return float(value)
    if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
        return value.isoformat()
    if isinstance(value, bytes):
        return base64.b64encode(value).decode("ascii")
    if isinstance(value, dict):
        return {k: _to_json_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_to_json_value(v) for v in value]
    return value


class BigQueryTool:
    """
    Tool for executing SQL queries against Google BigQuery.
    
    Handles:
    - Query execution with timeout
    - Error recovery and reporting
    - Result formatting as JSON
    - Schema caching and inspection
    """

    def __init__(
        self,
        project_id: str,
        max_results: int = 10000,
        credentials_path: Optional[str] = None,
        max_bytes_billed: Optional[int] = None,
    ):
        """
        Initialize BigQuery tool.
        
        Args:
            project_id: GCP project ID
            max_results: Maximum rows to return per query (safety limit)
            credentials_path: Service account JSON key file. If omitted,
                Application Default Credentials are used.
            max_bytes_billed: Queries that would scan more bytes than this
                fail instead of running (cost guard)
        
        Raises:
            ValueError: If project_id is empty
        """
        if not project_id:
            raise ValueError("project_id cannot be empty")
        
        self.project_id = project_id
        self.max_results = max_results
        self.max_bytes_billed = max_bytes_billed
        if credentials_path:
            self.client = bigquery.Client.from_service_account_json(
                credentials_path, project=project_id
            )
        else:
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
            - total_rows (int): Rows in the full result (may exceed row_count)
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
            if self.max_bytes_billed:
                query_config.maximum_bytes_billed = self.max_bytes_billed
            if job_config:
                # Apply any custom config
                for key, value in job_config.items():
                    setattr(query_config, key, value)

            logger.info(f"[BigQueryTool] Executing query (timeout: {timeout_seconds}s)")
            logger.debug(f"[BigQueryTool] Query: {query[:200]}...")

            # Execute query
            query_job = self.client.query(query, job_config=query_config)
            # max_results stops the client from downloading rows we'd discard
            results = query_job.result(
                timeout=timeout_seconds, max_results=self.max_results
            )

            # Extract field names from schema
            field_names = [field.name for field in results.schema]
            
            # Convert results to list of JSON-friendly dicts
            rows = [
                {key: _to_json_value(value) for key, value in zip(field_names, row)}
                for row in results
            ]
            total_rows = results.total_rows if results.total_rows is not None else len(rows)
            if total_rows > len(rows):
                logger.warning(
                    f"[BigQueryTool] Result set truncated at {len(rows)} of {total_rows} rows"
                )

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
                "total_rows": total_rows,
                "error": None,
                "execution_time_ms": execution_time,
            }

        except BadRequest as e:
            # SQL syntax or semantic errors
            error_msg = safe_error_message(e, self.project_id)
            execution_time = (time.time() - start_time) * 1000

            logger.error(f"[BigQueryTool] SQL Error: {e}")

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
            error_msg = f"BigQuery API Error: {safe_error_message(e, self.project_id)}"

            logger.error(f"[BigQueryTool] BigQuery API Error: {e}")
            
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
            error_msg = f"Unexpected Error: {type(e).__name__}: {safe_error_message(e, self.project_id)}"

            logger.error(f"[BigQueryTool] Unexpected Error: {type(e).__name__}: {e}")
            
            return {
                "success": False,
                "data": [],
                "row_count": 0,
                "schema": [],
                "error": error_msg,
                "execution_time_ms": execution_time,
            }

    def dry_run(self, query: str) -> dict[str, Any]:
        """
        Validate a query with a BigQuery dry run (free; nothing is executed).

        Args:
            query: SQL query string

        Returns:
            dict with keys:
            - success (bool): Whether BigQuery accepted the query
            - bytes_processed (int): Bytes the query would scan
            - error (str): Error message if invalid
        """
        try:
            query_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
            query_job = self.client.query(query, job_config=query_config)
            bytes_processed = query_job.total_bytes_processed or 0
            if self.max_bytes_billed and bytes_processed > self.max_bytes_billed:
                return {
                    "success": False,
                    "bytes_processed": bytes_processed,
                    "error": (
                        f"Query would scan {bytes_processed:,} bytes, over the "
                        f"{self.max_bytes_billed:,} byte limit"
                    ),
                }
            return {"success": True, "bytes_processed": bytes_processed, "error": None}
        except BadRequest as e:
            message = safe_error_message(e, self.project_id)
            return {"success": False, "bytes_processed": 0, "error": f"SQL Error: {message}"}
        except Exception as e:
            return {
                "success": False,
                "bytes_processed": 0,
                "error": f"Dry run failed: {type(e).__name__}: {safe_error_message(e, self.project_id)}",
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
            error_msg = f"Failed to get schema: {safe_error_message(e, self.project_id)}"
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
            error_msg = f"Failed to list tables: {safe_error_message(e, self.project_id)}"
            logger.error(f"[BigQueryTool] {error_msg}")
            
            return {
                "success": False,
                "tables": [],
                "error": error_msg,
            }


# Create a singleton instance wrapper for LangChain tool integration
def create_bigquery_tool(
    project_id: str,
    max_results: int = 10000,
    credentials_path: Optional[str] = None,
    max_bytes_billed: Optional[int] = None,
) -> BigQueryTool:
    """
    Factory function to create BigQuery tool instance.
    
    Args:
        project_id: GCP project ID
        max_results: Maximum rows to return
        credentials_path: Optional service account JSON key file
        max_bytes_billed: Optional per-query scan limit in bytes
    
    Returns:
        Configured BigQueryTool instance
    """
    return BigQueryTool(
        project_id=project_id,
        max_results=max_results,
        credentials_path=credentials_path,
        max_bytes_billed=max_bytes_billed,
    )
