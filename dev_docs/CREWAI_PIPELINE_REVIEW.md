# Review: Original CrewAI Pipeline

The first multi-agent pipeline (`backend/agents/data_crew.py` as of commit `12ace89`)
was never used by the API, and it could not have worked reliably if it had been.
This note lists its main flaws and how the rebuilt pipeline addresses them.

## Main flaws

1. **Never wired in, but still slowed startup.** `main.py` only used the simplified
   pipeline. `agents/__init__.py` still imported the crew eagerly, so loading CrewAI
   took about 9 of the backend's 13 seconds of startup.

2. **Tools couldn't be called as intended.** `@tool` was applied to instance methods
   (`def execute_bigquery(self, sql_query)`). The decorator wraps the plain function
   when the class is defined, so `self` is treated as a tool argument and the
   BigQuery client is never bound. Reproduced with CrewAI 1.15: the tool's argument
   schema is `self, sql_query`, and calling it with only `sql_query` fails validation
   (`self: Field required`).

3. **Agents handed results to each other as free text.** Tasks had no structured
   outputs. The executor and visualizer had to find the SQL and the data again in the
   previous agent's prose.

4. **Results were scraped out of the final text.**
   - SQL came from the first line containing `SELECT` up to a `;`. Prose such as
     "I will SELECT…" matched, and without a semicolon the rest of the output came too.
   - When nothing matched, it returned a canned
     `SELECT * FROM products LIMIT 5`, so the UI could show SQL that never ran.
   - The chart came from `json.loads` of everything between the first `{` and the
     last `}`. Any parse failure silently became an empty table.
   - `thought_process` was simply the first 500 characters of the final output.

5. **Charts were built from LLM-retyped data.** The execution tool returned only 10
   rows to the agents, and the visualizer had to re-emit the data as JSON. Charts were
   therefore capped at 10 points and open to transcription errors or invented numbers.

6. **No safety checks on generated SQL.** Whatever the agent wrote went straight to
   BigQuery. There was no read-only check, no byte cap, and no timeout around the
   crew. The README's suggested "BigQuery Admin" role made this worse; see the
   recommendation below.

7. **Cost and latency had no limit.**
   - `allow_delegation=True` let the executor bounce work back to the SQL developer.
   - `memory=True` added embedding calls (and storage) on every run.
   - With `max_iter` of 3/5/3, one question could take many LLM calls; `max_rpm=10`
     then throttled them.

8. **Not safe under concurrent requests.** One `Crew` and its agents were created at
   startup and reused for every request. The BigQuery call inside the tool was
   blocking.

9. **Weak prompts.** Requirement lines were joined without newlines
   (`"Requirements:- Use…- Include…"`), so they ran together. Only 2 of the 4 tables
   were described, and that schema listed columns that don't exist. The SQL developer
   ran at temperature 0.7.

10. **Telemetry on by default.** CrewAI's anonymous telemetry was never disabled.

## What replaced it

The current `backend/agents/data_crew.py` is a CrewAI **Flow**: fixed steps that call
agents, instead of agents delegating freely.

| Flaw | Now |
|---|---|
| Free-text hand-offs and scraping (3, 4) | Every agent returns a Pydantic model (`QueryPlan`, `SQLDraft`, `Analysis`) |
| LLM-retyped chart data (5) | Charts are built in code from the real result rows (`agents/common.py`) |
| No safety checks (6) | Shared read-only guard, free BigQuery dry run, 10 GB byte cap, 110 s flow timeout |
| Broken tools (2) | Validation is a code step; dry-run and execution errors go back to the SQL developer, with at most 2 fixes |
| Unbounded cost (7) | No delegation and no memory; 3 LLM calls per question, plus 1 per fix |
| Shared state, blocking calls (8) | Fresh agents per request; BigQuery runs in worker threads |
| Weak prompts (9) | Verified schema for all 4 tables, shared SQL rules, temperature 0 for SQL |
| Slow startup (1) | CrewAI loads only when the crew pipeline is first used, or at startup with `PIPELINE_MODE=crew` |
| Telemetry (10) | Disabled unless explicitly enabled |

The simplified pipeline remains the default (`PIPELINE_MODE=simple`). The UI's
"Multi-agent analysis" toggle switches pipelines per request.

## Recommendation

Give the service account **BigQuery Job User** + **BigQuery Data Viewer** instead of
BigQuery Admin. The SQL guard is the first line of defense; least privilege should
be the second.
