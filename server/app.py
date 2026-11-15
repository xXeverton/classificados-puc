"""Application entry point and dependency composition root."""

import os
from collections.abc import Mapping

from flask_cors import CORS
from flask_openapi3 import Info, OpenAPI

from server.api.controllers.health_controller import (
    register_health_controller,
)
from server.infra.db.database import (
    create_database_engine,
    create_session_factory,
    initialize_database,
)
from server.infra.gateways.usuario_repository_sqlalchemy import (
    UsuarioRepositorySQLAlchemy,
)


def create_app(config: Mapping[str, object] | None = None) -> OpenAPI:
    """Create the API and wire its infrastructure dependencies."""
    app = OpenAPI(
        __name__,
        info=Info(
            title="Classificados PUC API",
            version="1.0.0",
            description=(
                "API da plataforma de classificados da comunidade PUC."
            ),
        ),
    )
    app.config.from_mapping(
        DATABASE_URL=os.environ.get("DATABASE_URL"),
        CORS_ORIGINS=[
            origin.strip()
            for origin in os.environ.get("CORS_ORIGINS", "").split(",")
            if origin.strip()
        ],
    )
    if config is not None:
        app.config.update(config)

    engine = create_database_engine(app.config["DATABASE_URL"])
    initialize_database(engine)
    session_factory = create_session_factory(engine)
    app.extensions["database_engine"] = engine
    app.extensions["session_factory"] = session_factory
    app.extensions["usuario_repository"] = UsuarioRepositorySQLAlchemy(
        session_factory
    )

    cors_origins = app.config["CORS_ORIGINS"]
    if cors_origins:
        CORS(app, origins=cors_origins)

    register_health_controller(app)
    return app


if __name__ == "__main__":
    create_app().run(debug=True)
