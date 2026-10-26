"""
Shared test setup.

Settings are pinned through environment variables, which take priority over
.env files, so the tests never use real credentials. OpenAI and BigQuery are
always replaced by fakes: the suite needs no network access and costs nothing.
"""

import os

# Must run before config.py is imported by any test module
os.environ.update(
    {
        "OPENAI_API_KEY": "sk-test-key",
        "GCP_PROJECT_ID": "test-project-123",
        "GOOGLE_APPLICATION_CREDENTIALS": "",
        "PIPELINE_MODE": "simple",
        "ENABLE_REQUEST_LOGGING": "false",
        "DEBUG": "false",
        "CREWAI_DISABLE_TELEMETRY": "true",
        "CREWAI_TRACING_ENABLED": "false",
    }
)
