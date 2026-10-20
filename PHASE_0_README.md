# Phase 0: Environment Setup ✅

**Status**: Complete  
**Estimated Time**: 2-3 hours  
**Prerequisites**: Git, Docker Desktop, GCP account

---

## 📋 What Was Created

### ✅ Directory Structure
```
text-to-sql/
├── backend/
│   ├── tools/
│   ├── agents/
│   ├── schemas/
│   ├── utils/
│   ├── Dockerfile
│   ├── .dockerignore
│   └── requirements.txt (will be created in Phase 1)
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   ├── lib/
│   │   └── hooks/
│   ├── public/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── package.json (will be created in Phase 3)
│   └── tsconfig.json (will be created in Phase 3)
│
├── docker-compose.yml          ✅ Created
├── .env.example                ✅ Created
├── .gitignore                  ✅ Created
├── plan.md                     ✅ Created (Phase overview)
└── README.md                   (This file)
```

### ✅ Configuration Files
- **`docker-compose.yml`**: Orchestrates backend and frontend services
- **`.env.example`**: Environment variable template (secrets not included)
- **`.gitignore`**: Protects sensitive files from Git
- **Backend `Dockerfile`**: Multi-stage Python 3.11 FastAPI container
- **Frontend `Dockerfile`**: Multi-stage Node.js 18 Next.js container
- **`.dockerignore` files**: Reduces image size by excluding unnecessary files

---

## 🔧 GCP Setup (Manual Step)

You need to set up a Google Cloud Platform service account to access BigQuery.

### Steps:

1. **Go to Google Cloud Console**
   - URL: https://console.cloud.google.com
   - Select your existing GCP project (or create a new one)

2. **Create a Service Account**
   - Left sidebar → "Service Accounts" (under APIs & Services)
   - Click "Create Service Account"
   - Name: `text-to-sql-sa` (or any name you prefer)
   - Click "Create and Continue"

3. **Grant Permissions**
   - Role: **BigQuery Admin** (or "BigQuery Data Editor" for read-only)
   - Role: **BigQuery Job User** (to run queries)
   - Click "Continue" → "Done"

4. **Create & Download JSON Key**
   - Click on the new service account
   - Go to "Keys" tab
   - Click "Add Key" → "Create new key"
   - Choose **JSON** format
   - Click "Create"
   - File will download as `[project-id]-[hash].json`

5. **Place Key in Project Root**
   - Copy the downloaded JSON file to: `text-to-sql/gcp-key.json`
   - **Important**: Keep this file in `.gitignore` (already added) — NEVER commit it

6. **Verify the Key**
   ```bash
   # You should see the file exists
   ls gcp-key.json
   # Output: gcp-key.json (exists)
   ```

---

## 🔑 Set Up Environment Variables

### Step 1: Copy `.env.example` to `.env.local`

```bash
cd text-to-sql
cp .env.example .env.local
```

### Step 2: Edit `.env.local` with Your Values

Open `.env.local` and fill in:

```bash
# Required: Your OpenAI API Key
OPENAI_API_KEY=sk-your-actual-api-key-here

# Required: Your GCP Project ID (found in Google Cloud Console)
GCP_PROJECT_ID=your-actual-gcp-project-id

# Optional: Path to GCP key (default: ./gcp-key.json)
GCP_KEY_PATH=./gcp-key.json

# Rest can use defaults, but review them
```

### Step 3: Verify No Secrets Are Exposed

```bash
# Make sure .env.local is in .gitignore
cat .gitignore | grep ".env"
# Output should show: .env, .env.local, etc.

# Verify gcp-key.json is in .gitignore
cat .gitignore | grep "gcp-key"
# Output should show: gcp-key.json
```

---

## 🐳 Install & Verify Docker

### Check Docker Installation

```bash
# Check Docker version
docker --version
# Output: Docker version 24.0.0 (or later)

# Check Docker Compose version
docker-compose --version
# Output: Docker Compose version 2.20.0 (or later)

# Verify Docker can run containers
docker run hello-world
# Output: Hello from Docker! (if successful)
```

### If Docker Is Not Installed

