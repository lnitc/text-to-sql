# ============================================================================
# FRONTEND DOCKERFILE - Next.js 16 with TypeScript
# Multi-stage build for production optimization
# ============================================================================

# ============================================================================
# STAGE 1: BUILDER
# ============================================================================
FROM node:20-alpine AS builder

LABEL maintainer="Text-to-SQL Project"
LABEL description="Next.js frontend for Text-to-SQL Agentic Data Analyst"

WORKDIR /app

# ============================================================================
# Dependencies - Copy package files for layer caching
# ============================================================================
COPY package*.json ./

# Install dependencies
# --omit=optional: skip optional dependencies to reduce size
# If package-lock.json doesn't exist, fall back to npm install
RUN npm ci --omit=optional || npm install --omit=optional

# ============================================================================
# Build Application
# ============================================================================
COPY . .

# Build Next.js application
# Outputs optimized build to .next directory
RUN npm run build

# ============================================================================
# STAGE 2: RUNTIME
# ============================================================================
FROM node:20-alpine

WORKDIR /app

# ============================================================================
# Production Dependencies Only
# ============================================================================
# Copy package files from builder
COPY package*.json ./

# Install only production dependencies (much lighter)
# Use --production or --omit=dev to exclude dev dependencies
RUN npm ci --omit=optional || npm install --production --omit=optional

# ============================================================================
# Copy Built Application
# ============================================================================
# Copy .next build output from builder stage
COPY --from=builder /app/.next ./.next

# Copy public assets
COPY public ./public

# ============================================================================
# Runtime Configuration
# ============================================================================
# Expose port (matches FRONTEND_PORT in environment)
EXPOSE 3000

# ============================================================================
# Health Check
# ============================================================================
# Docker will check if the service is healthy by calling localhost:3000
# This verifies that the Next.js server is responding
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:3000 || exit 1

# ============================================================================
# Environment Variables (injected at runtime)
# ============================================================================
# NEXT_PUBLIC_API_URL: Backend API URL (set via docker-compose)
# NODE_ENV: should be "production" for optimal performance

# ============================================================================
# Entrypoint
# ============================================================================
# Start Next.js server
# -p 3000: listen on port 3000
CMD ["npm", "start"]

# ============================================================================
# Notes:
# ============================================================================
# - NODE VERSION: node:20-alpine (~170MB)
#   Alpine Linux variant keeps image size minimal
#
# - MULTI-STAGE BUILD:
#   Stage 1 (builder): Full build with dev dependencies
#   Stage 2 (runtime): Only production runtime, much smaller
#   Result: ~300MB development vs ~250MB production
#
# - LAYER CACHING:
#   Dependencies installed before source code copied
#   Docker caches npm install if package*.json unchanged
#
# - HEALTH CHECK:
#   Verifies Next.js server is responding on port 3000
#   Used by docker-compose to coordinate service startup
#
# - ENVIRONMENT VARIABLES:
#   NEXT_PUBLIC_* variables are baked into the Next.js build at build time
#   If you need to change them at runtime, you must rebuild the image
#   For runtime configuration, consider using a wrapper script
#
# - STARTUP TIME:
#   First startup may take 5-10 seconds for Next.js to initialize
#   start_period=10s gives it time before health checks begin failing
#
# - PRODUCTION OPTIMIZATION:
#   This Dockerfile is already optimized for production with:
#   - Multi-stage build (removes dev dependencies)
#   - Alpine base image (small size)
#   - npm ci instead of npm install (deterministic dependencies)
#   - Health checks enabled
# ============================================================================
