"""
CrewAI multi-agent Text-to-SQL pipeline (PIPELINE_MODE=crew).

A CrewAI Flow orchestrates three agents plus deterministic code steps:

    plan ──► write_sql ──► check_sql ──► execute ──► analyze
     │          ▲              │            │
     │          └──── retry ───┴────────────┘   (error fed back; bounded)
     └──► not answerable

- Planner agent: interprets the question against the schema and decides
  whether and how it can be answered (tables, filters, grouping, chart).
- SQL developer agent: writes GoogleSQL from the plan; when a check fails it
  gets the exact BigQuery error back and fixes its own query.
- check_sql / execute (code, not agents): the read-only guard, a free
  BigQuery dry run, then execution with the byte cap and result conversion
  shared with the simple pipeline (agents/common.py).
- Analyst agent: reads the actual result rows and writes the answer,
  insights and follow-up questions.

Every agent returns a Pydantic model (structured output), so nothing is
scraped out of free text. Agents never delegate to each other: the Flow
decides what runs next, which keeps cost and latency bounded.
"""

import os

# CrewAI sends anonymous usage telemetry by default; opt out unless the
# operator configured otherwise. Must be set before crewai is imported.
os.environ.setdefault("CREWAI_DISABLE_TELEMETRY", "true")
os.environ.setdefault("CREWAI_TRACING_ENABLED", "false")

import asyncio
import datetime
import json
import logging
import re
import time
from typing import Any, Literal

from crewai import LLM, Agent
from crewai.events.event_listener import event_listener as _crewai_event_listener
from crewai.flow.flow import Flow, listen, or_, router, start
from pydantic import BaseModel, Field

from config import settings
from tools import create_bigquery_tool
from agents.common import (
    MAX_DISPLAY_ROWS,
    RELATIONSHIPS,
    SQL_RULES,
    extract_sql,
    format_chart_data,
    schemas_text,
    summarize,
    validate_read_only_sql,
)
from agents.simplified_pipeline import describe_llm_error
from schemas.models import ChartData

logger = logging.getLogger(__name__)

# CrewAI's global console listener prints Rich panels for every agent run
# regardless of Agent(verbose=...); only show them when debugging.
_crewai_event_listener.formatter.verbose = settings.debug


# Times the SQL developer is sent back after its query fails a check
MAX_SQL_FIX_ATTEMPTS = 2

# Result rows shown to the analyst agent (keeps the prompt small)
ANALYST_SAMPLE_ROWS = 50
ANALYST_SAMPLE_CHARS = 8000

# Overall time budget; the frontend gives up after 120 s
FLOW_TIMEOUT_SECONDS = 110


# ============================================================================
# Structured agent outputs
# ============================================================================


class QueryPlan(BaseModel):
    """Planner agent output."""

    answerable: bool = Field(
        description="False only if these tables clearly cannot answer the question"
    )
    reason: str = Field(
        default="",
        description="If not answerable: a short explanation for the user",
    )
    alternative_questions: list[str] = Field(
        default_factory=list,
        description="If not answerable: 2-3 related questions the data can answer",
    )
    tables: list[str] = Field(default_factory=list, description="Tables the query needs")
    approach: str = Field(
        default="",
        description=(
            "Precise query recipe: joins, filters (with exact date logic), grouping, "
            "measures with aliases, ordering and row limit. Note any interpretation "
            "made for a vague question."
        ),
    )
    chart: Literal["bar", "line", "pie", "table"] = Field(
        default="table",
        description=(
            "bar: compare categories (<=30 rows); line: trend over time; "
            "pie: share of a whole (<=8 slices); table: detailed rows"
        ),
    )


class SQLDraft(BaseModel):
    """SQL developer agent output."""

    sql: str = Field(description="The final, validated BigQuery SQL query")
    notes: str = Field(default="", description="One sentence on how the query works")


class Analysis(BaseModel):
    """Analyst agent output."""

    summary: str = Field(
        description="Direct answer to the question in 1-3 sentences with concrete numbers"
    )
    insights: list[str] = Field(
        default_factory=list,
        description="2-4 short findings that are visible in the result rows",
    )
    follow_up_questions: list[str] = Field(
        default_factory=list,
        description="3 short follow-up questions answerable from the same tables",
    )


# ============================================================================
# Flow
# ============================================================================