- **Windows**: Download [Docker Desktop](https://www.docker.com/products/docker-desktop) and run the installer
- **macOS**: Download [Docker Desktop](https://www.docker.com/products/docker-desktop) and run the installer
- **Linux**: Install via package manager:
  ```bash
  sudo apt-get install docker.io docker-compose
  sudo usermod -aG docker $USER
  ```

---

## 🚀 Verify Everything Works

### Test 1: Verify Project Structure

```bash
cd text-to-sql

# Check key files exist
ls -la docker-compose.yml .env.example .gitignore plan.md
# All files should exist

# Check directories
ls -d backend frontend
# Both should exist

# Check subdirectories
ls backend/{tools,agents,schemas,utils}
ls frontend/src/{app,components,lib,hooks}
# All should exist
```

### Test 2: Verify Git Initialization (Optional)

```bash
# Initialize Git repository (if not already done)
git init

# Check status
git status
# Should show untracked files, but NOT gcp-key.json or .env.local
# (they're in .gitignore)

# Add all (except ignored files)
git add .
git status
# Should show staged files for commit

# Create initial commit
git commit -m "Phase 0: Project structure and Docker setup"
```

### Test 3: Verify Environment Setup

```bash
# Check .env.local exists and is in .gitignore
ls -la .env.local
file .env.local
# Should exist and contain your settings

# Verify gcp-key.json is in .gitignore but not yet in repo
cat .gitignore | grep "gcp-key.json"
# Should see: gcp-key.json

# Verify gcp-key.json exists locally
ls -la gcp-key.json
# Should exist
```

### Test 4: Dry Run Docker Compose (Optional, if Docker is running)

```bash
# This only validates the docker-compose.yml syntax, doesn't start services
docker-compose config
# Should output the full compose configuration without errors

# To actually start services (backend needs requirements.txt first):
# docker-compose up --build
# (Skip this for now; we'll do it in Phase 1)
```

---

## ✅ Phase 0 Completion Checklist

- ✅ Directory structure created
- ✅ `docker-compose.yml` created
- ✅ `.env.example` created
- ✅ `.gitignore` created
- ✅ Backend `Dockerfile` created
- ✅ Frontend `Dockerfile` created
- ✅ GCP service account created
- ✅ `gcp-key.json` downloaded to project root
- ✅ `.env.local` created with required values
- ✅ Docker installed and verified
- ✅ Git initialized (optional)

---

## 🎯 Next Phase

When ready, proceed to **Phase 1: FastAPI Backend Setup**

Phase 1 will:
- Create Python virtual environment
- Generate `requirements.txt`
- Create FastAPI `main.py` with health check and CORS
- Create Pydantic models in `schemas/models.py`
- Test FastAPI locally

---

## 🆘 Troubleshooting

### Error: "Cannot find gcp-key.json"
**Solution**: Make sure the file is in the project root (where docker-compose.yml is located)

### Error: "OPENAI_API_KEY not set"
**Solution**: Check `.env.local` has `OPENAI_API_KEY=sk-...` (not empty)

### Error: "Docker not found"
**Solution**: Install Docker Desktop from https://www.docker.com/products/docker-desktop

### Error: "GCP Project ID not found"
**Solution**: Go to Google Cloud Console, top bar shows your project ID. Copy it to `.env.local`

### Git Error: "fatal: not a git repository"
**Solution**: Run `git init` in the project root

---

## 📚 Files Reference

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Orchestrates backend & frontend services |
| `.env.example` | Template for environment variables |
| `.env.local` | Actual environment variables (YOU create from .env.example) |
| `.gitignore` | Prevents secrets from being committed |
| `backend/Dockerfile` | Builds FastAPI container |
| `frontend/Dockerfile` | Builds Next.js container |
| `backend/.dockerignore` | Excludes unnecessary files from backend image |
| `frontend/.dockerignore` | Excludes unnecessary files from frontend image |
| `gcp-key.json` | GCP service account credentials (NOT committed) |
| `plan.md` | High-level project plan |

---

**Status**: ✅ Phase 0 Complete

**Ready for Phase 1**: FastAPI Backend Setup
