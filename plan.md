# Text-to-SQL Agentic Data Analyst – Implementation Plan

**Project**: Enterprise Data Engineering + Generative AI Portfolio Application  
**Duration**: 6 Phases (estimated 40-60 hours)  
**Status**: Planning Phase ✅  
**Cost**: ~$5-15/month (OpenAI API only; GCP services free)

---

## 📋 Executive Summary

Build a **Text-to-SQL Agentic Data Analyst** that converts natural language questions into SQL queries, executes them against Google BigQuery, and renders dynamic visualizations. Users ask questions via a Next.js chat interface; a CrewAI pipeline orchestrates three specialized agents (SQL Developer, Data Executor, Data Visualizer) to deliver structured JSON responses that render as interactive Recharts.

**Key Value**: Demonstrates full-stack AI engineering, enterprise architecture, and cloud integration.

---

## 🏗️ Tech Stack & Justification

### **Frontend Layer**
| Technology | Version | Purpose | Why |
|---|---|---|---|
| Next.js | 16+ (App Router) | React framework | Enterprise standard, built-in SSR, API routes |
| TypeScript | Latest | Type safety | Catch errors at compile-time, better DX |
| Tailwind CSS | 3+ | Styling | Utility-first, rapid UI development, responsive by default |
| Recharts | 2.12+ | Data visualization | React-native, composable, excellent BigQuery data support |
| Axios | 1.6+ | HTTP client | Promise-based, request/response interceptors |
| Zustand | 4.4+ | State management | Lightweight, simple API, DevTools support |
| Lucide React | Latest | Icons | Modern, tree-shakeable, consistent design |
| Vercel AI SDK | 3.0+ | Streaming (optional) | Real-time response streaming, useChat hook |

### **Backend Layer**
| Technology | Version | Purpose | Why |
|---|---|---|---|
| Python | 3.11+ | Runtime | Industry standard for AI/ML, async support, rich ecosystem |
| FastAPI | 0.109+ | Web framework | Async-first, auto-generated OpenAPI docs, Pydantic integration |
| Uvicorn | 0.27+ | ASGI server | Production-grade, low overhead, easy deployment |
| Pydantic | 2.5+ | Data validation | Strong typing, JSON schema generation, decorator-based |
| CrewAI | 0.30+ | Agent orchestration | Multi-agent framework, built-in tool integration, task management |
| LangChain | 0.1.10+ | LLM framework | BigQuery tools, prompt management, chains |
| Google BigQuery | 7.14+ | Data warehouse | Serverless, scales infinitely, SQL dialect support |
| OpenAI SDK | 1.3+ | LLM access | GPT-4o (recommended) or GPT-3.5-turbo for cost control |
| python-dotenv | 1.0+ | Environment vars | Secure credential management |
| Tenacity | 8.2+ | Retry logic | Exponential backoff, circuit breaker patterns |

### **DevOps & Infrastructure**
| Technology | Version | Purpose | Why |
|---|---|---|---|
| Docker | 24+ | Containerization | Consistency across dev/prod, isolated environments |
| Docker Compose | 2.20+ | Orchestration | Multi-service local development, networking |
| Google Cloud Platform | - | Data warehouse | Free tier: 1TB/month BigQuery queries + 10GB storage |

### **Development Tools**
| Tool | Purpose |
|---|---|
| Git | Version control |
| GitHub | Repository hosting |
| VS Code | IDE with TypeScript + Python support |
| ESLint + Prettier | Frontend linting/formatting |
| Pytest | Python testing framework |
| Docker Desktop | Local containerization |

---

## 🎯 System Architecture

### **Data Flow**

