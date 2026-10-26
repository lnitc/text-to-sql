# Development Story

How the Text-to-SQL Data Analyst was built, from the first plan to the current
codebase. It condenses the ~55 session reports that used to live in
`dev_docs/` and the git history (54 commits, October 20–26, 2026) into one
narrative, followed by the lessons worth keeping.

The project was built with AI coding assistants: Phases 0–5 with GitHub
Copilot (15 commits carry its co-author trailer), and the review, rebuild and
hardening from October 25 onward with Claude Code. That workflow explains the
old documentation style, which had a separate report for nearly every session.

---

## Timeline at a glance

| Date | Stage | Key commits |
|---|---|---|
| Oct 20 | Plan and project scaffolding (Phase 0) | `0f5e6e6`, `edacb4a` |
| Oct 21 | FastAPI backend (Phase 1), BigQuery tool and pipeline (Phase 2), Next.js frontend (Phase 3), first advanced features (Phase 4.1) | `286e5ba` – `c3891c9` |
| Oct 22 | More frontend components (Phase 4.2) | `2061e98` |
| Oct 23–24 | Manual testing and bug fixing (Phase 4.2) | `97b1fe2` – `2809ea8` |
| Oct 24 | Docker deployment (Phase 5) | `85185e0` – `e27c225` |
| Oct 25 | First README; full code review and debugging; multi-agent pipeline rebuilt | `12ace89`, `23175b2`, `8c8bd94` |
| Oct 26 | Repo hygiene, UI polish, security review, tests, Docker rework, documentation | `878f61f` – `13dbc08` and later |

---

## 1. The plan (October 20)

`plan.md` set out to build a portfolio piece showing "full-stack AI
engineering": a chat UI where questions in English become BigQuery SQL and
then charts. The planned stack is essentially what shipped: Next.js with
TypeScript, Tailwind, Recharts, Zustand and Axios on the front; FastAPI,
Pydantic and Uvicorn on the back; BigQuery's public `thelook_ecommerce`
dataset; Docker Compose to tie it together. The estimated cost was $5–15 a
month, almost all OpenAI.

The centerpiece was to be a **CrewAI crew of three agents**: a *SQL Developer*
writing the query, a *Data Executor* running it and recovering from errors,
and a *Data Visualizer* choosing the chart and explaining the result. The plan
had six phases of 40–60 hours in total. In practice the work was reorganized
into Phases 0–5 below and took about a week.

## 2. Phase 0: scaffolding (October 20)

The repository got its folder layout, `docker-compose.yml`, Dockerfiles for both
services, `.env.example` and a `.gitignore` protecting `.env`, `.env.local` and
`gcp-key.json`. A quick-start guide listed the manual steps no tool can do for
you: create a GCP project and service account, download its key, get an OpenAI
API key.

## 3. Phase 1: the FastAPI backend (October 21)

`main.py`, `config.py` (pydantic-settings) and `schemas/models.py` defined the
API: `GET /health`, `POST /api/chat`, request validation (questions of 1–1,000
characters), CORS for the frontend, a common error format, and OpenAPI docs.

## 4. Phase 2: BigQuery tool and the pipeline decision (October 21)

`tools/bigquery_tool.py` wrapped query execution with timeouts, row limits and
error handling, and `schemas/bigquery_schema.py` hardcoded the four tables'
columns for the prompt.

The key decision of the project happened here. The CrewAI crew was written
(`agents/data_crew.py`), but the API was wired to a **simplified LangChain
pipeline** instead: one LLM call writes the SQL, the tool runs it, code picks
a chart. The report gave four reasons: reliability, speed, debuggability and
fewer moving parts. The crew was left "for future enhancement", to be enabled
by swapping one call.

*Postscript:* the October 25 review found the crew could not have worked as
written (its tools were broken and its results were scraped from free text),
and that the hardcoded schema listed columns that don't exist. See sections 9
and 10.

## 5. Phase 3: the Next.js frontend (October 21)

A Next.js 16 App Router project with a chat interface (`ChatInterface.tsx`,
`ChatMessage.tsx`), a `ChartRenderer` for bar, line, pie and table results, a
Zustand store for messages, and an Axios client.

