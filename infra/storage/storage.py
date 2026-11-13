"""Validated image storage for local files and S3-compatible buckets."""

import importlib
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Mapping, Protocol
from uuid import uuid4

_DEFAULT_MAX_IMAGE_BYTES = 5 * 1024 * 1024
_CACHE_CONTROL = "public, max-age=31536000, immutable"
_CONTENT_TYPES = {
    "jpg": "image/jpeg",
    "png": "image/png",
    "webp": "image/webp",
}
_IMAGE_SIGNATURES = (
    (b"\xff\xd8\xff", "jpg", "image/jpeg"),
    (b"\x89PNG\r\n\x1a\n", "png", "image/png"),
)
_NAMESPACE_PATTERN = re.compile(r"[a-z0-9_-]+")
_KEY_PATTERN = re.compile(
    r"([a-z0-9_-]+)/([0-9a-f]{32})\.(jpg|png|webp)"
)
_PROJECT_ROOT = Path(__file__).resolve().parents[2]


class ImagemInvalidaError(ValueError):
    """Raised when an image is not allowed or exceeds its size limit."""


class ChaveInvalidaError(ValueError):
    """Raised when a storage key or namespace has an invalid format."""


class StorageIndisponivelError(RuntimeError):
    """Raised when a configured storage provider cannot be reached."""


class ConfiguracaoStorageError(ValueError):
    """Raised when storage configuration is missing or invalid."""


@dataclass(frozen=True)
class ImagemArmazenada:
    """Metadata for a successfully stored immutable image."""

    chave: str
    url: str
    content_type: str
    tamanho: int


@dataclass(frozen=True)
class ConfiguracaoStorage:
    """Validated settings shared by local and S3-compatible providers."""

    provider: str = "local"
    max_image_bytes: int = _DEFAULT_MAX_IMAGE_BYTES
    local_root: Path = _PROJECT_ROOT / "media"
    local_url_base: str = "/media"
    s3_bucket: str | None = None
    s3_region: str | None = None
    s3_endpoint_url: str | None = None
    s3_access_key_id: str | None = None
    s3_secret_access_key: str | None = None
    s3_public_base_url: str | None = None
    s3_presign_expires_seconds: int = 3600
    s3_key_prefix: str = ""

    @classmethod
    def from_environment(
        cls, environ: Mapping[str, str] | None = None
    ) -> "ConfiguracaoStorage":
        """Read and validate storage settings from environment variables."""
        values = os.environ if environ is None else environ
        provider = values.get("STORAGE_PROVIDER", "local")
        if provider not in ("local", "s3"):
            raise ConfiguracaoStorageError(
                "STORAGE_PROVIDER deve ser 'local' ou 's3'."
            )

        max_bytes = _read_positive_integer(
            values, "STORAGE_MAX_IMAGE_BYTES", _DEFAULT_MAX_IMAGE_BYTES
        )
        expires = _read_positive_integer(
            values, "STORAGE_S3_PRESIGN_EXPIRES_SECONDS", 3600
        )
        root_setting = values.get("STORAGE_LOCAL_ROOT", "media")
        local_root = Path(root_setting)
        if not local_root.is_absolute():
            local_root = _PROJECT_ROOT / local_root

        local_url_base = values.get("STORAGE_LOCAL_URL_BASE", "/media").rstrip(
            "/"
        )
        if (
            not local_url_base.startswith("/")
            or "?" in local_url_base
            or "#" in local_url_base
            or ".." in local_url_base.split("/")
        ):
            raise ConfiguracaoStorageError(
                "STORAGE_LOCAL_URL_BASE deve ser um caminho local absoluto."
            )

        access_key = values.get("STORAGE_S3_ACCESS_KEY_ID") or None
        secret_key = values.get("STORAGE_S3_SECRET_ACCESS_KEY") or None
        if bool(access_key) != bool(secret_key):
            raise ConfiguracaoStorageError(
                "STORAGE_S3_ACCESS_KEY_ID e "
                "STORAGE_S3_SECRET_ACCESS_KEY devem ser configuradas juntas."
            )

        bucket = values.get("STORAGE_S3_BUCKET") or None
        if provider == "s3" and not bucket:
            raise ConfiguracaoStorageError(
                "STORAGE_S3_BUCKET é obrigatória quando STORAGE_PROVIDER=s3."
            )

        prefix = values.get("STORAGE_S3_KEY_PREFIX", "").strip("/")
        if prefix and any(
            not _NAMESPACE_PATTERN.fullmatch(part)
            for part in prefix.split("/")
        ):
            raise ConfiguracaoStorageError(
                "STORAGE_S3_KEY_PREFIX contém caracteres inválidos."
            )

        return cls(
            provider=provider,
            max_image_bytes=max_bytes,
            local_root=local_root,
            local_url_base=local_url_base,
            s3_bucket=bucket,
            s3_region=values.get("STORAGE_S3_REGION") or None,
            s3_endpoint_url=values.get("STORAGE_S3_ENDPOINT_URL") or None,
            s3_access_key_id=access_key,
            s3_secret_access_key=secret_key,
            s3_public_base_url=(
                values.get("STORAGE_S3_PUBLIC_BASE_URL", "").rstrip("/")
                or None
            ),
            s3_presign_expires_seconds=expires,
            s3_key_prefix=prefix,
        )


