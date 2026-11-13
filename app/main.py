"""Ponto de entrada da aplicação Flask (camada Frameworks & Drivers)."""

from flask import Flask

from app.storage import init_storage
from infra.storage.storage import ImageStorage


def create_app(
    image_storage: ImageStorage | None = None,
    *,
    config: dict | None = None,
) -> Flask:
    """Cria e configura a instância da aplicação Flask (app factory)."""
    app = Flask(__name__)
    app.config.update(config or {})
    init_storage(app, image_storage)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    # Registre aqui os blueprints definidos em app/routes/
    # Ex.: app.register_blueprint(task_bp)

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
