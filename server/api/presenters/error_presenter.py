"""Schema for HTTP representations of expected errors."""

from pydantic import BaseModel


class ErrorSchema(BaseModel):
    """Public error response shape."""

    message: str


def apresenta_erro(message: str) -> ErrorSchema:
    """Build an explicit error response model."""
    return ErrorSchema(message=message)
