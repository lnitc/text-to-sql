"""Tests for the SQL guard, SQL extraction and chart selection shared by both pipelines."""

import pytest

from agents.common import (
    MAX_DISPLAY_ROWS,
    extract_sql,
    format_chart_data,
    summarize,
    validate_read_only_sql,
)


# ============================================================================
# extract_sql
# ============================================================================


@pytest.mark.parametrize(
    "llm_output, expected",
    [
        ("SELECT 1", "SELECT 1"),
        ("SELECT 1;", "SELECT 1"),
        ("```sql\nSELECT 1;\n```", "SELECT 1"),
        ("```\nSELECT 1\n```", "SELECT 1"),
        ("Here is the query:\n```sql\nWITH a AS (SELECT 1) SELECT * FROM a\n```\nDone.",
         "WITH a AS (SELECT 1) SELECT * FROM a"),
        ("Sure! SELECT x FROM t;", "SELECT x FROM t"),
    ],
)
def test_extract_sql(llm_output, expected):
    assert extract_sql(llm_output) == expected


# ============================================================================
# validate_read_only_sql
# ============================================================================


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT 1",
        "select * from t",
        "WITH a AS (SELECT 1) SELECT * FROM a",
        # Keywords and semicolons inside strings, identifiers and comments are fine
        "SELECT 'a;b' AS s FROM t WHERE status = 'Deleted'",
        "SELECT `drop;table` FROM t",
        "SELECT 1 -- ; DROP TABLE t",
        "SELECT 1 /* ; DELETE */",
    ],
)
def test_read_only_sql_is_allowed(sql):
    assert validate_read_only_sql(sql) is None


@pytest.mark.parametrize(
    "sql",
    [
        "",
        "DELETE FROM t WHERE 1=1",
        "INSERT INTO t SELECT 1",
        "UPDATE t SET x = 1",
        "DROP TABLE t",
        "CREATE TABLE x AS SELECT 1",
        "MERGE t USING s ON TRUE WHEN MATCHED THEN DELETE",
        "EXECUTE IMMEDIATE 'DROP TABLE t'",
        "DECLARE x INT64; SELECT x",
        "SELECT 1; DROP TABLE t",
        "-- comment first\nDROP TABLE t",
    ],
)
def test_write_or_multi_statement_sql_is_rejected(sql):
    assert validate_read_only_sql(sql)


# ============================================================================
# format_chart_data
# ============================================================================


def test_category_and_measure_make_a_bar_chart():
    rows = [{"category": "Jeans", "revenue": 10.5}, {"category": "Tops", "revenue": 3}]
    chart = format_chart_data(rows, ["category", "revenue"])
    assert (chart.chart_type, chart.x_axis_key, chart.y_axis_key) == ("bar", "category", "revenue")


def test_date_and_measure_make_a_line_chart():
    rows = [{"month": "2024-01-01", "n": 5}, {"month": "2024-02-01", "n": 7}]
    chart = format_chart_data(rows, ["month", "n"])
    assert (chart.chart_type, chart.x_axis_key, chart.y_axis_key) == ("line", "month", "n")


def test_timestamps_count_as_dates():
    rows = [{"day": "2024-01-01T00:00:00+00:00", "n": 1}, {"day": "2024-01-02T00:00:00+00:00", "n": 2}]
    assert format_chart_data(rows, ["day", "n"]).chart_type == "line"


def test_two_numeric_columns_make_a_line_chart():
    rows = [{"year": 2023, "revenue": 1.0}, {"year": 2024, "revenue": 2.0}]
    assert format_chart_data(rows, ["year", "revenue"]).chart_type == "line"


def test_nulls_are_ignored_when_classifying_columns():
    rows = [{"c": "a", "n": None}, {"c": "b", "n": 2}]
    assert format_chart_data(rows, ["c", "n"]).chart_type == "bar"


@pytest.mark.parametrize(
    "rows, schema",
    [
        ([{"n": 5310}], ["n"]),  # single value
        ([{"a": "x", "b": 1, "c": 2, "d": 3}], ["a", "b", "c", "d"]),  # too many columns
        ([{"flag": True, "n": 1}, {"flag": False, "n": 2}], ["flag", "n"]),  # bool isn't a number
        ([{"c": f"x{i}", "n": i} for i in range(31)], ["c", "n"]),  # too many bars
    ],
)
def test_shapes_that_dont_chart_well_become_tables(rows, schema):
    assert format_chart_data(rows, schema).chart_type == "table"


def test_tables_are_capped_for_display():
    rows = [{"c": f"x{i}", "n": i} for i in range(MAX_DISPLAY_ROWS + 50)]
    chart = format_chart_data(rows, ["c", "n"])
    assert chart.chart_type == "table"
    assert len(chart.data) == MAX_DISPLAY_ROWS


def test_no_rows_gives_an_empty_table():
    chart = format_chart_data([], ["a", "b"])
    assert (chart.chart_type, chart.data, chart.x_axis_key) == ("table", [], "a")


# ============================================================================
# summarize
# ============================================================================


def test_summary_mentions_truncation_and_correction():
    rows = [{"c": f"x{i}", "n": i} for i in range(1000)]
    result = {"row_count": 1000, "total_rows": 5000, "data": rows, "schema": ["c", "n"]}
    chart = format_chart_data(rows, ["c", "n"])
    text = summarize("How many?", result, chart, corrected=True)
    assert "automatically corrected" in text
    assert "first 1,000 of 5,000 rows" in text
    assert f"Showing the first {MAX_DISPLAY_ROWS} rows" in text
