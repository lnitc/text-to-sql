"""
Main FastAPI application for Text-to-SQL Agentic Data Analyst backend.

Provides HTTP endpoints for:
- Health checks
- Chat queries (text-to-SQL conversion with CrewAI pipeline)
- OpenAPI documentation
"""

import time
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx

from backend.config import settings, validate_settings
from backend.schemas.models import (
    ChatRequest,
    AgentResponse,
    HealthResponse,
    ErrorResponse,
    ChartData,
)


# ============================================================================
# Lifespan Context Manager (FastAPI 0.93+)
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    Runs on startup and shutdown.
    """
    # Startup
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Environment: {settings.environment}")
    print(f"Debug: {settings.debug}")

    # Validate settings
    is_valid, message = validate_settings()
    if not is_valid:
        print(f"WARNING: {message}")

    yield

    # Shutdown
    print("Shutting down application...")


# ============================================================================
# FastAPI Application
# ============================================================================


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Convert natural language questions to SQL queries",
    lifespan=lifespan,
)


# ============================================================================
# CORS Middleware
# ============================================================================


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


# ============================================================================
# Middleware for Request Logging & Error Handling
# ============================================================================


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log HTTP requests and responses.
    """
    start_time = time.time()
    request_path = request.url.path
    request_method = request.method

    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000  # Convert to ms

        if settings.enable_request_logging:
            print(
                f"[{request_method}] {request_path} - "
                f"Status: {response.status_code} - "
                f"Time: {process_time:.2f}ms"
            )

        # Add processing time header
        response.headers["X-Process-Time"] = str(process_time)
        return response

    except Exception as exc:
        process_time = (time.time() - start_time) * 1000
        print(
            f"[{request_method}] {request_path} - "
            f"Error: {str(exc)} - "
            f"Time: {process_time:.2f}ms"
        )
        raise


# ============================================================================
# Error Handlers
# ============================================================================


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="HTTPError",
            message=exc.detail,
            status_code=exc.status_code,
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    print(f"Unhandled exception: {type(exc).__name__}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="InternalServerError",
            message="An unexpected error occurred",
            status_code=500,
            details=str(exc) if settings.debug else None,
        ).model_dump(),
    )


# ============================================================================
# Health Check Endpoint
# ============================================================================


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Health check endpoint",
    description="Check if the service is running and healthy",
)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    Returns service status and version information.
    """
    # Validate settings
    is_valid, message = validate_settings()
    status_value = "ok" if is_valid else "degraded"

    return HealthResponse(
        status=status_value,
        message=message,
        version=settings.app_version,
    )


# ============================================================================
# Chat Endpoint (Main Feature)
# ============================================================================


@app.post(
    "/api/chat",
    response_model=AgentResponse,
    tags=["Chat"],
    summary="Send a natural language query",
    description="Convert natural language question to SQL and execute",
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Invalid request (empty query, etc.)",
        },
        500: {
            "model": ErrorResponse,
            "description": "Internal server error (CrewAI/BigQuery failure)",
        },
    },
)
async def chat(request: ChatRequest) -> AgentResponse:
    """
    Chat endpoint - main functionality.

    Takes a natural language question and returns:
    - The SQL query that was executed
    - The results formatted for visualization
    - A thought process explaining the analysis

    Args:
        request: ChatRequest with user_query

    Returns:
        AgentResponse with thought_process, sql_query, and chart data

    Raises:
        HTTPException: If query processing fails
    """
    start_time = time.time()

    try:
        # Validate request
        user_query = request.user_query.strip()
        if not user_query:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query cannot be empty",
            )

        # TODO: Implement CrewAI pipeline
        # For now, return a mock response to validate the endpoint structure
        print(f"Processing query: {user_query}")

        # Mock response (will be replaced with actual CrewAI pipeline in Phase 2)
        mock_response = AgentResponse(
            thought_process=(
                "The user is asking a question about the dataset. "
                "In Phase 2, this will be processed by the CrewAI pipeline. "
                f"Query received: {user_query[:50]}..."
            ),
            sql_query="SELECT * FROM `bigquery-public-data.thelook_ecommerce.products` LIMIT 5",
            chart=ChartData(
                chart_type="table",
                data=[
                    {"id": 1, "name": "Product 1", "category": "Electronics"},
                    {"id": 2, "name": "Product 2", "category": "Clothing"},
                ],
                x_axis_key="id",
                y_axis_key="name",
                title="Sample Data (Mock Response)",
            ),
            execution_time_ms=(time.time() - start_time) * 1000,
        )

        return mock_response

    except HTTPException:
        raise
    except Exception as exc:
        print(f"Error processing query: {type(exc).__name__}: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(exc)}",
        )


# ============================================================================
# Root Endpoint
# ============================================================================


@app.get(
    "/",
    tags=["System"],
    summary="API information",
    description="Get API information and available endpoints",
)
async def root() -> dict[str, Any]:
    """Get API information."""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "health": "/health",
            "chat": "/api/chat",
        },
    }


# ============================================================================
# OpenAPI Configuration
# ============================================================================


def custom_openapi():
    """Customize OpenAPI schema."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = {
        "openapi": "3.0.2",
        "info": {
            "title": settings.app_name,
            "version": settings.app_version,
            "description": "Text-to-SQL Agentic Data Analyst API",
            "contact": {
                "name": "Your Name",
                "url": "https://github.com",
            },
        },
        "servers": [
            {
                "url": f"http://localhost:{settings.backend_port}",
                "description": "Local development server",
            }
        ],
        "paths": app.openapi()["paths"],
        "components": app.openapi()["components"],
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# ============================================================================
# Application Entry Point
# ============================================================================


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.backend_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