class ImageStorage(Protocol):
    """Common operations exposed by every image storage provider."""

    @property
    def config(self) -> ConfiguracaoStorage:
        """Return the validated configuration used by this provider."""

    def salvar_imagem(
        self, dados: bytes | BinaryIO, *, namespace: str = "anuncios"
    ) -> ImagemArmazenada:
        """Validate and store an image under a generated key."""

    def obter_url(self, chave: str) -> str:
        """Build an access URL from a validated key."""

    def remover(self, chave: str) -> None:
        """Remove an image; removing a missing key is a no-op."""


def _read_positive_integer(
    environ: Mapping[str, str], name: str, default: int
) -> int:
    value = environ.get(name)
    if value is None:
        return default
    try:
        parsed = int(value)
    except ValueError as error:
        raise ConfiguracaoStorageError(
            f"{name} deve ser um número inteiro positivo."
        ) from error
    if parsed < 1:
        raise ConfiguracaoStorageError(
            f"{name} deve ser um número inteiro positivo."
        )
    return parsed


def _validate_namespace(namespace: str) -> None:
    if not isinstance(namespace, str) or not _NAMESPACE_PATTERN.fullmatch(
        namespace
    ):
        raise ChaveInvalidaError("Namespace inválido.")


def _validate_key(chave: str) -> str:
    if not isinstance(chave, str):
        raise ChaveInvalidaError("Chave de armazenamento inválida.")
    match = _KEY_PATTERN.fullmatch(chave)
    if match is None:
        raise ChaveInvalidaError("Chave de armazenamento inválida.")
    return match.group(3)


def _read_image_data(
    dados: bytes | BinaryIO, max_image_bytes: int
) -> bytes:
    if isinstance(dados, bytes):
        content = dados[: max_image_bytes + 1]
    elif hasattr(dados, "read"):
        content = dados.read(max_image_bytes + 1)
        if not isinstance(content, bytes):
            raise ImagemInvalidaError(
                "O conteúdo da imagem deve ser binário."
            )
    else:
        raise ImagemInvalidaError("O conteúdo da imagem deve ser binário.")

    if len(content) > max_image_bytes:
        raise ImagemInvalidaError(
            "A imagem excede o tamanho máximo permitido."
        )
    if not content:
        raise ImagemInvalidaError("A imagem está vazia.")
    return content


def _detect_image_type(content: bytes) -> tuple[str, str]:
    for signature, extension, content_type in _IMAGE_SIGNATURES:
        if content.startswith(signature):
            return extension, content_type
    if (
        len(content) >= 12
        and content[:4] == b"RIFF"
        and content[8:12] == b"WEBP"
    ):
        return "webp", "image/webp"
    raise ImagemInvalidaError(
        "Formato de imagem não permitido; use JPEG, PNG ou WebP."
    )


def _new_key(namespace: str, extension: str) -> str:
    _validate_namespace(namespace)
    return f"{namespace}/{uuid4().hex}.{extension}"


@dataclass
class LocalImageStorage:
    """Store validated images atomically on the local filesystem."""

    config: ConfiguracaoStorage

    def salvar_imagem(
        self, dados: bytes | BinaryIO, *, namespace: str = "anuncios"
    ) -> ImagemArmazenada:
        content = _read_image_data(dados, self.config.max_image_bytes)
        extension, content_type = _detect_image_type(content)
        chave = _new_key(namespace, extension)
        path = self._path_for_key(chave)
        try:
            path = self._path_for_key(chave)
            path.parent.mkdir(parents=True, exist_ok=True)
            path = self._path_for_key(chave)
            temporary_name = None
            try:
                with tempfile.NamedTemporaryFile(
                    mode="wb", dir=path.parent, delete=False
                ) as temporary_file:
                    temporary_name = temporary_file.name
                    temporary_file.write(content)
                os.replace(temporary_name, path)
            finally:
                if temporary_name and os.path.exists(temporary_name):
                    os.unlink(temporary_name)
        except ChaveInvalidaError:
            raise
        except (OSError, RuntimeError):
            raise StorageIndisponivelError(
                "Não foi possível salvar a imagem no armazenamento local."
            ) from None
        return ImagemArmazenada(
            chave=chave,
            url=self.obter_url(chave),
            content_type=content_type,
            tamanho=len(content),
        )

    def obter_url(self, chave: str) -> str:
        _validate_key(chave)
        return f"{self.config.local_url_base}/{chave}"

    def remover(self, chave: str) -> None:
        try:
            path = self._path_for_key(chave)
            path.unlink(missing_ok=True)
        except ChaveInvalidaError:
            raise
        except (OSError, RuntimeError):
            raise StorageIndisponivelError(
                "Não foi possível remover a imagem do armazenamento local."
            ) from None

    def _path_for_key(self, chave: str) -> Path:
        _validate_key(chave)
        root = self.config.local_root.resolve()
        path = (root / chave).resolve()
        if not path.is_relative_to(root):
            raise ChaveInvalidaError("Chave de armazenamento inválida.")
        return path

    def _content_type_for_key(self, chave: str) -> str:
        extension = _validate_key(chave)
        return _CONTENT_TYPES[extension]

    def caminho_arquivo(self, chave: str) -> tuple[Path, str]:
        """Return a validated local path and its detected content type."""
        return self._path_for_key(chave), self._content_type_for_key(chave)


