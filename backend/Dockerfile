# ============================================================================
# BACKEND DOCKERFILE - FastAPI + Python 3.11
# Multi-stage build for production optimization
# ============================================================================

FROM python:3.11-slim

LABEL maintainer="Text-to-SQL Project"
LABEL description="FastAPI backend for Text-to-SQL Agentic Data Analyst"

WORKDIR /app

# ============================================================================
# System Dependencies
# ============================================================================
# Install system-level dependencies required by Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ============================================================================
# Python Dependencies
# ============================================================================
# Copy requirements first for layer caching
# (requirements changes more frequently than code)
COPY requirements.txt .

# Install Python dependencies
# --no-cache-dir: reduce image size
RUN pip install --no-cache-dir -r requirements.txt

# ============================================================================
# Application Code
# ============================================================================
# Copy application source code
COPY . .

# Set Python path so imports work correctly from /app directory
ENV PYTHONPATH=/app:$PYTHONPATH

# ============================================================================
# Runtime Configuration
# ============================================================================
# Expose port (matches BACKEND_PORT in environment)
EXPOSE 8000

# ============================================================================
# Health Check
# ============================================================================
# Docker will check if the service is healthy by calling the /health endpoint
# Interval: Check every 30 seconds
# Timeout: If check takes >10s, mark as unhealthy
# Start Period: Give 5s for the service to start before first check
# Retries: Mark as unhealthy after 3 consecutive failures
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# ============================================================================
# Entrypoint
# ============================================================================
# Run via Python wrapper script that sets up sys.path correctly
# The wrapper ensures imports like 'from backend.config' work in Docker
CMD ["python", "run.py"]

# ============================================================================
# Notes:
# ============================================================================
# - BASE IMAGE: python:3.11-slim (~150MB)
#   Slim variant removes unnecessary packages, keeping image size minimal
#
# - LAYER CACHING:
#   requirements.txt is copied first so Docker can cache dependencies
#   if source code changes but requirements.txt doesn't
#
# - HEALTH CHECK:
#   /health endpoint must return 200 OK for Docker to consider service healthy
#   Used by docker-compose to coordinate service startup
#
# - ENVIRONMENT VARIABLES:
#   All sensitive configuration (OPENAI_API_KEY, GCP credentials) are
#   injected at runtime via docker-compose, not baked into the image
#
# - PRODUCTION OPTIMIZATION:
#   For production, remove --reload flag:
#   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
# ============================================================================
