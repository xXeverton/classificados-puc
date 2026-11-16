"""Local route for serving stored images."""

from flask import Flask, abort, send_from_directory

from infra.storage.storage import (
    ChaveInvalidaError,
    LocalImageStorage,
)

_CACHE_CONTROL = "public, max-age=31536000, immutable"


def registrar_rota_local(app: Flask, storage: LocalImageStorage) -> None:
    """Register a non-browsable route for local image files."""

    @app.get(f"{storage.config.local_url_base}/<path:chave>")
    def servir_imagem_local(chave: str):
        try:
            path, content_type = storage.caminho_arquivo(chave)
            if not path.is_file():
                abort(404)
            response = send_from_directory(
                storage.config.local_root,
                chave,
                mimetype=content_type,
                conditional=True,
            )
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["Cache-Control"] = _CACHE_CONTROL
            return response
        except ChaveInvalidaError:
            abort(404)
        except (OSError, RuntimeError):
            abort(404)
