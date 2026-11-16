"""Ponto de entrada da aplicação Flask (camada Frameworks & Drivers)."""

from flask import Flask

from app.routes.anuncios import registrar_rota_novo_anuncio
from app.routes.media import registrar_rota_local
from infra.storage.storage import (
    ImageStorage,
    LocalImageStorage,
    criar_storage,
)
from infra.repositories.autenticador_mock import AutenticadorMock
from use_cases.autenticacao import (
    CHAVE_EXTENSAO_AUTENTICADOR,
    Autenticador,
)


def create_app(
    image_storage: ImageStorage | None = None,
    *,
    autenticador: Autenticador | None = None,
) -> Flask:
    """Cria e configura a instância da aplicação Flask (app factory)."""
    app = Flask(__name__)
    storage = (
        criar_storage() if image_storage is None else image_storage
    )
    autenticador_ativo = (
        AutenticadorMock() if autenticador is None else autenticador
    )
    app.extensions["image_storage"] = storage
    app.extensions[CHAVE_EXTENSAO_AUTENTICADOR] = autenticador_ativo

    if isinstance(storage, LocalImageStorage):
        registrar_rota_local(app, storage)

    registrar_rota_novo_anuncio(app, autenticador_ativo)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    # Registre aqui os blueprints definidos em app/routes/
    # Ex.: app.register_blueprint(task_bp)

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
