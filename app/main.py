"""Ponto de entrada da aplicação Flask (camada Frameworks & Drivers)."""

from flask import Flask

from app.routes.media import registrar_rota_local
from infra.storage.storage import (
    ImageStorage,
    LocalImageStorage,
    criar_storage,
)


def create_app(image_storage: ImageStorage | None = None) -> Flask:
    """Cria e configura a instância da aplicação Flask (app factory)."""
    app = Flask(__name__)
    storage = (
        criar_storage() if image_storage is None else image_storage
    )
    app.extensions["image_storage"] = storage

    if isinstance(storage, LocalImageStorage):
        registrar_rota_local(app, storage)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    # Registre aqui os blueprints definidos em app/routes/
    # Ex.: app.register_blueprint(task_bp)

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
