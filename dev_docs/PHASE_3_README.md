# Phase 3: Frontend Quick Start

## Prerequisites
- Node.js 18+ installed
- Backend running on port 8000 (see Phase 1/2)
- `.env.local` in frontend directory with `NEXT_PUBLIC_API_URL`

## Quick Start (Development)

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Start Development Server
```bash
npm run dev
```
- Frontend: http://localhost:3000
- Hot reload enabled

### 3. Start Backend (in separate terminal)
```bash
cd ..  # root directory
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

### 4. Open Browser
Navigate to http://localhost:3000

## Available Scripts

```bash
# Development
npm run dev          # Start dev server with hot reload

# Production
npm run build        # Create optimized build
npm start            # Start production server

# Code Quality
npm run lint         # Run ESLint
npm run type-check   # Run TypeScript check (if available)

# Formatting
npm run format       # Format code (if Prettier configured)
```

## Troubleshooting

### "Backend is not responding"
- Ensure backend is running on port 8000
- Check `.env.local` has correct `NEXT_PUBLIC_API_URL`
- Verify backend health: `curl http://localhost:8000/health`

### "Module not found" errors
- Run `npm install` from frontend directory
- Clear `.next/` cache: `rm -r .next` (PowerShell: `Remove-Item .next -Recurse`)
- Restart dev server

### Port 3000 already in use
- Kill existing process or change port: `npm run dev -- -p 3001`

### TypeScript errors
- Run `npm run type-check` to see all errors
- Frontend uses strict mode; all types must be correct

## Environment Variables

### Development (`.env.local`)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Docker/Production (`.env.local`)
```env
NEXT_PUBLIC_API_URL=http://backend:8000
```

## Features

- ✅ Chat interface for natural language queries
- ✅ SQL query display with copy button
- ✅ 4 chart types: bar, line, pie, table
- ✅ Real-time connection status
- ✅ Error handling and recovery
- ✅ Type-safe TypeScript
- ✅ Responsive Tailwind CSS design

## Next Phase

See Phase 4 for advanced features like query customization, export, and favorites.
