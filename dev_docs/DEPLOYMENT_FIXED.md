# Phase 5: Deployment - Docker Volume Mount Issue FIXED ✓

## Problem
After Docker containers started, the backend returned 503 errors with warnings:
```
WARNING: Settings validation failed: OPENAI_API_KEY is not set; GCP_PROJECT_ID is not set; GOOGLE_APPLICATION_CREDENTIALS is not set
```

Root cause: Incorrect Windows Docker volume mount configuration for `gcp-key.json`

### Original Issue
The `docker-compose.yml` had:
```yaml
- ${GCP_KEY_PATH:-.}/gcp-key.json:/secrets/gcp-key.json:ro
```

When `GCP_KEY_PATH` was not set, it defaulted to `.`, resulting in Docker trying to mount `./gcp-key.json` as a directory path, which failed.

## Solution Applied

### 1. Fixed docker-compose.yml Volume Mount
Changed from variable-based path to direct relative path:
```yaml
volumes:
  # Mount GCP service account key (read-only)
  # On Windows: use full path or relative path to the gcp-key.json file
  - ./gcp-key.json:/secrets/gcp-key.json:ro
```

### 2. Updated .env File
Changed `GOOGLE_APPLICATION_CREDENTIALS` to point to the container mount path:
```env
# Before: GOOGLE_APPLICATION_CREDENTIALS=gcp-key.json
# After:  GOOGLE_APPLICATION_CREDENTIALS=/secrets/gcp-key.json
```

### 3. Removed Unnecessary Variable
Removed the now-unused `GCP_KEY_PATH` variable from .env file.

## Verification Results

✅ **Backend Container Health**: 
```
Status: 200 OK
Message: Settings validated successfully
```

✅ **Frontend Container Health**:
```
Status: UP
Port: 3000
```

✅ **Chat API Test**:
```
Query: "How many orders were placed in the last 7 days?"
Response: 200 OK (4.9 seconds)
Result: {"thought_process": "...", "sql_query": "...", "chart": {...}}
```

✅ **GCP Credentials Loaded**:
- No more validation warnings in backend logs
- BigQuery queries executing successfully
- GCP project initialized correctly

## Next Steps

1. Open frontend at http://localhost:3000
2. Test query submission and visualization rendering
3. Verify all Phase 4.2 features:
   - [x] Chat interface
   - [ ] Dark mode toggle (currently hidden)
   - [ ] Favorites panel (add/remove)
   - [ ] Query history
   - [ ] SQL query collapsible panel
   - [ ] Chart visualization
4. Test error handling with invalid queries

## Docker Service Status

```
Container Name            Image                  Status    Ports
────────────────────────  ─────────────────────  ────────  ──────────────────
text-to-sql-backend       text-to-sql-backend    Healthy   0.0.0.0:8000->8000/tcp
text-to-sql-frontend      text-to-sql-frontend   Healthy   0.0.0.0:3000->3000/tcp
```

## Key Takeaway

**Windows Docker Desktop** requires careful path handling:
- Use relative paths (e.g., `./file`) for files in the build context
- Avoid variable expansion for file-level mounts (only directory mounts work reliably)
- Container paths (inside volumes) should use Linux paths (e.g., `/secrets/path`)