```
┌─────────────────────────────────────────────────────────────────┐
│                     FRONTEND (Next.js)                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Chat Interface                                          │  │
│  │  - Message history                                       │  │
│  │  - User query input                                      │  │
│  │  - AI response (thought_process + chart)                │  │
│  └─────────────────────────┬──────────────────────────────┘  │
│                            │ HTTP POST /api/chat              │
│                            ↓                                   │
└─────────────────────────────────────────────────────────────────┘
                             │
        ┌────────────────────┴────────────────────┐
        │  Docker Compose Network (localhost)    │
        ↓                                         ↓
┌──────────────────────┐              ┌──────────────────────┐
│  BACKEND (FastAPI)   │              │  FRONTEND (Next.js)  │
│  Port: 8000          │              │  Port: 3000          │
└──────────┬───────────┘              └──────────────────────┘
           │
           ├─► CrewAI Pipeline
           │   ├─ Agent 1: SQL Developer
           │   ├─ Agent 2: Data Executor
           │   └─ Agent 3: Data Visualizer
           │
           ├─► LangChain BigQuery Tool
           │
           └─► OpenAI GPT-4o / GPT-3.5-turbo
                │
                └─► Google BigQuery
                    └─ bigquery-public-data.thelook_ecommerce
```

### **Agent Workflow**

```
User Query: "What were the top 5 product categories by revenue last month?"
    │
    ├─ TASK 1 (SQL Developer Agent)
    │  Input: User query + BigQuery schema
    │  Output: SELECT query for thelook_ecommerce dataset
    │  
    ├─ TASK 2 (Data Executor Agent)
    │  Input: SQL query
    │  Tool: BigQuery Tool (executes query)
    │  Output: Raw JSON data
    │  Error Handling: If SQL fails → escalate to Agent 1 for correction
    │
    ├─ TASK 3 (Data Visualizer Agent)
    │  Input: Raw data + user query
    │  Logic: Determine best chart type (Bar, Line, Pie, Table)
    │  Output: ChartData JSON (structured for Recharts)
    │
    └─ FastAPI Response (AgentResponse)
       {
         "thought_process": "...",
         "sql_query": "SELECT ...",
         "chart": {
           "chart_type": "bar",
           "data": [...],
           "x_axis_key": "category",
           "y_axis_key": "revenue",
           "title": "..."
         }
       }
           │
           └─► Frontend renders via ChartRenderer.tsx
```

---

## 💰 Cost Analysis (Recommended Setup)

### **Monthly Estimates** (Local Development)

| Component | Cost | Notes |
|---|---|---|
| **Google BigQuery** | $0 | 1 TB/month free; typical queries = 5-50 MB |
| **GCP Storage** | $0 | 10 GB/month free for backup/caching (optional) |
| **OpenAI API** | $5-15 | gpt-3.5-turbo @ ~$0.01/query × 5-15 queries/week |
| **Cloud Hosting** | $0 | Local Docker only; no cloud compute |
| **Total** | **$5-15/month** | ✅ Stays within free tier + minimal LLM costs |

### **Cost Control Strategies**

1. **Model Selection**: Use `gpt-3.5-turbo` instead of `gpt-4o`
   - gpt-3.5-turbo: $0.0005/$0.0015 per 1K tokens (input/output)
   - gpt-4o: $0.0030/$0.0060 per 1K tokens (6x more expensive)
   - Estimated savings: 85% on LLM costs

2. **OpenAI API Limits**: Set hard cap at $10/month
   - Dashboard: Account Settings → Billing → Usage Limits
   - Alert at $5, hard stop at $10

3. **BigQuery Query Optimization**
   - Use `LIMIT 1000` for initial exploration
   - Partition queries by date ranges
   - Avoid `SELECT *`; specify columns explicitly
   - Monitor via: `bq ls -j` for recent queries

4. **Caching & Deduplication**
   - LangChain prompt caching (same user queries)
   - 30-minute result cache for identical SQL queries

5. **Local-Only Development**
   - Run `docker-compose up` for all services locally
   - No Cloud Run, no serverless costs
   - Database: Public dataset (free to query)

---

## 📅 Implementation Phases

### **Phase 0: Environment Setup (2-3 hours)**

**Objectives:**
- Set up GCP project and credentials
- Install Docker & required tools
- Initialize Git repository with `.gitignore`
- Create project directory structure

