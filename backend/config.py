"""
Configuration management for Text-to-SQL backend.
Environment variables are loaded from .env.local file.
"""

from pydantic_settings import BaseSettings
from typing import Literal


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
    frontend_url: str = "http://localhost:3000"
    cors_origins: list[str] = ["http://localhost:3000", "http://frontend:3000"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["GET", "POST", "OPTIONS"]
    cors_allow_headers: list[str] = ["*"]

    # ========================================================================
    # OpenAI Configuration
    # ========================================================================
    openai_api_key: str
    openai_model: Literal["gpt-4o", "gpt-3.5-turbo", "gpt-4-turbo"] = "gpt-3.5-turbo"
    openai_temperature: float = 0.7
    openai_max_tokens: int = 2000
    openai_monthly_budget: float = 15.0

    # ========================================================================
    # Google Cloud Configuration
    # ========================================================================
    gcp_project_id: str
    google_application_credentials: str  # Path to GCP service account JSON
    bq_dataset_project: str = "bigquery-public-data"
    bq_dataset_id: str = "thelook_ecommerce"
    bq_query_timeout_seconds: int = 30
    bq_max_results_rows: int = 1000

    # ========================================================================
    # Logging Configuration
    # ========================================================================
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    enable_request_logging: bool = True

    # ========================================================================
    # Caching Configuration
    # ========================================================================
    cache_enabled: bool = True
    cache_ttl_seconds: int = 1800  # 30 minutes
    cache_max_results: int = 10

    class Config:
        """Pydantic configuration."""
        env_file = ".env.local"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables


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

    if not settings.gcp_project_id:
        errors.append("GCP_PROJECT_ID is not set")

    if not settings.google_application_credentials:
        errors.append("GOOGLE_APPLICATION_CREDENTIALS is not set")

    if not settings.openai_api_key.startswith("sk-"):
        errors.append("OPENAI_API_KEY does not appear to be valid (should start with 'sk-')")

    # Check file existence
    import os
    if settings.google_application_credentials:
        if not os.path.exists(settings.google_application_credentials):
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
