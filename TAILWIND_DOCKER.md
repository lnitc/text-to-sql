# Tailwind CSS in Docker - Quick Reference

## Status: ✅ WORKING

Tailwind CSS styling is now properly applied in Docker containers.

## How to Build & Run

### Production Workflow
```bash
# 1. Build frontend locally (generates .next with Tailwind CSS)
cd frontend
npm run build

# 2. Go back to root and start Docker containers
cd ..
docker compose up -d

# 3. Access application
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
```

### Why Local Build?
Turbopack (Next.js 16 default builder) requires native modules (`lightningcss`) that don't compile reliably in Docker Linux environments. 

**Solution: Pre-build locally where native modules work, then copy the `.next` folder to Docker.**

## Key Files

- `frontend/tailwind.config.ts` - Specifies which files Tailwind scans for class names
- `frontend/.dockerignore` - Removed `.next` exclusion to allow copying pre-built output
- `frontend/Dockerfile` - Copies pre-built `.next` folder from host
- `frontend/next.config.ts` - Configured Turbopack with `@tailwindcss/turbopack` loader
- `frontend/app/globals.css` - Uses `@import "tailwindcss"` directive

## Verification

CSS file should contain Tailwind utilities:
```bash
# Check CSS size (should be > 20KB)
curl -s http://localhost:3000/_next/static/chunks/*.css | wc -c

# Check for Tailwind classes
curl -s http://localhost:3000/_next/static/chunks/*.css | grep -o "\.flex\|\.grid\|\.text-"
```

## Troubleshooting

### "All styling gone" after docker compose up
1. Ensure you ran `npm run build` locally first
2. Verify `.next` folder exists in `frontend/` directory
3. Rebuild Docker: `docker compose down && docker compose up -d`

### Docker build fails with "Cannot find module 'lightningcss'"
This is expected and will be caught if `.next` doesn't exist. Run local build first.

### Want to customize Tailwind?
1. Edit `frontend/tailwind.config.ts` (e.g., add custom colors)
2. Edit `frontend/app/globals.css` (e.g., add custom styles)
3. Run `npm run build` locally
4. Restart Docker: `docker compose up -d`

## Development Mode (Without Docker)

For faster local development without Docker:
```bash
cd frontend
npm run dev    # Turbopack rebuilds on file changes

# In another terminal
cd backend
python run.py  # or: uvicorn main:app --reload
```

Tailwind CSS works seamlessly with Next.js dev server and hot reloading.