**Deliverables:**
- `gcp-key.json` (service account) in project root (`.gitignored`)
- `docker-compose.yml` (ready to run)
- `.env.example` template
- Project folder structure

**Key Tasks:**
1. Create GCP service account with BigQuery Admin role
2. Download JSON key
3. Install Docker Desktop
4. Initialize Git repo: `git init`
5. Create folder structure:
   ```
   text-to-sql/
   ├── backend/
   ├── frontend/
   ├── docker-compose.yml
   ├── .env.example
   ├── .gitignore
   └── plan.md
   ```

**Success Criteria:**
- `gcloud` CLI authenticated (optional)
- Docker & Docker Compose installed
- Can run `docker ps` without errors

---

### **Phase 1: FastAPI Backend Setup (4-5 hours)**

**Objectives:**
- Initialize FastAPI project structure
- Set up Pydantic data models
- Implement CORS and health check endpoints
- Create environment configuration

**Deliverables:**
- `backend/main.py` (FastAPI app with CORS)
- `backend/requirements.txt` (all Python dependencies)
- `backend/config.py` (environment & settings)
- `backend/schemas/models.py` (Pydantic models)
- `backend/.dockerignore`
- `backend/Dockerfile`

**Key Tasks:**
1. Create Python virtual environment: `python -m venv venv`
2. Install dependencies (FastAPI, Uvicorn, Pydantic, etc.)
3. Generate `requirements.txt`: `pip freeze > requirements.txt`
4. Create `main.py` with:
   - FastAPI app instance
   - CORS middleware (allow `http://localhost:3000`)
   - `GET /health` endpoint
   - `POST /api/chat` endpoint (stub, returns 200)
   - Error handling middleware
   - Request logging
5. Create `config.py` with:
   - Pydantic Settings for environment variables
   - Validation for required vars (OPENAI_API_KEY, GOOGLE_APPLICATION_CREDENTIALS)
6. Create `schemas/models.py` with Pydantic models:
   - `ChatRequest` (user_query: str)
   - `ChartData` (chart_type, data, x_axis_key, y_axis_key, title)
   - `AgentResponse` (thought_process, sql_query, chart, execution_time_ms)
7. Create `Dockerfile` (multi-stage, minimal base image)
8. Test locally: `uvicorn main:app --reload`

**Success Criteria:**
- `curl http://localhost:8000/health` returns `{"status": "ok"}`
- `curl http://localhost:8000/docs` shows OpenAPI docs
- No hardcoded secrets
- All environment vars injected via `.env`

---

### **Phase 2: BigQuery Tool & Agents Setup (6-7 hours)**

**Objectives:**
- Create BigQuery tool for SQL execution
- Initialize CrewAI agents and tasks
- Implement error handling & retry logic
- Test agent pipeline end-to-end

**Deliverables:**
- `backend/tools/bigquery_tool.py` (BigQuery Tool)
- `backend/agents/data_crew.py` (Agent definitions & Crew)
- `backend/schemas/bigquery_schema.py` (Schema definitions)
- Integration tests

**Key Tasks:**
1. Create `tools/bigquery_tool.py`:
   - Custom LangChain tool class
   - `execute_query(sql: str) -> str | dict` function
   - BigQuery client initialization
   - Error handling:
     - Syntax errors → descriptive message
     - Auth failures → clear message
     - Timeouts (30s) → fallback behavior
     - Rate limits → retry with exponential backoff (Tenacity)
   - Query validation (prevent SELECT *)
   - Result formatting (JSON serialization)

2. Create `schemas/bigquery_schema.py`:
   - Hardcode schema for `order_items` table:
     - order_id, product_id, created_at, sale_price, status
   - Hardcode schema for `products` table:
     - id, name, category, retail_price
   - Add sample queries as documentation

