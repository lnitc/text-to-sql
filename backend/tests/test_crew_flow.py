"""
Tests for the CrewAI multi-agent flow with fake agents and a fake BigQuery
tool: they exercise the real Flow routing (plan, SQL checks, retries,
analysis) without calling OpenAI or BigQuery.
"""

import asyncio
from types import SimpleNamespace

import pytest

from agents.data_crew import (
    MAX_SQL_FIX_ATTEMPTS,
    Analysis,
    CrewTextToSQLPipeline,
    QueryPlan,
    SQLDraft,
    _apply_preferred_chart,
    _structured,
)
from agents.common import format_chart_data

ROWS = [{"category": "Jeans", "revenue": 120.0}, {"category": "Tops", "revenue": 80.0}]


# ============================================================================
# Fakes
# ============================================================================


class FakeAgent:
    """Returns the given structured outputs in order and records each prompt."""

    def __init__(self, *outputs):
        self.outputs = list(outputs)
        self.prompts = []

    async def kickoff_async(self, prompt, response_format=None):
        self.prompts.append(prompt)
        output = self.outputs.pop(0)
        if isinstance(output, Exception):
            raise output
        return SimpleNamespace(pydantic=output, raw="")


class FakeBigQuery:
    def __init__(self, dry_runs=(), executions=()):
        self.dry_runs = list(dry_runs)
        self.executions = list(executions)
        self.executed = []

    def dry_run(self, sql):
        return self.dry_runs.pop(0) if self.dry_runs else {"success": True, "bytes_processed": 1, "error": None}

    def execute(self, sql, timeout_seconds=60):
        self.executed.append(sql)
        return self.executions.pop(0)


def ok_execution(rows=ROWS):
    return {
        "success": True, "data": rows, "row_count": len(rows), "total_rows": len(rows),
        "schema": list(rows[0]) if rows else [], "error": None,
    }


def make_pipeline(planner, sql_developer, analyst, bq):
    # Bypass __init__, which would create a real BigQuery client
    pipeline = CrewTextToSQLPipeline.__new__(CrewTextToSQLPipeline)
    pipeline.bq_tool = bq
    pipeline.schemas = "<schemas>"
    pipeline.planner = lambda: planner
    pipeline.sql_developer = lambda: sql_developer
    pipeline.analyst = lambda: analyst
    return pipeline


def run(pipeline, question="Revenue by category?"):
    return asyncio.run(pipeline.execute_async(question))


PLAN = QueryPlan(answerable=True, tables=["order_items", "products"], approach="Sum sale_price by category", chart="bar")
SQL = SQLDraft(sql="```sql\nSELECT p.category, SUM(oi.sale_price) AS revenue FROM t GROUP BY 1;\n```")
ANALYSIS = Analysis(summary="Jeans lead with $120.", insights=["Jeans are 60% of revenue."], follow_up_questions=["And last year?"])


# ============================================================================
# Flow outcomes
# ============================================================================


def test_answered_question_returns_chart_and_analysis():
    bq = FakeBigQuery(executions=[ok_execution()])
    result = run(make_pipeline(FakeAgent(PLAN), FakeAgent(SQL), FakeAgent(ANALYSIS), bq))

    assert result["success"] is True
    assert result["sql_query"] == "SELECT p.category, SUM(oi.sale_price) AS revenue FROM t GROUP BY 1"
    assert result["chart"].chart_type == "bar"
    assert result["thought_process"] == "Jeans lead with $120."
    assert result["insights"] == ["Jeans are 60% of revenue."]
    assert result["follow_up_questions"] == ["And last year?"]


def test_failed_dry_run_is_sent_back_to_the_sql_developer():
    fixed = SQLDraft(sql="SELECT p.category, SUM(oi.sale_price) AS revenue FROM t GROUP BY 1")
    sql_developer = FakeAgent(SQL, fixed)
    bq = FakeBigQuery(
        dry_runs=[{"success": False, "bytes_processed": 0, "error": "SQL Error: Unrecognized name: products"}],
        executions=[ok_execution()],
    )
    result = run(make_pipeline(FakeAgent(PLAN), sql_developer, FakeAgent(ANALYSIS), bq))

    assert result["success"] is True
    assert len(sql_developer.prompts) == 2
    assert "Unrecognized name: products" in sql_developer.prompts[1]
    assert len(bq.executed) == 1  # only the fixed query ran


def test_unanswerable_question_returns_alternatives_without_sql():
    plan = QueryPlan(answerable=False, reason="No weather data.", alternative_questions=["Orders by city?"])
    sql_developer = FakeAgent()
    bq = FakeBigQuery()
    result = run(make_pipeline(FakeAgent(plan), sql_developer, FakeAgent(), bq), "Weather tomorrow?")

    assert result["success"] is True
    assert result["sql_query"] == ""
    assert result["thought_process"] == "No weather data."
    assert result["follow_up_questions"] == ["Orders by city?"]
    assert sql_developer.prompts == [] and bq.executed == []


def test_write_queries_are_never_executed():
    attempts = MAX_SQL_FIX_ATTEMPTS + 1
    sql_developer = FakeAgent(*[SQLDraft(sql="DELETE FROM users WHERE TRUE")] * attempts)
    bq = FakeBigQuery()
    result = run(make_pipeline(FakeAgent(PLAN), sql_developer, FakeAgent(), bq))

    assert result["success"] is False
    assert "Rejected generated SQL" in result["error"]
    assert len(sql_developer.prompts) == attempts
    assert bq.executed == []


def test_analyst_failure_falls_back_to_the_plain_summary():
    bq = FakeBigQuery(executions=[ok_execution()])
    result = run(make_pipeline(FakeAgent(PLAN), FakeAgent(SQL), FakeAgent(RuntimeError("LLM down")), bq))

    assert result["success"] is True
    assert result["thought_process"].startswith("Question: Revenue by category?")
    assert result["insights"] == []


def test_llm_errors_fail_the_request_cleanly():
    result = run(make_pipeline(FakeAgent(RuntimeError("401 Unauthorized")), FakeAgent(), FakeAgent(), FakeBigQuery()))
    assert result["success"] is False
    assert "authentication failed" in result["error"]


# ============================================================================
# Helpers
# ============================================================================


@pytest.mark.parametrize(
    "preferred, expected",
    [("pie", "pie"), ("table", "table"), ("line", "bar"), ("bar", "bar")],
)
def test_planner_chart_preference(preferred, expected):
    chart = format_chart_data(ROWS, ["category", "revenue"])
    assert _apply_preferred_chart(chart, preferred).chart_type == expected


def test_pie_needs_few_non_negative_slices():
    rows = [{"c": "a", "n": -1}, {"c": "b", "n": 2}]
    assert _apply_preferred_chart(format_chart_data(rows, ["c", "n"]), "pie").chart_type == "bar"


def test_structured_output_falls_back_to_parsing_raw_json():
    output = SimpleNamespace(pydantic=None, raw='Here you go: {"sql": "SELECT 1"} thanks')
    assert _structured(output, SQLDraft).sql == "SELECT 1"
