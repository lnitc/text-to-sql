"""
Configuration management for Text-to-SQL backend.
Environment variables are loaded from the process environment first, then from
.env / .env.local (project root or backend/), so the app works both in Docker
and when started locally from the backend/ directory.
"""

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # ========================================================================
    # FastAPI Configuration
    # ========================================================================
    app_name: str = "Text-to-SQL Agentic Data Analyst"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: Literal["development", "staging", "production"] = "development"
    backend_port: int = 8000

    # ========================================================================
    # CORS Configuration (for Next.js frontend)
    # ========================================================================
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://frontend:3000",
    ]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["GET", "POST", "OPTIONS"]
    cors_allow_headers: list[str] = ["*"]

    # ========================================================================
    # Pipeline Configuration
    # ========================================================================
    # "simple": one LLM call per question (agents/simplified_pipeline.py)
    # "crew": CrewAI multi-agent flow with planner, SQL developer and analyst
    #         agents (agents/data_crew.py) - slower, but adds written insights
    # Requests may override this per call via ChatRequest.pipeline.
    pipeline_mode: Literal["simple", "crew"] = "simple"

    # ========================================================================
    # OpenAI Configuration
    # ========================================================================
    # Required values default to "" so the API can start in a "degraded" state
    # and report what is missing via /health instead of crashing on import.
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_max_tokens: int = 2000

    # ========================================================================
    # Google Cloud Configuration
    # ========================================================================
    gcp_project_id: str = ""
    google_application_credentials: str = ""  # Path to GCP service account JSON
    bq_query_timeout_seconds: int = 30
    bq_max_results_rows: int = 1000
    # Hard cap on bytes a single query may scan (cost guard). 10 GB by default;
    # every thelook_ecommerce table is far smaller than this.
    bq_max_bytes_billed: int = 10 * 1024**3

    # ========================================================================
    # Logging Configuration
    # ========================================================================
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    enable_request_logging: bool = True

    model_config = SettingsConfigDict(
        # Later files take priority; missing files are ignored. .env is the
        # file Docker Compose reads, so local runs share the same settings.
        env_file=(
            PROJECT_ROOT / ".env",
            PROJECT_ROOT / ".env.local",
            BACKEND_DIR / ".env",
            BACKEND_DIR / ".env.local",
        ),
        case_sensitive=False,
        extra="ignore",  # Ignore extra environment variables
    )

    def resolved_credentials_path(self) -> str | None:
        """
        Locate the GCP service account key file.

        Relative paths are resolved against the project root. If the configured
        path does not exist (e.g. the Docker path /secrets/gcp-key.json when
        running locally), fall back to <project root>/gcp-key.json.

        Returns:
            Absolute path to an existing key file, or None if none was found
        """
        candidates = []
        if self.google_application_credentials:
            path = Path(self.google_application_credentials)
            candidates.append(path if path.is_absolute() else PROJECT_ROOT / path)
        candidates.append(PROJECT_ROOT / "gcp-key.json")

        for candidate in candidates:
            if candidate.is_file():
                return str(candidate)
        return None


# Create global settings instance
settings = Settings()


def validate_settings() -> tuple[bool, str]:
    """
    Validate that all required settings are properly configured.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    errors = []

    # Check required fields
    if not settings.openai_api_key:
        errors.append("OPENAI_API_KEY is not set")
    elif not settings.openai_api_key.startswith("sk-"):
        errors.append("OPENAI_API_KEY does not appear to be valid (should start with 'sk-')")

    if not settings.gcp_project_id:
        errors.append("GCP_PROJECT_ID is not set")

    # Credentials may also come from gcloud Application Default Credentials,
    # so only complain when a key file was configured but can't be found.
    if settings.google_application_credentials and not settings.resolved_credentials_path():
        errors.append(
            f"GCP credentials file not found: {settings.google_application_credentials}"
        )

    if errors:
        return False, "; ".join(errors)

    return True, "Settings validated successfully"


# Validate settings on module load
is_valid, message = validate_settings()
if not is_valid:
    print(f"WARNING: Settings validation failed: {message}")