@dataclass
class S3ImageStorage:
    """Store images in an S3-compatible bucket."""

    config: ConfiguracaoStorage
    client: object
    client_error_types: tuple[type[BaseException], ...]

    def _bucket_key(self, chave: str) -> str:
        _validate_key(chave)
        if self.config.s3_key_prefix:
            return f"{self.config.s3_key_prefix}/{chave}"
        return chave

    def salvar_imagem(
        self, dados: bytes | BinaryIO, *, namespace: str = "anuncios"
    ) -> ImagemArmazenada:
        content = _read_image_data(dados, self.config.max_image_bytes)
        extension, content_type = _detect_image_type(content)
        chave = _new_key(namespace, extension)
        try:
            self.client.put_object(
                Bucket=self.config.s3_bucket,
                Key=self._bucket_key(chave),
                Body=content,
                ContentType=content_type,
                CacheControl=_CACHE_CONTROL,
            )
        except self.client_error_types:
            raise StorageIndisponivelError(
                "Não foi possível salvar a imagem no bucket."
            ) from None
        return ImagemArmazenada(
            chave=chave,
            url=self.obter_url(chave),
            content_type=content_type,
            tamanho=len(content),
        )

    def obter_url(self, chave: str) -> str:
        key = self._bucket_key(chave)
        if self.config.s3_public_base_url:
            return f"{self.config.s3_public_base_url}/{key}"
        try:
            return self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.config.s3_bucket, "Key": key},
                ExpiresIn=self.config.s3_presign_expires_seconds,
            )
        except self.client_error_types:
            raise StorageIndisponivelError(
                "Não foi possível gerar uma URL para a imagem."
            ) from None

    def remover(self, chave: str) -> None:
        key = self._bucket_key(chave)
        try:
            self.client.delete_object(
                Bucket=self.config.s3_bucket,
                Key=key,
            )
        except self.client_error_types:
            raise StorageIndisponivelError(
                "Não foi possível remover a imagem do bucket."
            ) from None


def _create_s3_storage(config: ConfiguracaoStorage) -> S3ImageStorage:
    try:
        boto3 = importlib.import_module("boto3")
        botocore_exceptions = importlib.import_module("botocore.exceptions")
    except ImportError as error:
        raise ConfiguracaoStorageError(
            "O provedor s3 requer a dependência boto3."
        ) from error

    client_options = {}
    if config.s3_region:
        client_options["region_name"] = config.s3_region
    if config.s3_endpoint_url:
        client_options["endpoint_url"] = config.s3_endpoint_url
    if config.s3_access_key_id:
        client_options["aws_access_key_id"] = config.s3_access_key_id
        client_options["aws_secret_access_key"] = config.s3_secret_access_key
    try:
        client = boto3.client("s3", **client_options)
    except (botocore_exceptions.BotoCoreError, ValueError):
        raise StorageIndisponivelError(
            "Não foi possível inicializar o cliente do bucket."
        ) from None
    return S3ImageStorage(
        config=config,
        client=client,
        client_error_types=(
            botocore_exceptions.BotoCoreError,
            botocore_exceptions.ClientError,
        ),
    )


def criar_storage(
    config: ConfiguracaoStorage | None = None,
    *,
    s3_client: object | None = None,
    s3_error_types: tuple[type[BaseException], ...] | None = None,
) -> ImageStorage:
    """Create the configured provider, loading boto3 only for S3."""
    settings = config or ConfiguracaoStorage.from_environment()
    if settings.provider == "local":
        return LocalImageStorage(settings)
    if settings.provider == "s3":
        if s3_client is not None:
            if not s3_error_types:
                raise ConfiguracaoStorageError(
                    "s3_error_types é obrigatório ao injetar um cliente S3."
                )
            return S3ImageStorage(settings, s3_client, s3_error_types)
        return _create_s3_storage(settings)
    raise ConfiguracaoStorageError("STORAGE_PROVIDER inválido.")
