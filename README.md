# 🚀 Text-to-SQL Agentic Data Analyst

> **Status**: 🧪 **PROOF OF CONCEPT** - Active Development
> 
> This is a working prototype demonstrating enterprise-grade AI/ML and data engineering practices. **Testing is ongoing and some features are simplified for cost optimization.** The Query Builder feature is currently in testing and will be fully integrated in a future release.

## 📋 Overview

**Text-to-SQL Agentic Data Analyst** is a full-stack generative AI application that transforms natural language questions into SQL queries, executes them against Google BigQuery, analyzes the results, and renders dynamic data visualizations. The application demonstrates production-grade data engineering, AI orchestration, and cloud architecture patterns.

### What It Does
1. **User asks a question in natural language** (e.g., "What were the top 3 product categories by revenue last month?")
2. **AI agents generate and execute SQL** against BigQuery using CrewAI orchestration
3. **Results are analyzed and formatted** into structured JSON responses
4. **Frontend renders interactive visualizations** (charts, tables) using Recharts
5. **Chat history and favorites** are persisted for the session

### Example Flow
```
User: "How many orders were placed in the last 7 days?"
                    ↓
          [CrewAI SQL Agent]
                    ↓
          SQL: SELECT COUNT(DISTINCT order_id)...
                    ↓
          [BigQuery Execution]
                    ↓
          Result: 5,310 orders
                    ↓
          [Visualization Agent]
                    ↓
          Response: {"chart_type": "table", "data": [...]}
                    ↓
    [Next.js Frontend Renders Chart]
```

---

## 🏗️ Architecture

### System Design

```
┌─────────────────────────────────────────────────────────────┐
│                    Client (Browser)                         │
│                   http://localhost:3000                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Next.js 16 Frontend (React + TypeScript)              │ │
│  │  ├─ Chat Interface (message history)                   │ │
│  │  ├─ Query Input Form                                   │ │
│  │  ├─ Chart Renderer (Recharts)                          │ │
│  │  ├─ Favorites Panel (localStorage)                     │ │
│  │  └─ Dark Mode Toggle                                   │ │
│  └────────────────────────────────────────────────────────┘ │
└────────────────┬────────────────────────────────────────────┘
                 │ HTTP/CORS
                 │ JSON Request/Response
                 ↓
┌────────────────────────────────────────────────────────────┐
│                 Backend (Docker)                           │
│              http://localhost:8000                          │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  FastAPI Application (Python 3.11)                   │ │
│  │  ├─ REST API Endpoints                               │ │
│  │  ├─ Request Validation (Pydantic)                    │ │
│  │  ├─ CORS Configuration                               │ │
│  │  └─ Error Handling                                   │ │
│  └────────────────┬─────────────────────────────────────┘ │
│                   │                                        │
│  ┌────────────────▼─────────────────────────────────────┐ │
│  │  CrewAI Agentic Pipeline                             │ │
│  │  ├─ Agent 1: SQL Developer                           │ │
│  │  │   └─ Generates BigQuery SQL queries               │ │
│  │  ├─ Agent 2: Data Executor                           │ │
│  │  │   └─ Executes SQL and handles errors              │ │
│  │  └─ Agent 3: Presenter                               │ │
│  │      └─ Formats results and chooses visualization    │ │
│  └────────────────┬─────────────────────────────────────┘ │
│                   │                                        │
│  ┌────────────────▼─────────────────────────────────────┐ │
│  │  BigQuery Tool & Integration                         │ │
│  │  ├─ SQL Execution                                    │ │
│  │  ├─ Error Handling & Recovery                        │ │
│  │  └─ Result Formatting                                │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────┬─────────────────────────────────────────┘
                   │ BigQuery API
                   │ (Google Cloud)
                   ↓
      ┌────────────────────────────┐
      │    Google BigQuery         │
      │  (Public eCommerce Data)   │
      │  - order_items             │
      │  - products                │
      │  - users                   │
      │  - events                  │
      └────────────────────────────┘
```

### Technology Stack

