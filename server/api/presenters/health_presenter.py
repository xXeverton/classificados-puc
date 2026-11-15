"""Response schema and presenter for the health endpoint."""

from pydantic import BaseModel


class HealthViewSchema(BaseModel):
    """Public response returned by the health endpoint."""

    status: str


def apresenta_health() -> HealthViewSchema:
    """Build the health response model."""
    return HealthViewSchema(status="ok")