class CrewState(BaseModel):
    """State carried through one run of the flow."""

    question: str = ""
    plan: QueryPlan | None = None
    sql: str = ""
    sql_attempts: int = 0
    last_error: str = ""
    result: dict[str, Any] | None = None
    analysis: Analysis | None = None
    outcome: Literal["pending", "answered", "unanswerable", "failed"] = "pending"
    timings: dict[str, float] = Field(default_factory=dict)


def _structured(output: Any, model: type[BaseModel]) -> Any:
    """Return an agent's structured output, parsing its raw text as a fallback."""
    if isinstance(getattr(output, "pydantic", None), model):
        return output.pydantic
    raw = getattr(output, "raw", "") or ""
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError(f"{model.__name__}: agent returned no structured output")
    return model.model_validate_json(match.group(0))


class TextToSQLFlow(Flow[CrewState]):
    """Orchestrates the agents for a single question."""

    # CrewAI's console event output is noisy (and its emoji crash some
    # Windows consoles); the pipeline does its own logging.
    suppress_flow_events = True

    def __init__(self, pipeline: "CrewTextToSQLPipeline", **kwargs: Any):
        super().__init__(**kwargs)
        self._pipeline = pipeline

    @start()
    async def plan(self):
        prompt = f"""Question: {self.state.question}

Today's date: {datetime.date.today().isoformat()}

Available tables:
{self._pipeline.schemas}

{RELATIONSHIPS}

Decide whether one SQL query over these tables can answer the question. Mark it
unanswerable only when the data clearly lacks what is needed; for a vague
question, pick a sensible interpretation and state it in the approach. Then
describe the approach precisely and choose the chart that best fits the result.
Don't add filters the question doesn't ask for (e.g. on order status): revenue
and order counts include every status unless the question says otherwise."""
        step_start = time.time()
        output = await self._pipeline.planner().kickoff_async(prompt, response_format=QueryPlan)
        self.state.plan = _structured(output, QueryPlan)
        self.state.timings["plan"] = time.time() - step_start
        logger.info(
            f"[Crew] Plan: answerable={self.state.plan.answerable} "
            f"tables={self.state.plan.tables} chart={self.state.plan.chart}"
        )

    # Router labels must differ from handler names: CrewAI rejects a listener
    # that would be triggered by its own name.

    @router(plan)
    def route_plan(self):
        return "plan_ready" if self.state.plan.answerable else "not_answerable"

    @listen(or_("plan_ready", "retry"))
    async def write_sql(self):
        self.state.sql_attempts += 1
        plan = self.state.plan
        previous = ""
        if self.state.last_error:
            previous = f"""
Your previous query failed. Fix it so it runs.
Previous SQL:
{self.state.sql}
Error:
{self.state.last_error[:1500]}
"""
        prompt = f"""Question: {self.state.question}

Today's date: {datetime.date.today().isoformat()}

Plan from the planner:
- Tables: {', '.join(plan.tables) or 'choose as needed'}
- Approach: {plan.approach}

Available tables:
{self._pipeline.schemas}

{RELATIONSHIPS}
{previous}
{SQL_RULES}

Answer with the final query."""
        step_start = time.time()
        output = await self._pipeline.sql_developer().kickoff_async(prompt, response_format=SQLDraft)
        self.state.sql = extract_sql(_structured(output, SQLDraft).sql)
        self.state.timings[f"sql_{self.state.sql_attempts}"] = time.time() - step_start
        logger.info(f"[Crew] SQL (attempt {self.state.sql_attempts}): {self.state.sql[:100]}...")

    def _retry_or_fail(self, error: str) -> str:
        self.state.last_error = error
        if self.state.sql_attempts <= MAX_SQL_FIX_ATTEMPTS:
            logger.info(f"[Crew] SQL check failed, sending it back: {error[:120]}")
            return "retry"
        return "execution_failed"

    @router(write_sql)
    async def check_sql(self):
        guard_error = validate_read_only_sql(self.state.sql)
        if guard_error:
            return self._retry_or_fail(f"Rejected generated SQL: {guard_error}")
        # Free dry run: catches unknown columns, type errors and syntax errors
        # without running (or paying for) the query
        dry_run = await asyncio.to_thread(self._pipeline.bq_tool.dry_run, self.state.sql)
        if not dry_run["success"]:
            return self._retry_or_fail(dry_run["error"])
        return "sql_valid"

    @router("sql_valid")
    async def execute(self):
        result = await asyncio.to_thread(
            self._pipeline.bq_tool.execute,
            self.state.sql,
            timeout_seconds=settings.bq_query_timeout_seconds,
        )
        if result["success"]:
            self.state.result = result
            self.state.last_error = ""
            logger.info(f"[Crew] Query executed. Rows: {result['row_count']}")
            return "results_ready"

        if result["error"].startswith("SQL Error"):
            return self._retry_or_fail(result["error"])
        self.state.last_error = result["error"]
        return "execution_failed"

    @listen("results_ready")
    async def analyze(self):
        result = self.state.result
        sample = json.dumps(result["data"][:ANALYST_SAMPLE_ROWS], default=str)
        if len(sample) > ANALYST_SAMPLE_CHARS:
            sample = sample[:ANALYST_SAMPLE_CHARS] + " ...(truncated)"
        total_rows = result.get("total_rows") or result["row_count"]
        prompt = f"""Question: {self.state.question}

SQL that was run:
{self.state.sql}

Rows returned: {result['row_count']} (total matching: {total_rows})
Columns: {', '.join(result['schema'])}
Result rows (JSON, first {ANALYST_SAMPLE_ROWS} at most):
{sample}

Tables available for follow-up questions:
{self._pipeline.schemas}

Answer the question from these rows only; never invent numbers that are not in
them. Follow-up questions must be answerable from the tables above. Format money with $ and thousands separators and round sensibly. If no
rows came back, say that nothing matched and suggest how to broaden the question."""
        step_start = time.time()
        try:
            output = await self._pipeline.analyst().kickoff_async(prompt, response_format=Analysis)
            self.state.analysis = _structured(output, Analysis)
            self.state.timings["analyze"] = time.time() - step_start
        except Exception as e:
            # The query already succeeded; fall back to the plain summary
            # rather than failing the whole request.
            logger.warning(f"[Crew] Analyst failed, using plain summary: {type(e).__name__}: {e}")
        self.state.outcome = "answered"

    @listen("not_answerable")
    def unanswerable(self):
        self.state.outcome = "unanswerable"

    @listen("execution_failed")
    def failed(self):
        self.state.outcome = "failed"


