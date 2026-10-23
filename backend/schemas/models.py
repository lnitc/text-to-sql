"""
Pydantic models for request/response validation.
Provides strong typing and automatic OpenAPI documentation.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional


class ChatRequest(BaseModel):
    """User query request to the backend."""

    user_query: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Natural language question about the dataset",
        example="What were the top 5 product categories by revenue last month?"
    )

    @field_validator("user_query")
    @classmethod
    def validate_query_not_empty(cls, v: str) -> str:
        """Ensure query is not just whitespace."""
        if not v.strip():
            raise ValueError("Query cannot be empty or whitespace only")
        return v.strip()


class ChartData(BaseModel):
    """Structured data for chart rendering."""

    chart_type: Literal["bar", "line", "pie", "table"] = Field(
        ...,
        description="Type of chart to render"
    )

    data: list[dict] = Field(
        ...,
        description="Array of data points for the chart",
        example=[
            {"category": "Electronics", "revenue": 5000},
            {"category": "Clothing", "revenue": 3500}
        ]
    )

    x_axis_key: str = Field(
        ...,
        description="Key name for X-axis values",
        example="category"
    )

    y_axis_key: str = Field(
        ...,
        description="Key name for Y-axis values",
        example="revenue"
    )

    title: str = Field(
        ...,
        description="Chart title",
        example="Revenue by Category"
    )


class AgentResponse(BaseModel):
    """Complete response from the CrewAI pipeline."""

    thought_process: str = Field(
        ...,
        description="Brief explanation of what was found and how",
        example="The user asked for top 5 product categories by revenue..."
    )

    sql_query: str = Field(
        ...,
        description="The SQL query that was executed",
        example="SELECT category, SUM(sale_price) as revenue FROM..."
    )

    chart: ChartData = Field(
        ...,
        description="Chart data formatted for Recharts"
    )

    execution_time_ms: float = Field(
        default=0,
        ge=0,
        description="Query execution time in milliseconds"
    )


class HealthResponse(BaseModel):
    """Health check response."""

    status: Literal["ok", "degraded", "error"] = Field(
        default="ok",
        description="Service health status"
    )

    message: str = Field(
        default="Service is healthy",
        description="Status message"
    )

    version: str = Field(
        ...,
        description="API version"
    )


class ErrorResponse(BaseModel):
    """Error response format."""

    error: str = Field(
        ...,
        description="Error type"
    )

    message: str = Field(
        ...,
        description="Detailed error message"
    )

    status_code: int = Field(
        ...,
        description="HTTP status code"
    )

    details: Optional[str] = Field(
        default=None,
        description="Additional details about the error"
    )
