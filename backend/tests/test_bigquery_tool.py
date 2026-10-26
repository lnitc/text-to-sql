"""Tests for BigQueryTool with a fake BigQuery client (no network)."""

import datetime
import decimal

import pytest
from google.api_core.exceptions import BadRequest, Forbidden

from tools.bigquery_tool import BigQueryTool, _to_json_value, safe_error_message

PROJECT = "test-project-123"


# ============================================================================
# Fakes
# ============================================================================


class FakeField:
    def __init__(self, name):
        self.name = name


class FakeRowIterator:
    """Mimics google.cloud.bigquery RowIterator: iterable rows plus schema/total_rows."""

    def __init__(self, columns, rows, total_rows=None):
        self.schema = [FakeField(c) for c in columns]
        self._rows = rows
        self.total_rows = len(rows) if total_rows is None else total_rows

    def __iter__(self):
        return iter(self._rows)


class FakeJob:
    def __init__(self, iterator=None, error=None, total_bytes_processed=0):
        self._iterator = iterator
        self._error = error
        self.total_bytes_processed = total_bytes_processed

    def result(self, timeout=None, max_results=None):
        if self._error:
            raise self._error
        self.max_results = max_results
        return self._iterator


class FakeClient:
    def __init__(self, job=None, error=None):
        self.job = job
        self.error = error
        self.job_configs = []

    def query(self, query, job_config=None):
        self.job_configs.append(job_config)
        if self.error:
            raise self.error
        return self.job


def make_tool(client, max_results=1000, max_bytes_billed=10 * 1024**3):
    # Bypass __init__, which would create a real BigQuery client
    tool = BigQueryTool.__new__(BigQueryTool)
    tool.project_id = PROJECT
    tool.max_results = max_results
    tool.max_bytes_billed = max_bytes_billed
    tool.client = client
    tool._schema_cache = {}
    return tool


def leaky_bad_request():
    """A BadRequest shaped like the real ones: the URL embeds the project ID."""
    return BadRequest(
        f"POST https://bigquery.googleapis.com/bigquery/v2/projects/{PROJECT}/jobs?prettyPrint=false: "
        "Unrecognized name: nope at [1:8]\n\nLocation: US\nJob ID: 1234-abcd",
        errors=[{"message": "Unrecognized name: nope at [1:8]", "reason": "invalidQuery"}],
    )


# ============================================================================
# Value conversion
# ============================================================================


@pytest.mark.parametrize(
    "value, expected",
    [
        (decimal.Decimal("12.50"), 12.5),
        (datetime.datetime(2024, 1, 2, 3, 4, 5, tzinfo=datetime.timezone.utc), "2024-01-02T03:04:05+00:00"),
        (datetime.date(2024, 1, 2), "2024-01-02"),
        (b"\x00\x01", "AAE="),
        ({"a": decimal.Decimal("1")}, {"a": 1.0}),
        ([datetime.date(2024, 1, 2)], ["2024-01-02"]),
        ("text", "text"),
        (None, None),
    ],
)
def test_values_are_converted_to_json_friendly_types(value, expected):
    assert _to_json_value(value) == expected


# ============================================================================
# Error sanitizing
# ============================================================================


def test_structured_error_message_is_used():
    assert safe_error_message(leaky_bad_request(), PROJECT) == "Unrecognized name: nope at [1:8]"


def test_unstructured_error_is_scrubbed():
    error = Forbidden(
        f"POST https://bigquery.googleapis.com/bigquery/v2/projects/{PROJECT}/jobs: "
        f"Access Denied: Project {PROJECT}: User does not have bigquery.jobs.create permission. "
        f"Caller: my-sa@{PROJECT}.iam.gserviceaccount.com\n\nJob ID: abc-123"
    )
    message = safe_error_message(error, PROJECT)
    assert PROJECT not in message
    assert "gserviceaccount" not in message
    assert "https://" not in message
    assert "Job ID" not in message
    assert "Access Denied" in message


# ============================================================================
# execute / dry_run
# ============================================================================


def test_execute_converts_rows_and_applies_the_byte_cap():
    iterator = FakeRowIterator(
        ["category", "revenue", "first_sale"],
        [("Jeans", decimal.Decimal("10.5"), datetime.date(2024, 1, 2))],
    )
    client = FakeClient(job=FakeJob(iterator))
    result = make_tool(client, max_bytes_billed=12345).execute("SELECT 1")

    assert result["success"] is True
    assert result["schema"] == ["category", "revenue", "first_sale"]
    assert result["data"] == [{"category": "Jeans", "revenue": 10.5, "first_sale": "2024-01-02"}]
    assert client.job_configs[0].maximum_bytes_billed == 12345


def test_execute_reports_truncated_results():
    iterator = FakeRowIterator(["id"], [(1,), (2,)], total_rows=100000)
    result = make_tool(FakeClient(job=FakeJob(iterator)), max_results=2).execute("SELECT id FROM t")
    assert (result["row_count"], result["total_rows"]) == (2, 100000)


def test_execute_sql_error_is_sanitized():
    result = make_tool(FakeClient(job=FakeJob(error=leaky_bad_request()))).execute("SELECT nope")
    assert result["success"] is False
    assert result["error"] == "SQL Error: Unrecognized name: nope at [1:8]"


def test_execute_rejects_empty_query():
    result = make_tool(FakeClient()).execute("   ")
    assert result == {
        "success": False, "data": [], "row_count": 0, "schema": [],
        "error": "Query cannot be empty", "execution_time_ms": 0,
    }


def test_dry_run_reports_bytes():
    client = FakeClient(job=FakeJob(total_bytes_processed=2048))
    result = make_tool(client).dry_run("SELECT 1")
    assert result == {"success": True, "bytes_processed": 2048, "error": None}
    assert client.job_configs[0].dry_run is True


def test_dry_run_enforces_the_byte_cap():
    client = FakeClient(job=FakeJob(total_bytes_processed=5000))
    result = make_tool(client, max_bytes_billed=1000).dry_run("SELECT 1")
    assert result["success"] is False
    assert "over the 1,000 byte limit" in result["error"]


def test_dry_run_sql_error_is_sanitized():
    result = make_tool(FakeClient(error=leaky_bad_request())).dry_run("SELECT nope")
    assert result["error"] == "SQL Error: Unrecognized name: nope at [1:8]"
