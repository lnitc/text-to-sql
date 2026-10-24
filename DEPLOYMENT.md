# Phase 5: Deployment Guide - Docker & Local Setup

## Overview

This guide covers deploying the Text-to-SQL Agentic Data Analyst application using Docker. The application consists of two main services:

- **Backend:** FastAPI + Python 3.11, CrewAI, BigQuery integration
- **Frontend:** Next.js 16 (App Router), TypeScript, Tailwind CSS

Both services are orchestrated using Docker Compose for local development and can be deployed to cloud platforms like Google Cloud Run, AWS ECS, or Azure Container Instances.

---

## Prerequisites

### Local Development (Outside Docker)
- Python 3.11+
- Node.js 20+ with npm
- Google Cloud SDK (`gcloud` CLI)
- GCP service account JSON key

### Docker Deployment
- Docker 24.0+
- Docker Compose 2.0+
- Docker Desktop (Windows/Mac) or Docker Engine (Linux)

### GCP Setup (Required for All)
- Active GCP project with billing enabled
- BigQuery API enabled
- Service account with BigQuery Data Editor role
- Service account JSON key file

---

## Environment Configuration

### 1. Create `.env.local` from template

```bash
cd /path/to/text-to-sql
cp .env.example .env.local
```

### 2. Fill in required values

```bash
# .env.local

# OpenAI Configuration (required)
OPENAI_API_KEY=sk-your-actual-openai-key

# GCP Configuration (required)
GOOGLE_APPLICATION_CREDENTIALS=gcp-key.json
GCP_PROJECT_ID=your-gcp-project-id

# Optional: Customize API base URL
NEXT_PUBLIC_API_URL=http://backend:8000

# Optional: Set environment
ENVIRONMENT=development
```

### 3. Verify GCP credentials

```bash
# Check that GCP key file exists
ls -la gcp-key.json

# Verify it's valid JSON
cat gcp-key.json | python -m json.tool > /dev/null && echo "Valid JSON"

# Check permissions (should be readable only by you)
ls -l gcp-key.json  # Should show -rw-r--r-- or more restrictive
```

### 4. Test GCP access (optional)

```bash
# List your GCP projects
gcloud config list

# Test BigQuery access
gcloud bigquery query --use_legacy_sql=false "SELECT 1 as test"
```

---

## Local Development Without Docker

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run FastAPI server
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Server runs at: http://localhost:8000
# API docs: http://localhost:8000/docs
```

### Frontend Setup (New Terminal)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run Next.js development server
npm run dev

# Server runs at: http://localhost:3000
```

### Verify Setup

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Backend Docs: http://localhost:8000/docs

---

## Docker Deployment - Local Development

### Quick Start

```bash
# Build and start both services
docker-compose up --build

# Services will be available at:
# - Frontend: http://localhost:3000
# - Backend: http://localhost:8000
# - Backend Docs: http://localhost:8000/docs
```

### Common Docker Compose Commands

```bash
# Start services (without rebuilding)
docker-compose up

# Start in background
docker-compose up -d

# Stop services
docker-compose down

# Rebuild images
docker-compose up --build

# View logs for all services
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart services
docker-compose restart

# Remove all containers, networks, and volumes
docker-compose down -v
```

### Environment Variables in Docker

The `.env.local` file is automatically loaded by docker-compose. No additional setup needed.

**Important:** Sensitive values (OPENAI_API_KEY, GCP credentials) should:
- Never be hardcoded in Dockerfiles
- Always be passed via environment variables
- Never be committed to git

### Verify Services Are Healthy

```bash
# Check service status
docker-compose ps

# Test backend health
curl http://localhost:8000/health

# Test frontend
curl http://localhost:3000

# View service logs
docker-compose logs backend
docker-compose logs frontend
```

---

## Docker Compose Architecture

### Services Overview

```yaml
services:
  backend:
    - Image: Python 3.11 + FastAPI + CrewAI
    - Port: 8000
    - Health check: /health endpoint
    - Volumes: Source code (hot reload), GCP key mount
    - Depends on: GCP credentials

  frontend:
    - Image: Node 20 + Next.js 16
    - Port: 3000
    - Health check: localhost:3000 HTTP check
    - Volumes: Source code (hot reload), node_modules
    - Depends on: backend service health

  network:
    - Type: Bridge network
    - Purpose: Services communicate via service names (e.g., http://backend:8000)
```

### Volume Mounts

