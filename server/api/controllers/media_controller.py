"""Serve locally stored ad images."""

from flask import abort, send_from_directory
from flask_openapi3 import OpenAPI

from server.infra.storage.storage import (
    ChaveInvalidaError,
    LocalImageStorage,
)


def register_media_controller(
    app: OpenAPI, storage: LocalImageStorage
) -> None:
    def serve_image(key: str):
        try:
            path, content_type = storage.caminho_arquivo(key)
        except ChaveInvalidaError:
            abort(404)
        if not path.is_file():
            abort(404)
        response = send_from_directory(
            storage.config.local_root,
            key,
            mimetype=content_type,
            conditional=True,
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Cache-Control"] = (
            "public, max-age=31536000, immutable"
        )
        return response

    app.add_url_rule(
        f"{storage.config.local_url_base}/<path:key>",
        endpoint="serve_ad_image",
        view_func=serve_image,
        methods=["GET"],
    )
