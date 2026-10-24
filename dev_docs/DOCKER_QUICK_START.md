# Docker Quick Start Guide

## Prerequisites
- Docker Desktop installed and running
- `gcp-key.json` in project root directory
- `.env` file with credentials configured

## Quick Start Commands

### Start the Application
```bash
docker compose up -d
```

### Verify Services Are Running
```bash
docker compose ps
```

Expected output:
```
NAME                   IMAGE                  STATUS              PORTS
text-to-sql-backend    text-to-sql-backend    Up (healthy)        0.0.0.0:8000->8000/tcp
text-to-sql-frontend   text-to-sql-frontend   Up (healthy)        0.0.0.0:3000->3000/tcp
```

### Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Check Backend Health
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "ok",
  "message": "Settings validated successfully",
  "version": "1.0.0"
}
```

### Test Chat API
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"user_query": "How many orders were placed in the last 7 days?"}'
```

### View Backend Logs
```bash
docker compose logs backend -f
```

### View Frontend Logs
```bash
docker compose logs frontend -f
```

### Rebuild Images (after code changes)
```bash
docker compose up -d --build
```

### Stop the Application
```bash
docker compose down
```

### Reset Everything (WARNING: removes volumes)
```bash
docker compose down -v
docker compose up -d
```

## Troubleshooting

### Containers won't start
1. Check Docker Desktop is running
2. Verify ports 3000 and 8000 are not in use
3. Check `.env` file exists and has required variables
4. Check `gcp-key.json` exists in project root

### Backend shows credential errors
- Verify `gcp-key.json` exists: `ls gcp-key.json`
- Verify `.env` has `GOOGLE_APPLICATION_CREDENTIALS=/secrets/gcp-key.json`
- Restart containers: `docker compose down && docker compose up -d`

### Frontend has no styling
- This should be fixed, but if styling missing:
  - Delete `.next` folder locally
  - Run `npm run build` in frontend directory
  - Rebuild Docker: `docker compose up -d --build`

### API returns 503 Service Unavailable
- Check backend logs: `docker compose logs backend`
- Verify GCP credentials loaded: Look for "Settings validated successfully"
- Check internet connectivity to BigQuery

## Environment Variables

Key variables in `.env`:
```
OPENAI_API_KEY=sk-proj-...           # OpenAI API key
GCP_PROJECT_ID=data-eng-...          # GCP project ID
GOOGLE_APPLICATION_CREDENTIALS=/secrets/gcp-key.json  # Path inside container
NEXT_PUBLIC_API_URL=http://backend:8000  # Frontend to backend
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Docker Network                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────────┐    ┌──────────────────────┐  │
│  │ Frontend Container   │    │ Backend Container    │  │
│  │ (Next.js)            │    │ (FastAPI)            │  │
│  │ Port: 3000           │    │ Port: 8000           │  │
│  │                      │◄──►│                      │  │
│  │ http://localhost:300 │    │ http://localhost:800 │  │
│  └──────────────────────┘    └──────────────────────┘  │
│                                      │                  │
│                                      │ BigQuery API     │
│                                      │                  │
└──────────────────────────────────────┼──────────────────┘
                                       │
                              ┌────────▼────────┐
                              │  Google Cloud   │
                              │  BigQuery       │
                              └─────────────────┘
```

## Performance Notes
- Initial query: 4-5 seconds (includes SQL generation, execution, visualization)
- Subsequent similar queries: 2-3 seconds (depends on BigQuery caching)
- CSS loading: ~28KB (full Tailwind CSS included in .next build)

## For Development

### Local Development (without Docker)
```bash
# Terminal 1: Frontend
cd frontend
npm install
npm run dev

# Terminal 2: Backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

### Building Frontend for Production
```bash
cd frontend
npm run build
# Then update docker-compose to copy pre-built .next
```

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Port 3000 in use | Stop other services or use `docker compose up -d --force-recreate` |
| Port 8000 in use | Same as above |
| No styling in UI | Rebuild frontend: `npm run build && docker compose up -d` |
| API 503 errors | Check backend logs for credential issues |
| BigQuery connection fails | Verify GCP service account has BigQuery permissions |
| Slow queries | Check BigQuery dashboard for performance issues |

## Next Steps
1. Open http://localhost:3000 in browser
2. Send a test query from the chat interface
3. Verify visualization renders correctly
4. Test different query types and chart types
5. Check favorites and history features