# ============================================================================
# Pipeline
# ============================================================================


def _apply_preferred_chart(chart: ChartData, preferred: str) -> ChartData:
    """
    Honor the planner's chart choice where the data supports it.

    format_chart_data picks a chart from the data's shape; the planner knows
    the intent (e.g. "share of" -> pie), so it may refine that choice.
    """
    if preferred == "table" and chart.chart_type != "table":
        return chart.model_copy(update={"chart_type": "table", "data": chart.data[:MAX_DISPLAY_ROWS]})
    if preferred == "pie" and chart.chart_type == "bar" and len(chart.data) <= 8:
        values = [row.get(chart.y_axis_key) for row in chart.data]
        if all(isinstance(v, (int, float)) and v >= 0 for v in values):
            return chart.model_copy(update={"chart_type": "pie"})
    return chart


class CrewTextToSQLPipeline:
    """
    Multi-agent Text-to-SQL pipeline built on a CrewAI Flow.

    Exposes the same execute_async contract as SimplifiedTextToSQLPipeline,
    plus insights and follow-up questions from the analyst agent.
    """

    def __init__(self, project_id: str):
        """
        Initialize the pipeline.

        Args:
            project_id: GCP project ID for BigQuery access
        """
        self.project_id = project_id
        self.bq_tool = create_bigquery_tool(
            project_id,
            max_results=settings.bq_max_results_rows,
            credentials_path=settings.resolved_credentials_path(),
            max_bytes_billed=settings.bq_max_bytes_billed,
        )
        self.schemas = schemas_text()
        logger.info(f"[CrewPipeline] Initialized for project: {project_id}")

    # Agents are cheap to construct and hold per-run state, so each request
    # gets fresh instances instead of sharing them across concurrent requests.

    def _llm(self, temperature: float) -> LLM:
        return LLM(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=temperature,
            max_tokens=settings.openai_max_tokens,
            timeout=60,
        )

    def planner(self) -> Agent:
        return Agent(
            role="Analytics Planner",
            goal="Turn a business question into a precise, answerable query plan",
            backstory=(
                "You are a senior analytics engineer who knows the thelook_ecommerce "
                "dataset well. You translate loosely worded business questions into "
                "exact definitions: which tables, which filters, which measures."
            ),
            llm=self._llm(temperature=0),
            allow_delegation=False,
            max_iter=2,
            max_execution_time=60,
            verbose=settings.debug,
        )

    def sql_developer(self) -> Agent:
        return Agent(
            role="BigQuery SQL Developer",
            goal="Write a correct, efficient GoogleSQL query that implements the plan",
            backstory=(
                "You are an expert in BigQuery's GoogleSQL dialect, including its "
                "date and timestamp functions. You write simple, readable queries "
                "and fix errors precisely when told what failed."
            ),
            llm=self._llm(temperature=0),
            allow_delegation=False,
            max_iter=2,
            max_execution_time=60,
            verbose=settings.debug,
        )

    def analyst(self) -> Agent:
        return Agent(
            role="Data Analyst",
            goal="Explain what query results mean for the question that was asked",
            backstory=(
                "You are a data analyst who writes crisp, accurate findings for "
                "business stakeholders, always grounded in the numbers at hand."
            ),
            llm=self._llm(temperature=0.3),
            allow_delegation=False,
            max_iter=2,
            max_execution_time=60,
            verbose=settings.debug,
        )

    async def execute_async(self, user_query: str) -> dict[str, Any]:
        """
        Run the multi-agent flow for one question.

        Args:
            user_query: Natural language question

        Returns:
            dict with success status, SQL query, chart data, insights and
            follow-up questions (same shape as the simplified pipeline)
        """
        start_time = time.time()
        flow = TextToSQLFlow(self)
        logger.info(f"[Crew] Processing query: {user_query[:100]}...")

        try:
            await asyncio.wait_for(
                flow.kickoff_async(inputs={"question": user_query}),
                timeout=FLOW_TIMEOUT_SECONDS,
            )
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": f"Multi-agent pipeline timeout after {FLOW_TIMEOUT_SECONDS} seconds",
                "sql_query": flow.state.sql,
                "execution_time_ms": (time.time() - start_time) * 1000,
            }
        except Exception as e:
            error_msg = f"Pipeline error: {describe_llm_error(e)}"
            logger.error(f"[Crew] {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "sql_query": flow.state.sql,
                "execution_time_ms": (time.time() - start_time) * 1000,
            }

        state = flow.state
        execution_time = (time.time() - start_time) * 1000
        logger.info(
            f"[Crew] Finished ({state.outcome}) in {execution_time / 1000:.1f}s; steps: "
            + ", ".join(f"{name}={secs:.1f}s" for name, secs in state.timings.items())
        )

        if state.outcome == "unanswerable":
            return {
                "success": True,
                "thought_process": state.plan.reason
                or "This question can't be answered from the available tables.",
                "sql_query": "",
                "chart": ChartData(
                    chart_type="table", data=[], x_axis_key="value",
                    y_axis_key="count", title="Not answerable",
                ),
                "follow_up_questions": state.plan.alternative_questions,
                "execution_time_ms": execution_time,
            }

        if state.outcome != "answered":
            return {
                "success": False,
                "error": state.last_error or "Multi-agent pipeline did not produce a result",
                "sql_query": state.sql,
                "execution_time_ms": execution_time,
            }

        chart = format_chart_data(state.result["data"], state.result["schema"])
        chart = _apply_preferred_chart(chart, state.plan.chart)
        analysis = state.analysis

        return {
            "success": True,
            "thought_process": analysis.summary
            if analysis
            else summarize(user_query, state.result, chart, corrected=state.sql_attempts > 1),
            "sql_query": state.sql,
            "chart": chart,
            "insights": analysis.insights if analysis else [],
            "follow_up_questions": analysis.follow_up_questions if analysis else [],
            "execution_time_ms": execution_time,
        }


def create_crew_pipeline(project_id: str) -> CrewTextToSQLPipeline:
    """
    Factory function to create the multi-agent pipeline.

    Args:
        project_id: GCP project ID

    Returns:
        Initialized CrewTextToSQLPipeline instance
    """
    return CrewTextToSQLPipeline(project_id=project_id)
