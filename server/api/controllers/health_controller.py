"""HTTP controller for the service health endpoint."""

from flask_openapi3 import OpenAPI

from server.api.presenters.health_presenter import (
    HealthViewSchema,
    apresenta_health,
)


def register_health_controller(app: OpenAPI) -> None:
    """Register the health endpoint on the API application."""

    @app.get("/health", responses={200: HealthViewSchema})
    def health() -> dict[str, str]:
        return apresenta_health().model_dump()