3. Create `agents/data_crew.py`:
   - **Agent 1: SQL Developer**
     - Role: "BigQuery SQL Specialist"
     - Goal: "Write correct BigQuery Standard SQL queries"
     - Backstory: Expert in thelook_ecommerce dataset
     - Tools: None (reasoning only)
   
   - **Agent 2: Data Analyst**
     - Role: "Data Executor"
     - Goal: "Execute SQL queries and validate results"
     - Backstory: Experienced in data validation
     - Tools: BigQuery Tool
   
   - **Agent 3: Presenter**
     - Role: "Data Visualizer"
     - Goal: "Format results as ChartData JSON"
     - Backstory: Expert in data storytelling
     - Tools: None (formatting only)
   
   - **Tasks**:
     - Task 1 → Agent 1: Write SQL from user query
     - Task 2 → Agent 2: Execute SQL via BigQuery Tool
     - Task 3 → Agent 3: Format results as ChartData
   
   - **Crew**:
     - Sequential execution
     - Verbose logging enabled
     - Error handling: If Task 2 fails, escalate to Task 1

4. Create integration test:
   - Mock query: "What is the total revenue?"
   - Verify Agent 1 outputs valid SQL
   - Verify Agent 2 executes and returns data
   - Verify Agent 3 formats as ChartData JSON

**Success Criteria:**
- BigQuery Tool executes test query successfully
- CrewAI Crew completes all 3 tasks
- AgentResponse JSON is valid and complete
- Errors are caught and logged with context

---

### **Phase 3: FastAPI Endpoints & Integration (3-4 hours)**

**Objectives:**
- Implement `/api/chat` endpoint
- Wire CrewAI pipeline to FastAPI
- Add error handling and logging
- Test end-to-end backend flow

**Deliverables:**
- `backend/main.py` (updated with `/api/chat`)
- `backend/utils/logging.py` (structured logging)
- Integration tests

**Key Tasks:**
1. Update `main.py`:
   - Import Crew from `agents/data_crew.py`
   - Implement `POST /api/chat`:
     - Accept `ChatRequest` (user_query: str)
     - Validate input (non-empty, reasonable length)
     - Initialize Crew instance
     - Execute crew.kickoff(inputs={"user_query": user_query})
     - Parse CrewAI output → AgentResponse JSON
     - Handle errors (LLM failures, BigQuery errors, timeout)
     - Return AgentResponse (200) or error (400/500)
   - Add request logging with correlation IDs
   - Add response time metrics

2. Create `utils/logging.py`:
   - Structured logging (JSON format for Docker logs)
   - Request/response logging
   - Performance metrics (query execution time)

3. Test endpoint:
   ```bash
   curl -X POST http://localhost:8000/api/chat \
     -H "Content-Type: application/json" \
     -d '{"user_query": "What were the top 5 product categories by revenue?"}'
   ```

