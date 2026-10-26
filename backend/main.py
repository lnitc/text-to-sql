"""
Main FastAPI application for Text-to-SQL Agentic Data Analyst backend.

Provides HTTP endpoints:
- Health checks
- Chat queries (text-to-SQL conversion with the simplified or CrewAI
  multi-agent pipeline, selected by PIPELINE_MODE or per request)
- OpenAPI documentation
"""

import asyncio
import re
import time
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from config import settings, validate_settings
from schemas.models import (
    ChatRequest,
    AgentResponse,
    HealthResponse,
    ErrorResponse,
    ChartData,
)
from agents.simplified_pipeline import create_simplified_pipeline


# ============================================================================
# Pipeline Instances
# ============================================================================

# Pipelines by name ("simple" / "crew"). The simplified pipeline is created on
# startup. The CrewAI pipeline is created on startup only when it is the
# default (PIPELINE_MODE=crew), otherwise on first use, because importing
# CrewAI adds several seconds to startup.
pipelines: dict[str, Any] = {}
_crew_init_lock = asyncio.Lock()


_SECRET_PATTERNS = [
    (re.compile(r"[\w.+-]+@[\w-]+\.iam\.gserviceaccount\.com"), "<service-account>"),
    (re.compile(r"\bsk-[A-Za-z0-9_*-]{6,}"), "<api-key>"),
    (re.compile(r"https?://\S+"), "<url>"),
]


def redact_sensitive(text: str) -> str:
    """
    Last line of defense before error text reaches API clients: remove the
    GCP project ID, service account emails, API keys and request URLs that
    upstream libraries (BigQuery, OpenAI, CrewAI) may embed in messages.
    """
    # Patterns first: service account emails contain the project ID, and
    # replacing it first would stop the email pattern from matching
    for pattern, replacement in _SECRET_PATTERNS:
        text = pattern.sub(replacement, text)
    if settings.gcp_project_id:
        text = text.replace(settings.gcp_project_id, "<project>")
    return text


def _create_crew_pipeline():
    from agents.data_crew import create_crew_pipeline

    return create_crew_pipeline(settings.gcp_project_id)


async def get_pipeline(name: str):
    """Return the named pipeline, creating the CrewAI pipeline on first use."""
    if name in pipelines:
        return pipelines[name]
    if name == "crew" and validate_settings()[0]:
        async with _crew_init_lock:
            if "crew" not in pipelines:
                print("Initializing CrewAI multi-agent pipeline...")
                pipelines["crew"] = await asyncio.to_thread(_create_crew_pipeline)
                print("CrewAI multi-agent pipeline initialized successfully")
        return pipelines["crew"]
    return None


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
    print(f"Default pipeline: {settings.pipeline_mode}")

    # Validate settings
    is_valid, message = validate_settings()
    if not is_valid:
        print(f"WARNING: Settings validation failed: {message}")
    else:
        # Initialize pipeline
        try:
            print(f"Initializing Text-to-SQL pipeline for project: {settings.gcp_project_id}")
            pipelines["simple"] = create_simplified_pipeline(settings.gcp_project_id)
            print("Text-to-SQL pipeline initialized successfully")
        except Exception as e:
            print(f"ERROR: Failed to initialize pipeline: {str(e)}")
            import traceback
            traceback.print_exc()

        if settings.pipeline_mode == "crew":
            try:
                await get_pipeline("crew")
            except Exception as e:
                print(f"ERROR: Failed to initialize CrewAI pipeline: {str(e)}")
                import traceback
                traceback.print_exc()

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


# Registered for Starlette's base class so routing errors (404/405) use the
# same ErrorResponse shape as errors raised by our endpoints.
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="HTTPError",
            message=str(exc.detail),
            status_code=exc.status_code,
        ).model_dump(),
        headers=getattr(exc, "headers", None),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Return request validation errors (422) in the standard ErrorResponse shape."""
    messages = []
    for error in exc.errors():
        field = ".".join(str(part) for part in error.get("loc", []) if part != "body")
        messages.append(f"{field}: {error.get('msg')}" if field else str(error.get("msg")))
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error="ValidationError",
            message="; ".join(messages) or "Invalid request",
            status_code=422,
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
    # The crew pipeline may legitimately not exist yet (lazy init), so only
    # the default pipeline's absence makes the service degraded.
    if is_valid and settings.pipeline_mode not in pipelines:
        is_valid = False
        name = "CrewAI multi-agent" if settings.pipeline_mode == "crew" else "Text-to-SQL"
        message = f"{name} pipeline failed to initialize. Check the backend logs."
    status_value = "ok" if is_valid else "degraded"

    return HealthResponse(
        status=status_value,
        message=message,
        version=settings.app_version,
        default_pipeline=settings.pipeline_mode,
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

        # Resolve the pipeline (request override, else server default)
        pipeline_name = request.pipeline or settings.pipeline_mode
        try:
            pipeline = await get_pipeline(pipeline_name)
        except Exception as exc:
            print(f"[Chat] Failed to initialize {pipeline_name} pipeline: {exc}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=redact_sensitive(f"The {pipeline_name} pipeline could not be initialized: {exc}"),
            )
        if pipeline is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Text-to-SQL pipeline not initialized. Check backend configuration.",
            )

        print(f"[Chat] Processing query ({pipeline_name} pipeline): {user_query}")

        # Execute pipeline asynchronously
        result = await pipeline.execute_async(user_query)

        if not result.get("success"):
            error_msg = result.get('error', 'Unknown error')
            
            # Log specific error types for better error categorization
            if "model" in error_msg.lower() and "not found" in error_msg.lower():
                print(f"[Chat] Model not found error: {error_msg}")
            elif "authentication" in error_msg.lower():
                print(f"[Chat] Authentication error: {error_msg}")
            elif "rate" in error_msg.lower():
                print(f"[Chat] Rate limit error: {error_msg}")
            elif "sql" in error_msg.lower():
                print(f"[Chat] SQL execution error: {error_msg}")
            else:
                print(f"[Chat] Pipeline error: {error_msg}")
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=redact_sensitive(error_msg),
            )

        # Build response
        response = AgentResponse(
            thought_process=result.get("thought_process", "Analysis complete."),
            sql_query=result.get("sql_query", ""),
            chart=result.get("chart", ChartData(
                chart_type="table",
                data=[],
                x_axis_key="x",
                y_axis_key="y",
                title="Results"
            )),
            execution_time_ms=result.get("execution_time_ms", 0),
            pipeline=pipeline_name,
            insights=result.get("insights", []),
            follow_up_questions=result.get("follow_up_questions", []),
        )

        return response

    except HTTPException:
        raise
    except Exception as exc:
        print(f"Error processing query: {type(exc).__name__}: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=redact_sensitive(f"Error processing query: {str(exc)}"),
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

    # Build from the routes directly: calling app.openapi() here would recurse
    # into this function, since it replaces app.openapi below.
    app.openapi_schema = get_openapi(
        title=settings.app_name,
        version=settings.app_version,
        description="Text-to-SQL Agentic Data Analyst API",
        routes=app.routes,
        servers=[
            {
                "url": f"http://localhost:{settings.backend_port}",
                "description": "Local development server",
            }
        ],
    )
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