## 6. Phase 4: features (October 21–22)

**Phase 4.1** added CSV/JSON export and clipboard copy, conversation persistence
in `localStorage`, dark mode, and keyboard shortcuts. **Phase 4.2** added the
sidebar panels: Favorites (with tags and search), History, an Analytics
dashboard, and a Query Builder for adding parameters to a question.

## 7. Phase 4.2 testing: the first round of bugs (October 23–24)

Manual testing surfaced a run of bugs, each fixed in its own commit:

| Bug | Root cause | Fix |
|---|---|---|
| Dark mode only switched the sidebar | `dark:` classes didn't follow the toggle | Replaced them with explicit `isDark` conditionals in the chat interface |
| "Error [object Object]" on every question | Frontend sent `query` instead of `user_query`, and read `detail` instead of `message` | Aligned the request and error formats |
| `RowIterator has no attribute 'field_names'` | Wrong BigQuery client API | Read column names from `results.schema` |
| Queries returning 0 rows failed | A Pydantic validator rejected empty chart data | Removed the validator |
| React hydration error | A `<button>` nested inside another `<button>` | Restructured the SQL panel header |
| "Processing…" message never disappeared | Race in removing the placeholder | Removed it by a unique ID |
| Favorites never saved (three attempts) | Missing `userQuery` field, then hook-local state not shared between components, then a store-batching race when adding and starring in two steps | Moved saved queries into the Zustand store and created favorites in one step |
| Every question failed | `gpt-3.5-turbo` had been retired | Switched to `gpt-4o-mini` and categorized OpenAI errors |

Errors became user-friendly: the frontend's `errorHandler.ts` turns backend
errors into a title, explanation and suggestions per type (SQL, model,
authentication, rate limit, network). The Query Builder was hidden from the UI
as unfinished. The status report declared the app "production ready for
portfolio demonstration".

*Postscript:* the dark-mode fix treated the symptom. The real cause, found on
October 25, was that **Tailwind CSS 4 bases `dark:` on the operating-system
setting by default**, not on a class, so every remaining `dark:` class in the
app was still ignoring the toggle.

## 8. Phase 5: Docker (October 24)

Getting both containers to build and run took about fifteen fix commits in an
hour:

- **npm:** the deprecated `--no-optional` flag broke the frontend build; it was
  replaced with `--omit=optional`. `package-lock.json` was excluded by
  `.dockerignore`, so `npm ci` couldn't work.
- **Python imports:** the code imported `backend.config` and friends, but
  inside the container the backend folder *is* the root. After several
  attempts (PYTHONPATH, `python -m`, inline `sys.path`), all imports dropped the
  `backend.` prefix and a small `run.py` wrapper started Uvicorn.
- **Tailwind styles missing:** the frontend loaded without any styling. A
  `tailwind.config.ts` was added and the CSS pipeline reworked, but the build
  then failed on Turbopack's native CSS module (`lightningcss`) inside Docker.
  The workaround: **build the frontend on the host** and copy the `.next`
  folder into the image.
- **Credentials:** the key mount `${GCP_KEY_PATH:-.}/gcp-key.json` misbehaved on
  Windows when the variable was empty; it was replaced with a direct
  `./gcp-key.json` mount, and the backend read the key from
  `/secrets/gcp-key.json`.

Meanwhile the documentation, which had grown to dozens of session reports, was
gathered into `dev_docs/` (`b849023`, `e27c225`).

*Postscript:* the `lightningcss` failure was caused by the npm fix itself.
Next.js, Tailwind and lightningcss ship their Linux binaries as *optional*
dependencies, so `--omit=optional` skipped exactly the files the build needed.
This was found and fixed on October 26 (section 13).

## 9. A first README and a full review (October 25)

A tentative README and a GitHub publication checklist were written
(`12ace89`). The next request was to debug the app and improve it where
necessary, which turned into a file-by-file review plus live tests against
OpenAI and BigQuery (`23175b2`). It found that much of what the reports called
complete didn't actually work:

**Backend**
- The schema given to the model listed columns that don't exist
  (`products.distribution_centers`, `users.birth_date`, `users.updated_at`) and
  status values that never occur (`Pending`, `Delivered`), and only described
  2 of the 4 tables. It was rebuilt from the live table metadata.
