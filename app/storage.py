"""Flask initialization adapter for image storage."""

import os

from flask import Flask

from app.routes.media import registrar_rota_local
from infra.storage.storage import (
    ConfiguracaoStorage,
    ImageStorage,
    LocalImageStorage,
    criar_storage,
)

_STORAGE_KEYS = (
    "STORAGE_PROVIDER",
    "STORAGE_MAX_IMAGE_BYTES",
    "STORAGE_LOCAL_ROOT",
    "STORAGE_LOCAL_URL_BASE",
    "STORAGE_S3_BUCKET",
    "STORAGE_S3_REGION",
    "STORAGE_S3_ENDPOINT_URL",
    "STORAGE_S3_ACCESS_KEY_ID",
    "STORAGE_S3_SECRET_ACCESS_KEY",
    "STORAGE_S3_PUBLIC_BASE_URL",
    "STORAGE_S3_PRESIGN_EXPIRES_SECONDS",
    "STORAGE_S3_KEY_PREFIX",
)


def _storage_config(app: Flask) -> ConfiguracaoStorage:
    values = {
        key: os.environ[key]
        for key in _STORAGE_KEYS
        if key in os.environ
    }
    values.update(
        {
            key: str(app.config[key])
            for key in _STORAGE_KEYS
            if app.config.get(key) is not None
        }
    )
    return ConfiguracaoStorage.from_environment(values)


def init_storage(
    app: Flask, image_storage: ImageStorage | None = None
) -> ImageStorage:
    """Create, expose, and register routes for the configured storage."""
    storage = (
        criar_storage(_storage_config(app))
        if image_storage is None
        else image_storage
    )
    app.extensions["image_storage"] = storage
    app.config["STORAGE_PROVIDER"] = storage.config.provider
    app.config["STORAGE_MAX_IMAGE_BYTES"] = (
        storage.config.max_image_bytes
    )
    app.config["STORAGE_LOCAL_ROOT"] = storage.config.local_root
    app.config["STORAGE_LOCAL_URL_BASE"] = (
        storage.config.local_url_base
    )

    if isinstance(storage, LocalImageStorage):
        registrar_rota_local(app, storage)
    return storage
