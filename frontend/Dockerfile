# ============================================================================
# FRONTEND DOCKERFILE - Next.js 16 with Node.js 18
# Multi-stage build: Builder stage + Runtime stage (production optimization)
# ============================================================================

# ============================================================================
# STAGE 1: BUILDER
# ============================================================================
# Install dependencies and build Next.js application
FROM node:18-alpine AS builder

LABEL stage=builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
# --ci: Use npm ci instead of npm install (faster, more reliable in Docker)
RUN npm ci

# Copy source code
COPY . .

# Build Next.js application
# This generates .next folder with optimized production build
RUN npm run build

# ============================================================================
# STAGE 2: RUNTIME
# ============================================================================
# Lightweight runtime image with only production dependencies
FROM node:18-alpine

LABEL maintainer="Text-to-SQL Project"
LABEL description="Next.js 16 frontend for Text-to-SQL Agentic Data Analyst"

WORKDIR /app

# ============================================================================
# Runtime Dependencies
# ============================================================================
# Install only production dependencies
COPY package*.json ./
RUN npm ci --only=production

# ============================================================================
# Application Files from Builder
# ============================================================================
# Copy the built Next.js application from builder stage
COPY --from=builder /app/.next ./.next

# Copy public assets
COPY public ./public

# ============================================================================
# Runtime Configuration
# ============================================================================
# Expose port (matches Next.js default)
EXPOSE 3000

# ============================================================================
# Health Check
# ============================================================================
# Docker will check if the service is healthy by calling http://localhost:3000
# Interval: Check every 30 seconds
# Timeout: If check takes >10s, mark as unhealthy
# Start Period: Give 10s for Next.js to start before first check
# Retries: Mark as unhealthy after 3 consecutive failures
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:3000 || exit 1

# ============================================================================
# Entrypoint
# ============================================================================
# Start Next.js in production mode
# npm start: Runs the built Next.js application
CMD ["npm", "start"]

# ============================================================================
# Notes:
# ============================================================================
# - MULTI-STAGE BUILD:
#   Stage 1 (builder): node:18-alpine, installs deps, builds app (~900MB)
#   Stage 2 (runtime): node:18-alpine, only production deps (~150MB final image)
#   Final image size: ~150-200MB (vs ~900MB without multi-stage)
#
# - BASE IMAGE: node:18-alpine (~170MB)
#   Alpine is minimal (~5MB base), 18.x is stable LTS for Node.js
#
# - NPM CI vs NPM INSTALL:
#   npm ci (clean install) is preferred in Docker
#   Ensures exact versions from package-lock.json
#
# - HEALTH CHECK:
#   Frontend serves on port 3000
#   wget is pre-installed in Alpine, checks HTTP response
#   Used by docker-compose to coordinate service startup
#
# - ENVIRONMENT VARIABLES:
#   NEXT_PUBLIC_API_URL: injected at runtime by docker-compose
#   NODE_ENV=production: automatically set by Next.js on npm start
#
# - LAYER CACHING:
#   package*.json copied first so Docker caches npm install
#   if source code changes but dependencies don't
#
# - PRODUCTION OPTIMIZATION:
#   npm ci --only=production: removes dev dependencies
#   npm start: Next.js starts in optimized server mode
#   No source maps, minified bundles, SSR enabled
# ============================================================================