**Frontend**
- **Framework**: Next.js 16 (App Router, Turbopack)
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4
- **Visualization**: Recharts (Bar, Line, Pie, Table charts)
- **State Management**: React Hooks + localStorage
- **HTTP Client**: Axios

**Backend**
- **Framework**: FastAPI (Python 3.11)
- **AI Orchestration**: CrewAI (multi-agent system)
- **LLM**: OpenAI GPT-4o (can be switched to GPT-4-turbo for cost optimization)
- **Database**: Google BigQuery (with langchain-google-community)
- **Data Validation**: Pydantic
- **Server**: Uvicorn

**Infrastructure**
- **Containerization**: Docker & Docker Compose
- **Cloud Platform**: Google Cloud Platform (GCP)
- **Service Account**: GCP Service Account with BigQuery permissions
- **Database**: BigQuery (bigquery-public-data.thelook_ecommerce)

**Development**
- **Package Managers**: npm (frontend), pip (backend)
- **Version Control**: Git
- **API Documentation**: FastAPI Swagger UI

---

## ✨ Features

### Current Features (Phase 4.2)

| Feature | Status | Notes |
|---------|--------|-------|
| **Chat Interface** | ✅ Complete | Natural language query input with streaming responses |
| **SQL Generation** | ✅ Complete | AI-powered SQL query generation for BigQuery |
| **Query Execution** | ✅ Complete | Direct BigQuery integration with error handling |
| **Visualizations** | ✅ Complete | Dynamic charts (Bar, Line, Pie, Table) using Recharts |
| **Query History** | ✅ Complete | Session-based history maintained in UI |
| **Favorites** | ✅ Complete | Save/unsave queries to favorites (localStorage) |
| **SQL Display** | ✅ Complete | Collapsible SQL query panel with copy functionality |
| **Dark Mode** | 🙈 Hidden | Implemented but temporarily hidden from UI |
| **Error Display** | ✅ Partial | Basic error messages shown; graceful handling in progress |

### Upcoming Features (Phase 5+)

- **Query Builder**: Visual query construction interface (currently in testing)
- **Query Result Export**: Export to CSV, JSON, Parquet
- **Advanced Caching**: Query result caching to reduce API calls
- **Rate Limiting**: Protect against excessive API usage
- **Authentication**: User accounts and access control
- **Cost Tracking**: Real-time API cost monitoring and budgeting
- **Query Analytics**: Usage patterns and performance metrics
- **Mobile Responsive**: Optimize for mobile devices
- **Advanced Error Recovery**: Automatic query retry and optimization

---

## 📋 Prerequisites

### System Requirements
- **OS**: Windows, macOS, or Linux
- **RAM**: 4GB minimum (8GB recommended)
- **Disk Space**: 5GB minimum for Docker images