**Backend Volumes:**
```yaml
volumes:
  - ${GCP_KEY_PATH}:/secrets/gcp-key.json:ro  # GCP credentials (read-only)
  - ./backend:/app                             # Source code (hot reload)
  - /app/venv                                  # Exclude virtual env
  - /app/__pycache__                           # Exclude Python cache
```

**Frontend Volumes:**
```yaml
volumes:
  - ./frontend:/app                            # Source code (hot reload)
  - /app/node_modules                          # Exclude dependencies
  - /app/.next                                 # Exclude build output
```

### Health Checks

Both services have health checks configured:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]  # Backend
  interval: 30s      # Check every 30 seconds
  timeout: 10s       # Fail if check takes >10s
  retries: 3         # Fail after 3 consecutive failures
  start_period: 5s   # Wait 5s before first check
```

Docker uses health checks to:
- Restart unhealthy services automatically
- Delay frontend startup until backend is ready
- Monitor service status with `docker-compose ps`

---

## Production Deployment Considerations

### Image Optimization

**Current Setup (Development):**
```bash
# With hot reload and dev dependencies
Backend image: ~800MB
Frontend image: ~400MB
```

**For Production:** Remove `--reload` flag in backend Dockerfile:
```dockerfile
# Production: Use multiple workers instead of reload
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Environment Setup

**Development (.env.local):**
```
ENVIRONMENT=development
NEXT_PUBLIC_API_URL=http://backend:8000
LOG_LEVEL=INFO
```

**Production (.env.production):**
```
ENVIRONMENT=production
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
LOG_LEVEL=WARNING
```

### Resource Limits (Optional)

Uncomment in docker-compose.yml for production:

```yaml
deploy:
  resources:
    limits:
      cpus: '1'
      memory: 1G
    reservations:
      cpus: '0.5'
      memory: 512M
```

### Security Best Practices

1. **Secrets Management:**
   - Use Docker secrets (Swarm) or environment variables
   - Never build secrets into images
   - Use .gitignore to prevent .env commits

2. **Network Security:**
   - Use bridge networks (default in docker-compose)
   - Restrict exposed ports
   - Use HTTPS in production

3. **Image Security:**
   - Use specific version tags (not 'latest')
   - Scan images for vulnerabilities
   - Keep base images updated

4. **Access Control:**
   - Run as non-root user (optional, add to Dockerfile)
   - Use read-only root filesystem (production)
   - Implement RBAC for container orchestration

---

## Troubleshooting

### Backend Container Won't Start

```bash
# Check logs
docker-compose logs backend

# Common issues:
# 1. GCP credentials not found
#    → Verify GCP_KEY_PATH in .env.local
#    → Check gcp-key.json exists and is readable

# 2. OpenAI API key invalid
#    → Verify OPENAI_API_KEY is set correctly
#    → Check it starts with 'sk-'

# 3. Port 8000 already in use
#    → Kill existing process: lsof -i :8000 | awk 'NR!=1 {print $2}' | xargs kill -9
#    → Or change BACKEND_PORT in .env.local
```

### Frontend Container Won't Start

```bash
# Check logs
docker-compose logs frontend

# Common issues:
# 1. Backend not healthy
#    → Wait for backend to start: docker-compose logs backend
#    → Check backend health: curl http://localhost:8000/health

# 2. Dependencies not installed
#    → Clear and rebuild: docker-compose down && docker-compose up --build

# 3. Port 3000 already in use
#    → Kill process: lsof -i :3000 | awk 'NR!=1 {print $2}' | xargs kill -9
#    → Or map to different port in docker-compose.yml
```

### Services Can't Communicate

```bash
# Verify network
docker network ls
docker network inspect text-to-sql_app-network

# Test connectivity from frontend to backend
docker-compose exec frontend curl http://backend:8000/health

# Should return JSON response with status field
```

### Performance Issues

```bash
# Check resource usage
docker stats

# If services are memory-constrained:
# 1. Add resource limits in docker-compose.yml
# 2. Reduce cache sizes in config.py
# 3. Limit maximum concurrent connections

# Check disk space
docker system df

# Clean up unused images/containers
docker system prune -a
```

---

## Logs & Monitoring

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Last N lines
docker-compose logs --tail=100 backend