**Success Criteria:**
- Endpoint accepts requests and returns valid AgentResponse JSON
- All errors are caught and returned with status codes (400/500)
- Execution time is logged and included in response
- CORS works (can be called from http://localhost:3000)

---

### **Phase 4: Next.js Frontend Setup (4-5 hours)**

**Objectives:**
- Initialize Next.js App Router project
- Create chat interface UI layout
- Set up API client (Axios)
- Implement state management (Zustand)

**Deliverables:**
- `frontend/package.json` (dependencies)
- `frontend/src/app/page.tsx` (main chat page)
- `frontend/src/app/layout.tsx` (root layout)
- `frontend/src/lib/api.ts` (HTTP client)
- `frontend/src/lib/types.ts` (TypeScript types)
- `frontend/src/hooks/useChat.ts` (state management)
- Tailwind configuration

**Key Tasks:**
1. Initialize Next.js:
   ```bash
   npx create-next-app@latest frontend --typescript --tailwind
   cd frontend
   npm install lucide-react recharts axios zustand
   ```

2. Create `src/lib/types.ts`:
   - Export all Pydantic models (ChartData, AgentResponse, etc.)
   - Add frontend-specific types (UIMessage, ChatState)

3. Create `src/lib/api.ts`:
   - Axios instance with base URL (from NEXT_PUBLIC_API_URL env var)
   - `sendQuery(userQuery: string): Promise<AgentResponse>`
   - Error handling with user-friendly messages
   - Request/response interceptors

4. Create `src/hooks/useChat.ts` (Zustand store):
   - State: `messages: UIMessage[]`, `isLoading: bool`, `error: string | null`
   - Actions: `addMessage()`, `sendQuery()`, `clearHistory()`, `setError()`
   - Persist to localStorage (optional)

5. Create `src/app/page.tsx`:
   - Chat message history (scrollable container)
   - Message bubbles (user vs AI)
   - Input form with send button
   - Loading indicator
   - Error display
   - Responsive layout (Tailwind)

6. Create `src/components/MessageBubble.tsx`:
   - Render user and AI messages
   - Support markdown in AI responses
   - Show loading spinner for AI messages
   - Collapsible sections for thought_process and sql_query

7. Update `src/app/layout.tsx`:
   - Global styles
   - Fonts
   - Metadata

**Success Criteria:**
- Frontend runs: `npm run dev` → http://localhost:3000
- Chat UI loads with clean, modern design
- Input form is functional (no backend calls yet)
- Messages are stored in state
- Responsive on mobile/desktop (Tailwind)

---

### **Phase 5: ChartRenderer & Dynamic UI (5-6 hours)**

**Objectives:**
- Create ChartRenderer component with Recharts
- Implement chart type logic (Bar, Line, Pie, Table)
- Integrate with chat messages
- Add data export features

**Deliverables:**
- `frontend/src/components/ChartRenderer.tsx`
- `frontend/src/components/DataTable.tsx`
- `frontend/src/components/MessageBubble.tsx` (updated)
- `frontend/src/utils/chartUtils.ts` (chart type detection)

**Key Tasks:**
1. Create `src/utils/chartUtils.ts`:
   - `detectChartType(data: dict[], userQuery: string): "bar" | "line" | "pie" | "table"`
   - Logic:
     - If numeric data with categories → Bar
     - If time-series data → Line
     - If percentages/parts of whole → Pie
     - Otherwise → Table

2. Create `src/components/ChartRenderer.tsx`:
   - Accept `ChartData` prop
   - Switch statement based on chart_type:
     ```typescript
     case "bar":
       return <BarChart data={...} />
     case "line":
       return <LineChart data={...} />
     case "pie":
       return <PieChart data={...} />
     case "table":
       return <DataTable data={...} />
     ```
   - Recharts configuration:
     - Responsive container
     - Legend, tooltip
     - Formatted axis labels
     - Color palette consistency

3. Create `src/components/DataTable.tsx`:
   - Render data as HTML table
   - Sortable columns
   - Pagination for large datasets (>100 rows)
   - Export to CSV button

4. Update `src/components/MessageBubble.tsx`:
   - AI message structure:
     ```
     ┌─────────────────────────────────────┐
     │ Thought Process (collapsible)       │
     │ "The user asked for top 5..."       │
     ├─────────────────────────────────────┤
     │ SQL Query (collapsible)             │
     │ SELECT ... (with syntax highlight) │
     ├─────────────────────────────────────┤
     │ Chart / Data Table                  │
     └─────────────────────────────────────┘
     ```
   - Add "Copy SQL", "Export Data" buttons
   - Error messages with troubleshooting hints

5. Test with mock data:
   - Create sample AgentResponse JSON
   - Verify each chart type renders correctly
   - Test responsive behavior

**Success Criteria:**
- All 4 chart types render without errors
- Charts are interactive (hover, legend)
- Data export works
- Mobile layout is clean (no overflow)
- No console errors

---

### **Phase 6: Docker Integration & Production Hardening (4-5 hours)**

**Objectives:**
- Create Docker files for frontend and backend
- Set up Docker Compose orchestration
- Add health checks and logging
- Test full stack deployment locally
- Performance optimization

**Deliverables:**
- `backend/Dockerfile` (updated, optimized)
- `frontend/Dockerfile` (multi-stage build)
- `docker-compose.yml` (complete orchestration)
- `.dockerignore` files
- `.env.local` (example with all vars)
- Docker health check endpoints
- Logging configuration

**Key Tasks:**
1. Create `backend/Dockerfile`:
   - Base: `python:3.11-slim`
   - Install system dependencies (gcc for psycopg2, etc.)
   - COPY requirements, install deps (layer caching)
   - COPY source code
   - HEALTHCHECK endpoint
   - CMD: `uvicorn main:app --host 0.0.0.0 --port 8000`

2. Create `frontend/Dockerfile`:
   - Multi-stage build:
     - Stage 1: Builder (node:18-alpine, `npm ci`, `npm run build`)
     - Stage 2: Runtime (node:18-alpine, only production deps)
   - COPY .next, public folders
   - CMD: `npm start`

3. Create `docker-compose.yml`:
   - Backend service (port 8000)
     - Volume: gcp-key.json (read-only)
     - Environment: OPENAI_API_KEY, GOOGLE_APPLICATION_CREDENTIALS, etc.
     - Health check
     - Networks: app-network
   
   - Frontend service (port 3000)
     - Environment: NEXT_PUBLIC_API_URL=http://backend:8000
     - Depends on backend
     - Networks: app-network
   
   - Custom bridge network (app-network)
   - Volume definitions for dev hot-reload

4. Create `.env.local` template:
   ```
   # Backend
   OPENAI_API_KEY=sk-...
   GOOGLE_APPLICATION_CREDENTIALS=/secrets/gcp-key.json
   GCP_PROJECT_ID=your-project-id
   BACKEND_PORT=8000
   ENVIRONMENT=development

   # Frontend
   NEXT_PUBLIC_API_URL=http://backend:8000
   NEXT_PUBLIC_ENVIRONMENT=development

   # Paths (for docker-compose)
   GCP_KEY_PATH=./gcp-key.json
   ```

5. Add `.dockerignore` for both services:
   ```
   node_modules
   .git
   .next
   __pycache__
   *.pyc
   .pytest_cache
   .env
   gcp-key.json
   ```

6. Test Docker setup:
   ```bash
   docker-compose up --build
   # Visit http://localhost:3000 and http://localhost:8000/docs
   ```

7. Optimization:
   - Backend: Add connection pooling for BigQuery
   - Frontend: Enable Next.js caching headers
   - Both: Implement structured logging to stdout
   - Docker Compose: Add resource limits (memory, CPU)

**Success Criteria:**
- `docker-compose up --build` brings up both services
- Frontend connects to backend via internal network
- Both services log to stdout
- Health checks pass
- Can interact: send query from UI → see response from backend → chart renders
- All services stop cleanly with `Ctrl+C`

---

## 🧪 Testing Strategy

### **Backend Testing (Pytest)**
- Unit tests for BigQuery Tool
- Agent integration tests (mock LLM responses)
- FastAPI endpoint tests (with `httpx` test client)
- Error handling tests (invalid SQL, auth failures)

### **Frontend Testing (Jest + React Testing Library)**
- Component tests for ChartRenderer
- useChat hook tests
- API client tests (with mocked axios)

### **End-to-End Testing (Optional, Playwright)**
- User flow: Input query → View chart
- Error scenarios: Network failure, invalid response

### **Manual Testing**
- Send sample queries via Postman/curl
- Verify chart renders correctly
- Test error paths (bad SQL, timeout)

---

## ✅ Success Criteria (Project Completion)

### **Functional Requirements**
- ✅ User types question in Next.js chat UI
- ✅ Question is sent to FastAPI backend via HTTP
- ✅ CrewAI pipeline executes all 3 agents
- ✅ SQL query is generated, executed, and validated
- ✅ Results are formatted as ChartData JSON
- ✅ Response returned to frontend
- ✅ Chart renders dynamically based on data type
- ✅ SQL query is visible and collapsible
- ✅ Thought process is visible and collapsible

### **Non-Functional Requirements**
- ✅ All code is type-safe (TypeScript + Python type hints)
- ✅ Error handling for LLM hallucinations and BigQuery failures
- ✅ Production-ready code quality (logging, validation, CORS)
- ✅ Docker Compose runs entire stack locally
- ✅ Cost stays under $5-15/month
- ✅ No hardcoded secrets
- ✅ Responsive UI (mobile/desktop)
- ✅ All dependencies documented in requirements.txt/package.json

---

## 🚀 Development Workflow

### **Local Development Loop**
```bash
# 1. Start Docker Compose (all services)
docker-compose up --build

# 2. Frontend auto-reloads on file changes (next dev inside container)
# 3. Backend auto-reloads with uvicorn --reload

# 4. Send test query via http://localhost:3000

# 5. View logs:
docker-compose logs -f backend
docker-compose logs -f frontend

# 6. Stop all services
docker-compose down
```

### **Git Workflow**
```bash
# After Phase 0
git add .
git commit -m "Phase 0: Project structure and Docker setup"

# After each phase
git add .
git commit -m "Phase X: [Phase Name]"

# All commits include Co-authored-by trailer
```

### **Code Style**
- **Python**: Black formatter, isort for imports, Pylint/Flake8
- **TypeScript**: ESLint, Prettier
- **No hardcoded secrets**: Always use environment variables

---

## 📚 Reference Architecture Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                        INTERNET                                │
│                     (OpenAI API, GCP APIs)                     │
└────────────────────────────────────────────────────────────────┘
                              ▲
                              │
                    ┌─────────┴─────────┐
                    │                   │
        ┌───────────▼────────┐ ┌────────▼──────────┐
        │   FastAPI Backend  │ │  Next.js Frontend │
        │   Port: 8000       │ │  Port: 3000       │
        │   Python 3.11      │ │  Node.js 18+      │
        │   - CrewAI Agents  │ │  - Chat UI        │
        │   - BigQuery Tool  │ │  - ChartRenderer  │
        │   - FastAPI routes │ │  - Zustand store  │
        └───────────┬────────┘ └────────┬──────────┘
                    │                   │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │  Docker Compose   │
                    │  (app-network)    │
                    │  Port Mapping:    │
                    │  8000 → Backend   │
                    │  3000 → Frontend  │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │  GCP Service Acct │
                    │  (gcp-key.json)   │
                    │  - BigQuery Conn  │
                    │  - Auth Token     │
                    └───────────────────┘
```

---

## 📝 Notes & Considerations

### **Performance**
- BigQuery queries typically <2s for public dataset
- LLM inference: 3-5s per agent (sequential)
- Total end-to-end: 10-15s per query
- Frontend: Use skeleton loaders during API calls

### **Scalability**
- Local Docker: 1-2 queries/sec capacity
- For production scaling: Deploy backend to Cloud Run, frontend to Vercel
- Add result caching (Redis) for duplicate queries
- Implement token counting to avoid OpenAI overages

### **Security**
- Never commit `gcp-key.json` or `.env`
- Use `.gitignore` to exclude sensitive files
- Environment variables injected at runtime
- BigQuery service account: read-only BigQuery role

### **Error Scenarios**
- Network timeout → Show "Connection error, please try again"
- Invalid SQL → Agent 1 correction loop
- BigQuery quota exceeded → "Query too large, please refine..."
- LLM rate limit → Retry with exponential backoff
- Malformed response → Fallback to raw data table

### **Optional Enhancements** (Post-MVP)
- Chat history persistence (PostgreSQL)
- Multi-language support
- Advanced query caching
- Real-time streaming with WebSockets
- Mobile app (React Native)
- Analytics dashboard (user queries, performance metrics)

---

## 📞 Questions or Issues?

Refer to phase-specific success criteria above. If stuck:
1. Check Docker logs: `docker-compose logs -f [service]`
2. Validate environment variables: `cat .env.local`
3. Test endpoints manually: `curl http://localhost:8000/health`
4. Review Pydantic schema errors in console

---

**Status**: ✅ Plan Complete – Ready for Phase 1 Implementation