### Required Software
- **Docker Desktop** (v20.10+) - [Install here](https://www.docker.com/products/docker-desktop)
- **Git** - [Install here](https://git-scm.com/downloads)
- **Node.js** (v18+) - Only needed for local frontend development
- **Python** (v3.11+) - Only needed for local backend development

### Required Accounts & Keys
- **Google Cloud Platform (GCP)**
  - Active GCP Project
  - Service Account with BigQuery permissions
  - Service account JSON key file

- **OpenAI**
  - API key with GPT-4o access (or equivalent model)
  - Sufficient API quota and credits

### Cost Considerations (Important ⚠️)

This POC uses **shared public data** to minimize BigQuery costs:
- Uses `bigquery-public-data.thelook_ecommerce` (free public dataset)
- No data ingestion costs
- Query costs: ~$0.01-$0.10 per query (typical)

**Estimated Monthly Cost (Portfolio Use)**:
- BigQuery: $2-5 (low query volume)
- OpenAI API: $5-10 (GPT-4o, ~200 queries/month)
- **Total**: ~$7-15/month

**Cost Optimization Strategies Used in This POC**:
- Using public dataset (no ingestion costs)
- Query result caching (not yet fully implemented)
- Limiting results to 1000 rows per query
- Temperature/token limits for LLM calls
- Using more affordable models (can switch to GPT-4-turbo)

---

## 🚀 Quick Start

### Option 1: Using Docker (Recommended)

**1. Clone the Repository**
```bash
git clone https://github.com/lnitc/text-to-sql.git
cd text-to-sql
```

**2. Create GCP Service Account**
```bash
# Go to Google Cloud Console > Service Accounts
# Create new service account
# Grant "BigQuery Admin" role
# Create JSON key and download as gcp-key.json
# Place gcp-key.json in project root
```

**3. Configure Environment**
```bash
# Copy template
cp .env.example .env

# Edit .env with your credentials
# OPENAI_API_KEY=sk-proj-...
# GCP_PROJECT_ID=your-project-id
```

**4. Start Docker Containers**
```bash
docker compose up -d
```

**5. Verify Services**
```bash
# Check containers are running
docker compose ps

# Test backend health
curl http://localhost:8000/health

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

**6. Test the Application**
- Open http://localhost:3000 in your browser
- Type a natural language question (e.g., "How many orders were placed last week?")
- Watch the AI generate SQL, execute it, and render results!

### Option 2: Local Development (Without Docker)

**Frontend**
```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:3000
```

**Backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --reload
# Runs on http://localhost:8000
```

**Environment Variables** (for local development)
```bash
cd backend
# Create .env.local or set environment variables
export OPENAI_API_KEY=sk-proj-...
export GCP_PROJECT_ID=your-project-id
export GOOGLE_APPLICATION_CREDENTIALS=./gcp-key.json
```

---

## 📖 Usage Guide

### Basic Usage

1. **Open the Application**
   - Navigate to http://localhost:3000

2. **Ask a Question**
   - Type a natural language question in the chat input
   - Examples:
     - "How many orders were placed in the last 7 days?"
     - "What were the top 5 product categories by revenue?"
     - "Show me the distribution of orders by month"

3. **View Results**
   - AI generates and executes SQL query
   - Results displayed with visualization (chart or table)
   - SQL query available in collapsible panel

4. **Save to Favorites**
   - Click the star icon on a query to favorite it
   - Favorites appear in the "Favorites" panel on the left

5. **View History**
   - All queries are saved in session history
   - Click on previous queries to re-run them

### Advanced Features

**Collapsible SQL Query Panel**
- Click "SQL Query" to expand/collapse
- Copy button to copy SQL to clipboard
- Useful for auditing or manual execution

**Dark Mode** (currently hidden)
- Toggle available in sidebar (can be re-enabled)

**Query Modification**
- Edit previous queries and re-submit
- Try different variations to explore data

---

## 🔧 Configuration

### Environment Variables

**Backend (.env)**
```env
# Pipeline: simple (default, one LLM call) or crew (CrewAI multi-agent flow)
PIPELINE_MODE=simple

# OpenAI Configuration
OPENAI_API_KEY=sk-proj-xxxxx
OPENAI_MODEL=gpt-4o              # or gpt-4-turbo for cost savings
OPENAI_MAX_TOKENS=2000
OPENAI_TEMPERATURE=0.7
OPENAI_MONTHLY_BUDGET=15

# GCP Configuration
GOOGLE_APPLICATION_CREDENTIALS=gcp-key.json  # Local: file path
                                             # Docker: /secrets/gcp-key.json
GCP_PROJECT_ID=your-gcp-project-id

# BigQuery Configuration
BQ_DATASET_PROJECT=bigquery-public-data
BQ_DATASET_ID=thelook_ecommerce
BQ_QUERY_TIMEOUT_SECONDS=30
BQ_MAX_RESULTS_ROWS=1000
BQ_MAX_BYTES_BILLED=10737418240  # Per-query scan cap (10 GB)

# Application Configuration
ENVIRONMENT=development          # development, staging, production
DEBUG=False
LOG_LEVEL=INFO
```

**Frontend (.env.local)**
```env
# Called from the browser, so use a host-reachable URL (also under Docker)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ENVIRONMENT=development
```

### Customizing the Data Source

To use your own BigQuery dataset instead of the public data:

1. Update `.env`:
```env
BQ_DATASET_PROJECT=your-project-id
BQ_DATASET_ID=your-dataset-id
```

2. Ensure your GCP service account has permissions:
   - BigQuery Data Viewer
   - BigQuery Job User

3. Update the schema information in `backend/agents/data_crew.py`:
```python
# Update the SCHEMA_INFO variable with your table structures
SCHEMA_INFO = """
Your custom schema description here
"""
```

---

## 🧪 Testing

### Manual Testing (In Progress)

The following test scenarios are currently being executed:

- ✅ Basic query execution with different chart types
- ✅ Error handling with invalid queries
- ✅ Favorites add/remove functionality
- ✅ Query history retention
- ✅ Dark mode toggle (when enabled)
- 🧪 Edge cases: Very large result sets, timeouts, API errors
- 🧪 Performance: Response time measurements
- 🧪 Cross-browser compatibility

### Running Tests Locally

**Backend API Tests**
```bash
cd backend
# Test health endpoint
curl http://localhost:8000/health

# Test chat API
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"user_query": "How many orders were placed last week?"}'
```

**Frontend Testing**
- Open http://localhost:3000 in browser
- Test with various query types
- Check console for any JavaScript errors

### Example Test Queries

1. **Simple Aggregation**
   - Query: "How many orders were placed?"
   - Expected: Single number result

2. **Time-based Filtering**
   - Query: "Show me orders from the last 30 days"
   - Expected: Time-series or period comparison

3. **Categorical Analysis**
   - Query: "What are the top 5 product categories?"
   - Expected: Bar chart with categories

4. **Complex Filtering**
   - Query: "Which users spent the most money in Q3?"
   - Expected: Sorted table or top-N chart

---

## 📁 Project Structure

```
text-to-sql/
├── frontend/                          # Next.js 16 Frontend Application
│   ├── app/
│   │   ├── page.tsx                  # Main page
│   │   ├── ChatInterface.tsx          # Chat UI component
│   │   ├── ChatMessage.tsx            # Individual message component
│   │   ├── ChartRenderer.tsx          # Dynamic chart rendering
│   │   ├── api.ts                     # API client (Axios)
│   │   ├── globals.css                # Tailwind CSS configuration
│   │   └── layout.tsx                 # Root layout
│   ├── components/
│   │   ├── Sidebar.tsx                # Left sidebar (favorites, history)
│   │   └── ThemeToggle.tsx            # Dark mode toggle
│   ├── public/                        # Static assets
│   ├── tailwind.config.ts             # Tailwind CSS configuration
│   ├── next.config.ts                 # Next.js configuration (Turbopack)
│   ├── tsconfig.json                  # TypeScript configuration
│   ├── package.json                   # Dependencies
│   ├── Dockerfile                     # Docker image definition
│   └── .dockerignore                  # Docker build ignore patterns
│
├── backend/                           # FastAPI Backend Application
│   ├── main.py                        # FastAPI app & endpoints
│   ├── config.py                      # Configuration & settings validation
│   ├── agents/
│   │   ├── data_crew.py              # CrewAI agents definition
│   │   └── simplified_pipeline.py    # Alternative pipeline implementation
│   ├── tools/
│   │   └── bigquery_tool.py          # BigQuery execution tool
│   ├── models/
│   │   └── schemas.py                # Pydantic schemas & models
│   ├── requirements.txt               # Python dependencies
│   ├── run.py                         # Uvicorn startup wrapper
│   ├── Dockerfile                     # Docker image definition
│   └── .dockerignore                  # Docker build ignore patterns
│
├── docker-compose.yml                 # Docker Compose orchestration
├── .env                               # Environment variables (DO NOT COMMIT)
├── .env.example                       # Environment template
├── .gitignore                         # Git ignore patterns
├── gcp-key.json                       # GCP Service Account (DO NOT COMMIT)
├── README.md                          # This file
├── PHASE_5_DEPLOYMENT_COMPLETE.md     # Deployment status
├── DOCKER_QUICK_START.md              # Docker quick reference
└── LICENSE                            # MIT License
```

---

## 🐛 Troubleshooting

### Docker Issues

**Problem**: Containers won't start
```bash
# Solution 1: Verify Docker is running
docker ps

# Solution 2: Check for port conflicts
lsof -i :3000    # macOS/Linux
netstat -tuln | grep 3000  # Linux
Get-NetTCPConnection -LocalPort 3000  # Windows (PowerShell)

# Solution 3: Rebuild from scratch
docker compose down -v
docker compose up -d --build
```

**Problem**: "gcp-key.json: The system cannot find the path specified"
```bash
# On Windows, ensure:
# 1. gcp-key.json exists in project root
# 2. Docker Desktop has permission to mount volumes
# 3. Restart Docker Desktop
# 4. Use: docker compose down && docker compose up -d
```

### Backend Issues

**Problem**: "Settings validation failed: GOOGLE_APPLICATION_CREDENTIALS is not set"
```bash
# Check .env file has:
GOOGLE_APPLICATION_CREDENTIALS=/secrets/gcp-key.json
GCP_PROJECT_ID=your-actual-project-id

# Check logs:
docker compose logs backend
```

**Problem**: BigQuery query timeouts
```bash
# Increase timeout in .env:
BQ_QUERY_TIMEOUT_SECONDS=60  # default is 30

# Optimize query in the agent (reduce result set):
BQ_MAX_RESULTS_ROWS=500  # default is 1000
```

**Problem**: OpenAI API errors
```bash
# Check API key format:
# Should start with: sk-proj-
# Should be in .env file

# Check quota/credits:
# Visit https://platform.openai.com/account/billing

# Model deprecated error:
# Update to gpt-4-turbo or gpt-4o in .env
OPENAI_MODEL=gpt-4o
```

### Frontend Issues

**Problem**: "No styling visible" / "Tailwind CSS not applied"
```bash
# Solution 1: Build locally first
cd frontend
npm run build

# Solution 2: Rebuild Docker image
docker compose up -d --build

# Solution 3: Clear Docker cache
docker system prune -a
docker compose up -d --build
```

**Problem**: API returns 503 Service Unavailable
```bash
# Check backend is running:
docker compose ps

# Check backend logs:
docker compose logs backend -f

# Test API directly:
curl http://localhost:8000/health
```

**Problem**: CORS errors in browser console
```bash
# Ensure NEXT_PUBLIC_API_URL is correct in .env
# For Docker: http://backend:8000
# For local: http://localhost:8000

# Backend has CORS configured for localhost:3000
# Check in backend/main.py if using different port
```

### Data Issues

**Problem**: "No data returned" or empty results
```bash
# Verify public dataset is accessible:
# BigQuery Console > bigquery-public-data > thelook_ecommerce

# Check tables exist:
# Tables should include: order_items, products, users, events, inventory_items

# Test query manually in BigQuery Console:
SELECT COUNT(*) FROM `bigquery-public-data.thelook_ecommerce.order_items`
```

---

## 📊 Performance & Monitoring

### Expected Response Times

| Operation | Time | Notes |
|-----------|------|-------|
| Simple COUNT query | 2-3s | Including SQL generation |
| Aggregation query | 3-5s | With GROUP BY |
| JOIN query | 4-7s | Multiple tables |
| Complex filtering | 2-4s | Depends on data volume |

### Monitoring

**Backend Logs**
```bash
docker compose logs backend -f
```

**Frontend Console**
- Open browser DevTools (F12)
- Watch Network tab for API calls
- Check Console for errors

**BigQuery Console**
- Visit https://console.cloud.google.com/bigquery
- View query history and costs
- Monitor slot usage

---

## 🔐 Security Considerations

### Credentials Management
- ✅ **DO**: Use `.env` for secrets (NOT COMMITTED)
- ✅ **DO**: Rotate GCP service account keys periodically
- ✅ **DO**: Limit service account to BigQuery permissions only
- ❌ **DON'T**: Commit `gcp-key.json` to repository
- ❌ **DON'T**: Commit `.env` with real credentials
- ❌ **DON'T**: Share credentials in logs or error messages

### Backend Security
- Input validation via Pydantic models
- SQL injection mitigation (parameterized queries via BigQuery client)
- CORS restricted to localhost:3000 (configurable)
- Rate limiting not yet implemented (planned for Phase 5+)

### GCP Service Account
```json
// Minimal permissions needed (Principle of Least Privilege):
{
  "roles": [
    "roles/bigquery.dataViewer",        // Read data
    "roles/bigquery.jobUser"            // Execute queries
  ]
}
```

### Frontend Security
- No sensitive data stored in localStorage (only query history)
- API calls use HTTPS in production
- Content Security Policy (can be enhanced)

---

## 💡 Architecture Decisions

### Why Two Pipelines?
The backend ships two interchangeable pipelines with the same API contract,
selected by `PIPELINE_MODE` or per request (the UI's "Multi-agent analysis" toggle):

- **simple** (default, `agents/simplified_pipeline.py`): one LLM call writes the
  SQL, with automatic correction if BigQuery rejects it. ~3 s per question.
- **crew** (`agents/data_crew.py`): a CrewAI Flow with three agents:
  - *Planner*: interprets the question and decides how to answer it (or that it can't be answered)
  - *SQL developer*: writes the query and fixes it from dry-run/execution errors
  - *Analyst*: writes the answer, insights and follow-up questions from the result rows

  Validation, execution and chart selection are deterministic code steps shared
  with the simple pipeline. ~13-25 s and roughly 5-10x the token cost per question.

See `dev_docs/CREWAI_PIPELINE_REVIEW.md` for why the original crew was rebuilt.

### Why BigQuery Public Data?
- Free tier for portfolio projects
- No data ingestion costs
- Real-world eCommerce dataset for realistic queries
- Demonstrates ability to work with production-grade systems

### Why Next.js 16 + Turbopack?
- Latest React framework with server components
- Turbopack provides 5-10x faster builds
- TypeScript out-of-the-box
- App Router (modern routing)
- Integrated with Vercel for easy deployment

### Why FastAPI over Django/Flask?
- Modern Python web framework (async/await support)
- Automatic API documentation (Swagger UI)
- Built-in validation (Pydantic)
- High performance (uvicorn)
- Type hints for better IDE support

### Simplified Features (Cost Optimization)
- ⏱️ Query result caching (planned but not implemented)
- 💾 Database caching layer (using public data reduces need)
- 🔄 Connection pooling (single-user POC)
- 📊 Advanced analytics (query builder still in testing)

---

## 🎯 Known Limitations & Future Work

### Current Limitations
1. **Single-user** - No authentication/multi-user support yet
2. **Session-based** - No persistent query storage across sessions
3. **Limited Error Recovery** - Some error states show raw API errors
4. **No Result Caching** - Each query re-executes against BigQuery
5. **Query Builder** - Visual query construction still in testing phase
6. **Dark Mode** - Hidden from UI, needs theme persistence
7. **Limited Visualizations** - Only Bar, Line, Pie, Table charts

### Planned Features (Phase 5+)
- [ ] User authentication and multi-user support
- [ ] Persistent query database
- [ ] Advanced query caching with invalidation
- [ ] Query result export (CSV, Parquet, JSON)
- [ ] Query Builder UI (currently in testing)
- [ ] Real-time query cost estimation
- [ ] Query performance recommendations
- [ ] Multi-turn conversation context
- [ ] Custom metric definitions
- [ ] Advanced error recovery

### Testing Status
- ✅ Unit tests for core components
- ✅ Integration tests for API endpoints
- 🧪 End-to-end testing (in progress)
- 🧪 Performance testing (in progress)
- 🧪 Load testing (not started)
- 🧪 Error scenario testing (in progress)

### Python 3.11 Deprecation
The backend uses Python 3.11, which will reach end-of-life on 2027-10-24.
**Planned upgrade**: Python 3.12 (breaking change release, minor version bump)

---

## 📈 Cost Analysis

### Monthly Costs (Estimated)

**Google Cloud Platform**
- BigQuery: $2-5 (depending on query volume)
- Storage: $0 (using free public dataset)
- Compute: $0 (no App Engine/Cloud Run)

**OpenAI API**
- GPT-4o: $5-10 (200 queries × ~$0.025-0.05 per query)
- Alternative: GPT-4-turbo for $3-7 (cheaper)

**Infrastructure**
- Docker Desktop: Free (development)
- Deployment: Varies ($5-50 on Cloud Run/App Engine)

**Total**: $7-15/month for portfolio use

### Cost Optimization Strategies
1. ✅ Using free public BigQuery dataset
2. ✅ Limiting results to 1000 rows per query
3. ✅ Setting max tokens for LLM output
4. ✅ Can switch to cheaper models (GPT-4-turbo)
5. 🔄 Planned: Query result caching (reduces API calls)
6. 🔄 Planned: Scheduled cleanup jobs
7. 🔄 Planned: Cost alerts and budgeting

### Cost Per Query Breakdown
```
Query Execution:
- SQL Generation (GPT-4o): ~$0.01-0.03
- BigQuery execution: ~$0.01-0.10 (depends on data size)
- Result formatting: ~$0.001-0.01

Total per query: ~$0.02-0.15 (average: ~$0.05)
```

---

## 🤝 Contributing

This is a portfolio/POC project. Contributions and suggestions are welcome!

### To Contribute
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Use TypeScript for frontend, Python type hints for backend
- Follow existing code style and conventions
- Add tests for new features
- Update documentation for significant changes

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 📧 Support & Questions

For questions, issues, or suggestions:
- Open an issue on GitHub
- Check existing documentation in project root
- Review deployment guides (DOCKER_QUICK_START.md, PHASE_5_DEPLOYMENT_COMPLETE.md)

---

## 🙏 Acknowledgments

- **CrewAI** - Multi-agent orchestration framework
- **FastAPI** - Modern Python web framework
- **Next.js** - React framework with Turbopack bundler
- **Google Cloud** - BigQuery and infrastructure
- **OpenAI** - GPT-4o language model
- **Recharts** - React charting library
- **LangChain** - LLM integration tools

---

## 📌 Quick Links

- 📖 [Local Setup Guide](./DOCKER_QUICK_START.md)
- 🚀 [Deployment Status](./PHASE_5_DEPLOYMENT_COMPLETE.md)
- 🔧 [Environment Configuration](./.env.example)
- 🐛 [Troubleshooting](#-troubleshooting)
- 📊 [Cost Analysis](#-cost-analysis)

---

## 🏷️ Project Status

| Component | Status | Notes |
|-----------|--------|-------|
| **Backend** | ✅ Stable | FastAPI + CrewAI working reliably |
| **Frontend** | ✅ Stable | Next.js 16 with Tailwind CSS |
| **BigQuery Integration** | ✅ Stable | Queries execute successfully |
| **Docker Deployment** | ✅ Stable | Both containers healthy |
| **Error Handling** | 🟡 Partial | Basic errors shown, recovery in progress |
| **Caching** | 🟡 Planned | Not yet implemented |
| **Query Builder** | 🧪 Testing | Still in development |
| **Testing** | 🧪 In Progress | Manual testing ongoing |
| **Documentation** | ✅ Complete | README and guides available |
| **Production Ready** | ❌ Not Yet | More testing and hardening needed |

---

**Last Updated**: October 24, 2026  
**POC Status**: Active Development - Testing in Progress  
**Version**: 1.0.0-POC

---

## Quick Start (TL;DR)

```bash
# 1. Clone
git clone https://github.com/lnitc/text-to-sql.git
cd text-to-sql

# 2. Setup credentials
# - Create GCP service account
# - Download JSON key as gcp-key.json
# - Get OpenAI API key
# - Copy .env.example to .env and fill in values

# 3. Start
docker compose up -d

# 4. Access
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# Docs: http://localhost:8000/docs

# 5. Test
# Ask a question in the chat interface!
```

---

Made with ❤️ for portfolio | POC | Active Development
