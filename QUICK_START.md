# 🚀 Phase 0 Quick Start Guide

**Status**: ✅ PHASE 0 COMPLETE  
**Time**: ~30 minutes (automated + manual steps)  
**Next**: Phase 1 - FastAPI Backend Setup

---

## What Was Done Automatically ✅

```
✅ Created directory structure (backend, frontend with all subdirectories)
✅ Created docker-compose.yml (service orchestration)
✅ Created .env.example (environment template)
✅ Created .gitignore (secret protection)
✅ Created Dockerfiles for backend (FastAPI) and frontend (Next.js)
✅ Created project documentation (plan.md, README files)
✅ Initialized Git repository and created initial commit
```

---

## What You Need to Do (Manual) ⚠️

### Step 1: Create GCP Service Account (15 min)

1. Open: https://console.cloud.google.com
2. Make sure you're in your existing project (top-left dropdown)
3. Left sidebar → APIs & Services → Service Accounts
4. Click "Create Service Account"
   - Service account name: `text-to-sql-sa`
   - Click "Create and Continue"
5. Grant Role:
   - Search for "BigQuery Admin" → Select it
   - Click "Continue" → "Done"
6. Back on Service Accounts list, click on `text-to-sql-sa`
7. Go to "Keys" tab
8. "Add Key" → "Create new key"
   - Format: JSON
   - Click "Create"
9. A JSON file will download (e.g., `your-project-12345-abc123.json`)
10. **Move this file to project root and rename to `gcp-key.json`**
    ```bash
    mv Downloads/your-project-*.json c:\github_projects\data_proj\text-to-sql\gcp-key.json
    ```

### Step 2: Get OpenAI API Key (5 min)

1. Open: https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key (looks like: `sk-proj-abc123...`)
4. **Keep this safe** - you'll use it next

### Step 3: Set Up Environment Variables (5 min)

```bash
cd c:\github_projects\data_proj\text-to-sql

# Copy the template
cp .env.example .env.local

# Edit .env.local and fill in these three lines:
# OPENAI_API_KEY=sk-your-actual-key-here
# GCP_PROJECT_ID=your-gcp-project-id
# GCP_KEY_PATH=./gcp-key.json
```

**On Windows**, you can edit with any text editor:
```bash
notepad .env.local
```

Fill in:
```
OPENAI_API_KEY=sk-proj-your-key-here
GCP_PROJECT_ID=your-project-id
GCP_KEY_PATH=./gcp-key.json
```

### Step 4: Verify Everything (5 min)

```bash
cd c:\github_projects\data_proj\text-to-sql

# Check files exist
ls gcp-key.json .env.local
# Both should exist

# Check Docker
docker --version
docker-compose --version
# Both should show version numbers

# Check git
git log --oneline
# Should show: 0f5e6e6 Phase 0: Project structure and Docker setup
```

---

## 📁 Project Structure (What Exists Now)

```
text-to-sql/
├── .git/                       ← Git repository
├── docker-compose.yml          ← Service orchestration ✅
├── .env.example                ← Template (safe, no secrets) ✅
├── .env.local                  ← Your values (in .gitignore) ⚠️ YOU MUST CREATE
├── .gitignore                  ← Secret protection ✅
├── plan.md                     ← Full project plan ✅
├── PHASE_0_README.md           ← Detailed instructions ✅
├── PHASE_0_COMPLETION.md       ← Detailed summary ✅
├── gcp-key.json                ← GCP credentials (in .gitignore) ⚠️ YOU MUST DOWNLOAD
│
├── backend/
│   ├── Dockerfile              ← FastAPI container ✅
│   ├── .dockerignore           ← Image optimization ✅
│   ├── tools/                  ← Empty, filled in Phase 2
│   ├── agents/                 ← Empty, filled in Phase 2
│   ├── schemas/                ← Empty, filled in Phase 1
│   └── utils/                  ← Empty, filled in Phase 1
│
└── frontend/
    ├── Dockerfile              ← Next.js container ✅
    ├── .dockerignore           ← Image optimization ✅
    ├── public/                 ← Empty, filled later
    └── src/
        ├── app/                ← Empty, filled in Phase 3
        ├── components/         ← Empty, filled in Phase 4
        ├── lib/                ← Empty, filled in Phase 3
        └── hooks/              ← Empty, filled in Phase 4
```

---

## 🎯 Success Criteria

✅ You'll know Phase 0 is done when you have:

- [ ] `gcp-key.json` exists in project root
- [ ] `.env.local` exists and is filled with your keys
- [ ] `docker --version` shows Docker is installed
- [ ] `git log` shows at least one commit
- [ ] `cat .gitignore` shows secret files are protected

---

## 💡 Key Points

### What's Safe to Commit to Git
- `plan.md`
- `docker-compose.yml`
- `.env.example`
- `.gitignore`
- Dockerfiles
- Source code (when added)

### What's NOT Safe (Already in .gitignore)
- `.env.local` (your API keys)
- `gcp-key.json` (GCP credentials)
- `venv/`, `node_modules/` (dependencies)
- `.next/`, `__pycache__/` (build artifacts)

### Docker Strategy for Local Development
- Both services run in containers on your machine
- Code is mounted as volumes (changes auto-reload)
- Services communicate via internal Docker network
- No cloud costs for local development

---

## 🚀 Ready for Phase 1?

Once you have:
1. ✅ `gcp-key.json` downloaded to project root
2. ✅ `.env.local` created with your API keys
3. ✅ Docker installed and verified

You can proceed to **Phase 1: FastAPI Backend Setup**

In Phase 1, we'll:
- Create Python virtual environment
- Generate `requirements.txt` (Python dependencies)
- Create FastAPI `main.py` with health check endpoint
- Define Pydantic models
- Test locally before Docker

---

## 📞 Troubleshooting

### "Where do I find my GCP Project ID?"
**Answer**: Google Cloud Console, top bar (right of "Google Cloud")

### "How do I find OpenAI API key?"
**Answer**: https://platform.openai.com/api-keys (must be logged in)

### "Docker not found"
**Answer**: Download Docker Desktop: https://www.docker.com/products/docker-desktop

### ".env.local won't open in my editor"
**Answer**: Use `notepad .env.local` or any text editor (right-click → Open With)

### "gcp-key.json location wrong"
**Answer**: Must be in `c:\github_projects\data_proj\text-to-sql\` (same folder as docker-compose.yml)

---

## 📚 Documentation Files

| File | When to Read |
|------|---|
| `plan.md` | For full project overview and architecture |
| `PHASE_0_README.md` | For detailed Phase 0 instructions |
| `PHASE_0_COMPLETION.md` | For setup summary and what's next |
| This file | For quick start checklist |

---

**Status**: ✅ PHASE 0 AUTOMATED SETUP COMPLETE

**Next Step**: Complete the 4 manual steps above, then start **Phase 1**

