"""Tests for the FastAPI endpoints, with fake pipelines in place of the real ones."""

import pytest
from fastapi.testclient import TestClient

import main
from schemas.models import ChartData

PROJECT = "test-project-123"

# TestClient is used without a "with" block, so the startup hook that builds
# the real pipelines never runs; each test installs fakes instead.
client = TestClient(main.app)


class FakePipeline:
    def __init__(self, result):
        self.result = result
        self.queries = []

    async def execute_async(self, user_query):
        self.queries.append(user_query)
        return self.result


def success_result(**extra):
    return {
        "success": True,
        "thought_process": "Found 2 categories.",
        "sql_query": "SELECT category, SUM(x) AS revenue FROM t GROUP BY 1",
        "chart": ChartData(
            chart_type="bar",
            data=[{"category": "Jeans", "revenue": 10}, {"category": "Tops", "revenue": 5}],
            x_axis_key="category",
            y_axis_key="revenue",
            title="revenue by category",
        ),
        "execution_time_ms": 1234.5,
        **extra,
    }


@pytest.fixture
def pipelines(monkeypatch):
    """Replace the app's pipelines with an empty dict for the test to fill."""
    fakes = {}
    monkeypatch.setattr(main, "pipelines", fakes)
    return fakes


# ============================================================================
# System endpoints
# ============================================================================


def test_health_is_ok_when_the_default_pipeline_exists(pipelines):
    pipelines["simple"] = FakePipeline(success_result())
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert body["default_pipeline"] == "simple"


def test_health_is_degraded_without_a_pipeline(pipelines):
    body = client.get("/health").json()
    assert body["status"] == "degraded"
    assert "failed to initialize" in body["message"]


def test_openapi_schema_and_docs_render():
    assert client.get("/openapi.json").status_code == 200
    assert client.get("/docs").status_code == 200


def test_unknown_route_uses_the_error_format():
    response = client.get("/nope")
    assert response.status_code == 404
    assert response.json() == {
        "error": "HTTPError", "message": "Not Found", "status_code": 404, "details": None,
    }


# ============================================================================
# /api/chat
# ============================================================================


@pytest.mark.parametrize(
    "payload, expected_message",
    [
        ({"user_query": ""}, "user_query: String should have at least 1 character"),
        ({"user_query": "x" * 1001}, "user_query: String should have at most 1000 characters"),
        ({"user_query": "hi", "pipeline": "bogus"}, "pipeline: Input should be 'simple' or 'crew'"),
    ],
)
def test_invalid_requests_return_readable_validation_errors(payload, expected_message):
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 422
    assert response.json()["error"] == "ValidationError"
    assert response.json()["message"] == expected_message


def test_chat_returns_the_pipeline_result(pipelines):
    pipelines["simple"] = FakePipeline(success_result())
    response = client.post("/api/chat", json={"user_query": "  Revenue by category  "})

    assert response.status_code == 200
    body = response.json()
    assert body["pipeline"] == "simple"
    assert body["chart"]["chart_type"] == "bar"
    assert body["insights"] == [] and body["follow_up_questions"] == []
    assert pipelines["simple"].queries == ["Revenue by category"]


def test_chat_can_select_the_crew_pipeline_per_request(pipelines):
    pipelines["simple"] = FakePipeline(success_result())
    pipelines["crew"] = FakePipeline(
        success_result(insights=["Jeans lead."], follow_up_questions=["And last year?"])
    )
    body = client.post("/api/chat", json={"user_query": "Revenue", "pipeline": "crew"}).json()

    assert body["pipeline"] == "crew"
    assert body["insights"] == ["Jeans lead."]
    assert body["follow_up_questions"] == ["And last year?"]
    assert pipelines["simple"].queries == []


def test_chat_is_unavailable_without_a_pipeline(pipelines, monkeypatch):
    monkeypatch.setattr(main, "validate_settings", lambda: (False, "not configured"))
    response = client.post("/api/chat", json={"user_query": "Revenue"})
    assert response.status_code == 503


def test_chat_errors_are_redacted(pipelines):
    pipelines["simple"] = FakePipeline({
        "success": False,
        "error": (
            f"Access Denied: Project {PROJECT}; caller svc@{PROJECT}.iam.gserviceaccount.com; "
            "key sk-proj-abcdef123456; see https://bigquery.googleapis.com/x"
        ),
    })
    response = client.post("/api/chat", json={"user_query": "Revenue"})

    assert response.status_code == 500
    message = response.json()["message"]
    assert PROJECT not in message
    assert "svc@" not in message
    assert "sk-proj" not in message
    assert "https://" not in message
    assert "<project>" in message and "<service-account>" in message and "<api-key>" in message