- Running the backend locally (as the README said) crashed: `.env.local` was
  looked up relative to the working directory.
- `/openapi.json`, and with it the `/docs` page, crashed with infinite
  recursion.
- Validation errors (422) came back in a shape the frontend couldn't read.
- BigQuery calls blocked the server's event loop; NUMERIC and date values
  weren't converted, breaking charts.
- Importing the unused CrewAI module took 9 of the 13 seconds of startup.

**Safety and quality, added:** the read-only SQL guard, a per-query byte cap,
automatic correction (BigQuery's error is sent back to the model), and prompt
rules for BigQuery's date functions. In live tests, *"last month"* questions
failed (even after an automatic retry) before these rules and succeeded on the
first try after.

**Frontend**
- The Tailwind 4 dark-mode root cause (section 7) was fixed with one CSS rule.
- History was never recorded; clearing the chat came back after a reload; a
  "Processing…" placeholder could persist forever.
- The Analytics panel's "average response time" was `Math.random()`, and its
  keyword chart searched English questions for SQL keywords.
- Ctrl+Enter and Escape did nothing; a chart component broke React's rules of
  hooks; the backend status was checked only once on page load.
- The configuration told the browser to call `http://backend:8000`, an address
  that only exists inside the Docker network. It only worked because the
  Docker image reused a bundle built on the host with a different value.

The Query Builder was un-hidden, and its output changed from URL-style
`question?limit=5` text, which went straight to the LLM, to plain language.

## 10. Rebuilding the multi-agent pipeline (October 25)

The original crew had never run. A review
([`CREWAI_PIPELINE_REVIEW.md`](CREWAI_PIPELINE_REVIEW.md)) lists why: its tools
were decorated instance methods that couldn't be called, agents passed results
to each other as free text, and the SQL and chart were scraped out of the final
message with a fake fallback query. It also had no safety checks and no limit
on cost or latency.

It was rebuilt as a **CrewAI Flow** (`8c8bd94`): fixed steps that call agents,
with no free delegation. A planner, a SQL developer and an analyst agent each
return Pydantic models. Validation and execution are plain code shared with
the simple pipeline (`agents/common.py`). A `PIPELINE_MODE` setting and a UI
toggle switch between the two pipelines per question.

Testing shaped the final design:
- The first version gave the SQL agent a `validate_sql` tool. It fired 8–11
  validations at once, took up to 73 seconds, and once answered with an invalid
  query anyway. Validation moved into the Flow: the agent writes once, code
  runs a free BigQuery dry run, and any error goes back to the agent.
- CrewAI's console output crashed on a Windows console with a Japanese code
  page (emoji in log panels), so its console events are suppressed.
- CrewAI rejects a router label that matches a handler name (`"analyze"` →
  `analyze()`), so the labels were renamed.

The result answers in 13–18 seconds with written findings and follow-up
questions, and declines unanswerable questions in about 4 seconds. On one test
("brands with the highest return rate among those with 100+ items") it beat the
simple pipeline, which returned zero rows.

## 11. Repository hygiene (October 26)

A duplicate virtualenv at the repo root was deleted (`backend/venv` is the
documented one). The root `.gitignore` had been ignoring `.dockerignore`
files, so `backend/.dockerignore` was never committed and a fresh clone would
have copied a local virtualenv into the image (`878f61f`).

## 12. UI polish (October 26)

- Copy buttons in History and Favorites got click feedback: a press, a green
  "Copied!" with a check mark, or "Failed" if the clipboard is blocked
  (`53bc806`).
- Bar charts silently dropped category labels: Recharts hides x-axis labels
  that would overlap. Charts with many or long labels now use horizontal bars.
  This was verified by rendering old and new charts in headless Chrome with
  real data (7 of 10 labels before, 10 of 10 after) (`2a6e8ac`).
- In Analytics, the success rate overflowed its card, and the "SQL Features
  Used" pie clipped its labels. It became a sorted bar chart, which is also
  more honest: one query can use several features, so the counts aren't
  shares of a whole (`29697d5`).

## 13. Security review, tests and Docker rework (October 26)

A review before publishing (`44f0eef`, `13dbc08`) found:

- **No secrets in git history.** The service account key and `.env` were never
  committed. The GCP project ID appeared in one doc and one old commit; the
  author chose to replace the GCP project rather than rewrite history.
- **A runtime leak:** BigQuery error messages embed the request URL, which
  contains the project ID, and permission errors include the service account
  email. These were shown to users and sent to the LLM. Errors are now reduced
  to their human-readable reason, and the API redacts identifiers from every
  error as a last line of defense.
- **Dependencies:** about ten unused packages were removed (including the heavy
  `crewai-tools`), the rest pinned to tested versions, and test tools moved to
  `requirements-dev.txt`. A clean install proved the list complete.
- **Unused settings** (caching, monthly budget, dataset names, temperature)
  were removed, and Compose was found never passing `OPENAI_MODEL` or
  `BQ_MAX_BYTES_BILLED` to the container.
- **Tests:** a 76-test pytest suite now covers the SQL guard, chart selection,
  BigQuery conversion and error cleaning, the API, and the multi-agent flow's
  routing, using fakes for OpenAI and BigQuery.
- **Frontend Dockerfile:** with the real cause of the Phase 5 failure found
  (section 8), the image now builds itself with a normal `npm ci`, runs Next.js'
  standalone server as an unprivileged user on Node 24, and shrank from 2.64 GB
  to 414 MB. The backend image went from 2.17 GB to 1.8 GB.

## 14. Documentation (October 26)

The README gained deployment guidance (sign-in and rate limiting are required
before sharing the app), Compose ports were bound to `127.0.0.1`, the MIT
statement became a "reuse at your own risk" notice, and the unused
`GCP_KEY_PATH` variable was removed everywhere. Finally the README was
rewritten to match the code, and `dev_docs/` was condensed into this story.

---

## Lessons learned

For developers and AI agents continuing this project:

1. **Verify claims by running the real thing.** Several reports declared
   features complete or "production ready" while `/docs` crashed, the crew had
   never run, and the schema had wrong columns. A live end-to-end question (and
   now `pytest`) is the only status report worth trusting.
2. **Check the schema against the data.** Wrong column names in a text-to-SQL
   prompt don't fail loudly; they produce SQL that fails or answers a different
   question. `bigquery_schema.py` is verified against live table metadata;
   keep it that way.
3. **Find the root cause before working around it.** Two workarounds hid real
   causes for days: explicit `isDark` conditionals for Tailwind 4's dark
   variant, and pre-building on the host for a skipped optional dependency.
4. **Keep safety in code, not in agents.** The read-only guard, dry run, byte
   cap and error cleaning are deterministic and shared by both pipelines.
   Agents write and explain; they don't decide what's safe to run.
5. **Bound agent workflows.** A Flow with fixed steps and structured outputs is
   predictable in cost and latency; free delegation and tool loops were not.
6. **Error messages are an output channel.** Anything in them can reach users,
   logs and the LLM; scrub identifiers at the source.
7. **`NEXT_PUBLIC_*` values are fixed at build time** and are used by the
   *browser*, so they must be browser-reachable URLs.
8. **Windows quirks seen here:** CRLF line endings, a non-UTF-8 console code
   page breaking tools that print emoji, and Docker turning a missing bind-mount
   file into a directory or `mkdir` error.
9. **One living document beats fifty session reports.** Keep this story and the
   README current instead of adding a new report per session.

---

## Where the old documents went

The session and phase reports previously in `dev_docs/` (phase completion
reports, test guides, bug-fix write-ups, Docker guides, the original
`plan.md`, and README drafts) were condensed into this document and removed.
They remain in git history; to read one, find the last commit that had it:

```bash
git log --oneline -- dev_docs/PHASE_4_2_STATUS_REPORT.md
git show <commit>^:dev_docs/PHASE_4_2_STATUS_REPORT.md
```

Still in this folder: this story, and
[`CREWAI_PIPELINE_REVIEW.md`](CREWAI_PIPELINE_REVIEW.md), the analysis of why
the original multi-agent pipeline was rebuilt.