# Follow and filter
docker-compose logs -f backend | grep "ERROR"
```

### Log Levels (Backend)

Set via `LOG_LEVEL` environment variable:
- **DEBUG:** Verbose, all details (development only)
- **INFO:** Standard logging (default)
- **WARNING:** Important events only
- **ERROR:** Errors only
- **CRITICAL:** Critical errors only

### Request Logging (Backend)

Enable/disable with `ENABLE_REQUEST_LOGGING`:
```
ENABLE_REQUEST_LOGGING=true   # Log all HTTP requests
ENABLE_REQUEST_LOGGING=false  # Disable request logging
```

---

## Health Checks & Service Readiness

### Backend Health Endpoint

```bash
curl http://localhost:8000/health

# Response:
{
  "status": "ok",
  "message": "Application is healthy",
  "version": "1.0.0"
}
```

### Frontend Health Check

```bash
curl http://localhost:3000

# Response: HTML page (200 status)
```

### Dependency Status

```bash
docker-compose ps

# Shows:
# - SERVICE NAME
# - STATUS (running, exited, restarting)
# - PORTS
# - Health check status (healthy/unhealthy)
```

---

## Updating Services

### After Code Changes

```bash
# Option 1: With hot reload (default)
# Services automatically reload code changes
# No need to restart

# Option 2: Manual rebuild
docker-compose up --build

# Option 3: Rebuild specific service
docker-compose up --build backend
docker-compose up --build frontend
```

### After Dependency Changes

```bash
# Backend (requirements.txt changed)
docker-compose up --build backend

# Frontend (package.json changed)
docker-compose up --build frontend

# Both
docker-compose down && docker-compose up --build
```

### After Environment Changes

```bash
# .env.local was updated
docker-compose down
docker-compose up --build

# Or just restart (if only env values changed, not secrets)
docker-compose restart
```

---

## Next Steps: Cloud Deployment

This Docker Compose setup is ready for cloud deployment to:

1. **Google Cloud Run** (Recommended - serverless, auto-scaling)
2. **Google Cloud Compute Engine** (VMs)
3. **Google Kubernetes Engine (GKE)** (Kubernetes)
4. **AWS ECS/Fargate**
5. **Azure Container Instances**

For cloud deployment, you would:
1. Push images to container registry (Google Artifact Registry, ECR, ACR)
2. Configure environment variables in cloud platform
3. Set up reverse proxy/load balancer
4. Configure custom domain and HTTPS
5. Set up monitoring and logging

---

## Useful Docker Commands Reference

```bash
# Image operations
docker images                          # List images
docker build -t image:tag .           # Build image
docker rmi image:tag                  # Remove image

# Container operations
docker ps                              # List running containers
docker ps -a                           # List all containers
docker run -it image:tag /bin/bash    # Run container interactively
docker exec -it container bash        # Execute command in running container
docker logs container                  # View container logs
docker stop container                  # Stop container
docker rm container                    # Remove container

# Docker Compose operations
docker-compose up                      # Start services
docker-compose down                    # Stop and remove services
docker-compose ps                      # List services
docker-compose logs service            # View service logs
docker-compose exec service bash       # Execute command in service

# System operations
docker system df                       # Disk usage
docker system prune                    # Clean up unused resources
docker stats                           # Resource usage
```

---

## Configuration Files Summary

| File | Purpose | Commits |
|------|---------|---------|
| `docker-compose.yml` | Service orchestration | ✅ Existing |
| `backend/Dockerfile` | Backend container image | ✅ Existing |
| `backend/.dockerignore` | Exclude files from build | ✅ Existing |
| `frontend/Dockerfile` | Frontend container image | ✅ New (created this phase) |
| `frontend/.dockerignore` | Exclude files from build | ✅ New (created this phase) |
| `.env.example` | Environment template | ✅ Existing |
| `.env.local` | Local environment (not in git) | ⚠️ Create from .env.example |

---

## Checklist - Phase 5 Deployment Setup

- [x] Docker Compose configuration reviewed and working
- [x] Backend Dockerfile created and tested
- [x] Frontend Dockerfile created and tested
- [x] Environment configuration documented
- [x] Health checks implemented
- [x] Deployment guide created
- [ ] Cloud deployment (future phase)

---

## Support & Documentation

For more information, see:
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Next.js Deployment](https://nextjs.org/learn/basics/deploying-nextjs-app)
- [Google Cloud Run](https://cloud.google.com/run/docs)

---

**Status:** Phase 5 Deployment Setup - COMPLETE  
**Next:** Cloud deployment documentation and setup
