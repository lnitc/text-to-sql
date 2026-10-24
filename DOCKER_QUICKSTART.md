# Docker Quick Start Guide

## 🚀 Get Up and Running in 5 Minutes

### Prerequisites Check

```bash
docker --version          # Should be 24.0+
docker-compose --version  # Should be 2.0+
```

### Step 1: Setup Environment (2 minutes)

```bash
# Copy environment template
cp .env.example .env.local

# Edit .env.local and add:
# - OPENAI_API_KEY (from https://platform.openai.com/api-keys)
# - GCP_PROJECT_ID (your Google Cloud project)
# - Ensure gcp-key.json exists in project root
```

### Step 2: Start Services (1 minute)

```bash
# Build and start everything
docker-compose up --build

# Services will start and be available at:
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### Step 3: Verify It's Working (2 minutes)

```bash
# In a new terminal, test backend health
curl http://localhost:8000/health

# Expected response:
# {"status":"ok","message":"Application is healthy","version":"1.0.0"}

# Test frontend
open http://localhost:3000  # macOS
xdg-open http://localhost:3000  # Linux
start http://localhost:3000  # Windows
```

---

## Common Tasks

### Stop Services

```bash
docker-compose down
```

### View Logs

```bash
# All services
docker-compose logs -f

# Just backend
docker-compose logs -f backend

# Just frontend
docker-compose logs -f frontend
```

### Restart After Code Changes

```bash
# With hot reload (default), changes reload automatically
# If needed, manually rebuild:
docker-compose up --build
```

### Clean Everything

```bash
# Stop and remove all containers
docker-compose down -v

# Remove dangling images
docker system prune -a
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `Port 8000 already in use` | Change `BACKEND_PORT=8000` to `BACKEND_PORT=8001` in `.env.local` |
| `Port 3000 already in use` | Change port in `docker-compose.yml` |
| Backend won't start | Check `.env.local` has `OPENAI_API_KEY` and `GCP_PROJECT_ID` |
| Can't find gcp-key.json | Place your GCP service account JSON in project root as `gcp-key.json` |
| Backend unhealthy | Check logs: `docker-compose logs backend` |

---

## 📚 For More Details

See [DEPLOYMENT.md](./DEPLOYMENT.md) for comprehensive deployment guide.
