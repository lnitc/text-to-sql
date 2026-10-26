# ============================================================================
# FRONTEND DOCKERFILE - Next.js 16 with TypeScript
# ============================================================================
# Multi-stage build:
#   1. builder: installs dependencies and runs `next build` inside the image
#   2. runner:  runs Next's minimal standalone server (no node_modules needed)
#
# Build-time settings (NEXT_PUBLIC_* values are inlined into the browser
# bundle, so they must be passed as build args, not runtime env vars):
#   NEXT_PUBLIC_API_URL      URL the *browser* uses to reach the backend
#   NEXT_PUBLIC_ENVIRONMENT  development | staging | production
# ============================================================================

# ============================================================================
# STAGE 1: BUILDER
# ============================================================================
FROM node:24-slim AS builder

LABEL maintainer="Text-to-SQL Project"
LABEL description="Next.js frontend for Text-to-SQL Agentic Data Analyst"

WORKDIR /app

# Dependencies first, for layer caching. Optional dependencies must not be
# skipped: they carry the Linux native binaries the build needs (Next's SWC
# compiler, Tailwind's oxide engine, lightningcss).
COPY package.json package-lock.json ./
RUN npm ci

COPY . .

ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ARG NEXT_PUBLIC_ENVIRONMENT=development
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL \
    NEXT_PUBLIC_ENVIRONMENT=$NEXT_PUBLIC_ENVIRONMENT \
    NEXT_STANDALONE=true \
    NEXT_TELEMETRY_DISABLED=1

RUN npm run build

# ============================================================================
# STAGE 2: RUNNER
# ============================================================================
FROM node:24-slim AS runner

WORKDIR /app

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME=0.0.0.0

# The standalone server plus the static assets it serves
COPY --from=builder --chown=node:node /app/.next/standalone ./
COPY --from=builder --chown=node:node /app/.next/static ./.next/static
COPY --from=builder --chown=node:node /app/public ./public

# Run as the image's unprivileged user
USER node

EXPOSE 3000

# The slim image has no curl/wget, so use Node's built-in fetch
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD node -e "fetch('http://127.0.0.1:3000').then(r => process.exit(r.ok ? 0 : 1)).catch(() => process.exit(1))"

CMD ["node", "server.js"]
