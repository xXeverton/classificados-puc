import io
import re
from types import SimpleNamespace

import pytest

from app.main import create_app
from infra.storage.storage import (
    ChaveInvalidaError,
    ConfiguracaoStorage,
    ConfiguracaoStorageError,
    ImagemInvalidaError,
    LocalImageStorage,
    S3ImageStorage,
    StorageIndisponivelError,
    criar_storage,
)

JPEG = b"\xff\xd8\xff" + b"jpeg-data"
PNG = b"\x89PNG\r\n\x1a\n" + b"png-data"
WEBP = b"RIFF\x00\x00\x00\x00WEBP" + b"webp-data"


class FakeS3Client:
    def __init__(self):
        self.put_calls = []
        self.delete_calls = []
        self.presign_calls = []
        self.error = None

    def put_object(self, **kwargs):
        self.put_calls.append(kwargs)
        if self.error:
            raise self.error

    def delete_object(self, **kwargs):
        self.delete_calls.append(kwargs)
        if self.error:
            raise self.error

    def generate_presigned_url(self, operation, **kwargs):
        self.presign_calls.append((operation, kwargs))
        if self.error:
            raise self.error
        return "https://signed.example/image?signature=fake"


class FakeS3Error(Exception):
    pass


class TrackingStream(io.BytesIO):
    def __init__(self, content):
        super().__init__(content)
        self.read_sizes = []

    def read(self, size=-1):
        self.read_sizes.append(size)
        return super().read(size)


def local_storage(tmp_path, **overrides):
    settings = ConfiguracaoStorage(
        local_root=tmp_path,
        max_image_bytes=overrides.pop("max_image_bytes", 1024),
        **overrides,
    )
    return LocalImageStorage(settings)


def s3_storage(client=None, **overrides):
    settings = ConfiguracaoStorage(
        provider="s3",
        s3_bucket="test-image-bucket",
        **overrides,
    )
    return S3ImageStorage(
        settings,
        client or FakeS3Client(),
        (FakeS3Error,),
    )


@pytest.fixture
def local_app(tmp_path):
    app = create_app(
        config={
            "STORAGE_PROVIDER": "local",
            "STORAGE_LOCAL_ROOT": tmp_path,
            "STORAGE_LOCAL_URL_BASE": "/images",
        }
    )
    app.config["TESTING"] = True
    return app


@pytest.mark.parametrize(
    ("content", "extension", "content_type"),
    [
        (JPEG, "jpg", "image/jpeg"),
        (PNG, "png", "image/png"),
        (WEBP, "webp", "image/webp"),
    ],
)
def test_local_accepts_supported_image_signatures(
    tmp_path, content, extension, content_type
):
    result = local_storage(tmp_path).salvar_imagem(content)

    assert result.chave.endswith(f".{extension}")
    assert result.content_type == content_type


@pytest.mark.parametrize(
    "content",
    [
        b"not an image",
        b"<svg><script>alert(1)</script></svg>",
        b"GIF89a",
        b"<html>not an image</html>",
        b"%PDF-1.7",
        b"",
    ],
)
def test_local_rejects_empty_or_unsupported_content(tmp_path, content):
    with pytest.raises(ImagemInvalidaError):
        local_storage(tmp_path).salvar_imagem(content)


def test_content_type_is_derived_from_signature(tmp_path):
    class MisleadingStream(io.BytesIO):
        content_type = "image/jpeg"

    result = local_storage(tmp_path).salvar_imagem(MisleadingStream(PNG))

    assert result.content_type == "image/png"
    assert result.chave.endswith(".png")


def test_image_size_limit_and_stream_read_bound(tmp_path):
    storage = local_storage(tmp_path, max_image_bytes=len(PNG))

    accepted = storage.salvar_imagem(PNG)
    assert accepted.tamanho == len(PNG)

    stream = TrackingStream(PNG + b"x")
    with pytest.raises(ImagemInvalidaError):
        storage.salvar_imagem(stream)
    assert stream.read_sizes == [len(PNG) + 1]


def test_generated_keys_are_unique_and_do_not_use_client_filename(tmp_path):
    storage = local_storage(tmp_path)

    first = storage.salvar_imagem(JPEG)
    second = storage.salvar_imagem(JPEG)
    pattern = r"anuncios/[0-9a-f]{32}\.jpg"

    assert re.fullmatch(pattern, first.chave)
    assert re.fullmatch(pattern, second.chave)
    assert first.chave != second.chave


@pytest.mark.parametrize(
    "namespace",
    ["", "../outside", "anuncios/nested", r"anuncios\evil", "Has space"],
)
def test_invalid_namespace_is_rejected(tmp_path, namespace):
    with pytest.raises(ChaveInvalidaError):
        local_storage(tmp_path).salvar_imagem(JPEG, namespace=namespace)


@pytest.mark.parametrize(
    "key",
    [
        "",
        "../outside.jpg",
        "anuncios/../outside.jpg",
        "anuncios//abc.jpg",
        r"anuncios\abc.jpg",
        "/absolute/path.jpg",
        "anuncios/\x00.jpg",
        "anuncios/not-a-uuid.jpg",
        "anuncios/" + "a" * 32 + ".svg",
    ],
)
@pytest.mark.parametrize("operation", ["obter_url", "remover"])
def test_local_rejects_invalid_keys(tmp_path, key, operation):
    with pytest.raises(ChaveInvalidaError):
        getattr(local_storage(tmp_path), operation)(key)


def test_local_storage_saves_exact_content_and_builds_url(tmp_path):
    storage = local_storage(
        tmp_path, local_url_base="/static-media"
    )

    result = storage.salvar_imagem(PNG)

    assert (tmp_path / result.chave).read_bytes() == PNG
    assert result.url == f"/static-media/{result.chave}"


def test_local_remove_is_idempotent(tmp_path):
    storage = local_storage(tmp_path)
    result = storage.salvar_imagem(PNG)

    storage.remover(result.chave)
    storage.remover(result.chave)

    assert not (tmp_path / result.chave).exists()


def test_local_rejects_symlink_traversal(tmp_path):
    root = tmp_path / "media"
    outside = tmp_path / "outside"
    outside.mkdir()
    root.mkdir()
    (root / "anuncios").symlink_to(outside, target_is_directory=True)
    storage = local_storage(root)

    with pytest.raises(ChaveInvalidaError):
        storage.remover(f"anuncios/{'a' * 32}.jpg")

    assert list(outside.iterdir()) == []


def test_local_atomic_write_cleans_temporary_file(tmp_path, monkeypatch):
    storage = local_storage(tmp_path)

    def fail_replace(source, target):
        raise OSError("private filesystem detail")

    monkeypatch.setattr("infra.storage.storage.os.replace", fail_replace)
    with pytest.raises(StorageIndisponivelError) as error:
        storage.salvar_imagem(PNG)

    assert "private filesystem detail" not in str(error.value)
    assert not any(path.is_file() for path in tmp_path.rglob("*"))


def test_s3_put_uses_safe_headers_and_optional_prefix():
    client = FakeS3Client()
    storage = s3_storage(client, s3_key_prefix="classifieds/images")

    result = storage.salvar_imagem(PNG)

    call = client.put_calls[0]
    assert call["Bucket"] == "test-image-bucket"
    assert call["Key"] == f"classifieds/images/{result.chave}"
    assert call["Body"] == PNG
    assert call["ContentType"] == "image/png"
    assert call["CacheControl"] == (
        "public, max-age=31536000, immutable"
    )
    assert "ACL" not in call


def test_s3_public_url_and_presigned_url():
    client = FakeS3Client()
    public = s3_storage(
        client,
        s3_public_base_url="https://cdn.example/images",
        s3_key_prefix="app",
    )
    key = f"anuncios/{'a' * 32}.png"

    assert public.obter_url(key) == f"https://cdn.example/images/app/{key}"

    private = s3_storage(client, s3_presign_expires_seconds=900)
    assert private.obter_url(key) == (
        "https://signed.example/image?signature=fake"
    )
    operation, arguments = client.presign_calls[0]
    assert operation == "get_object"
    assert arguments["Params"] == {
        "Bucket": "test-image-bucket",
        "Key": key,
    }
    assert arguments["ExpiresIn"] == 900


def test_s3_remove_is_idempotent_and_validates_keys():
    client = FakeS3Client()
    storage = s3_storage(client)
    key = f"anuncios/{'b' * 32}.jpg"

    storage.remover(key)
    storage.remover(key)

    assert len(client.delete_calls) == 2
    assert client.delete_calls[0] == {
        "Bucket": "test-image-bucket",
        "Key": key,
    }
    with pytest.raises(ChaveInvalidaError):
        storage.remover("../secret")


@pytest.mark.parametrize("key", ["", "../outside.jpg", r"anuncios\bad.jpg"])
@pytest.mark.parametrize("operation", ["obter_url", "remover"])
def test_s3_rejects_invalid_keys(key, operation):
    with pytest.raises(ChaveInvalidaError):
        getattr(s3_storage(), operation)(key)


def test_s3_errors_are_wrapped_without_provider_details():
    client = FakeS3Client()
    client.error = FakeS3Error("secret-key and provider response")
    storage = s3_storage(client)

    with pytest.raises(StorageIndisponivelError) as error:
        storage.salvar_imagem(PNG)

    assert "secret-key" not in str(error.value)
    assert "provider response" not in str(error.value)


@pytest.mark.parametrize(
    ("environ", "message"),
    [
        ({"STORAGE_PROVIDER": "unknown"}, "STORAGE_PROVIDER"),
        (
            {"STORAGE_PROVIDER": "s3"},
            "STORAGE_S3_BUCKET",
        ),
        (
            {
                "STORAGE_S3_ACCESS_KEY_ID": "fictional",
            },
            "STORAGE_S3_ACCESS_KEY_ID",
        ),
        (
            {
                "STORAGE_S3_SECRET_ACCESS_KEY": "fictional",
            },
            "STORAGE_S3_ACCESS_KEY_ID",
        ),
        ({"STORAGE_MAX_IMAGE_BYTES": "zero"}, "STORAGE_MAX_IMAGE_BYTES"),
        (
            {"STORAGE_S3_PRESIGN_EXPIRES_SECONDS": "0"},
            "STORAGE_S3_PRESIGN_EXPIRES_SECONDS",
        ),
    ],
)
def test_invalid_storage_configuration(environ, message):
    with pytest.raises(ConfiguracaoStorageError, match=message):
        ConfiguracaoStorage.from_environment(environ)


def test_storage_configuration_defaults_and_s3_settings():
    default = ConfiguracaoStorage.from_environment({})
    assert default.provider == "local"
    assert default.max_image_bytes == 5 * 1024 * 1024
    assert default.local_url_base == "/media"

    s3 = ConfiguracaoStorage.from_environment(
        {
            "STORAGE_PROVIDER": "s3",
            "STORAGE_S3_BUCKET": "fictional-bucket",
            "STORAGE_S3_REGION": "us-east-1",
            "STORAGE_S3_ENDPOINT_URL": "https://s3.example",
            "STORAGE_S3_KEY_PREFIX": "service/images",
        }
    )
    assert s3.provider == "s3"
    assert s3.s3_region == "us-east-1"
    assert s3.s3_endpoint_url == "https://s3.example"
    assert s3.s3_key_prefix == "service/images"


def test_local_factory_does_not_import_boto3(monkeypatch, tmp_path):
    def reject_import(name):
        raise AssertionError(f"Unexpected import: {name}")

    monkeypatch.setattr(
        "infra.storage.storage.importlib.import_module", reject_import
    )
    storage = criar_storage(ConfiguracaoStorage(local_root=tmp_path))

    assert isinstance(storage, LocalImageStorage)


def test_missing_boto3_has_clear_configuration_error(monkeypatch):
    def missing_dependency(name):
        raise ImportError(name)

    monkeypatch.setattr(
        "infra.storage.storage.importlib.import_module", missing_dependency
    )
    config = ConfiguracaoStorage(
        provider="s3",
        s3_bucket="fictional-bucket",
    )

    with pytest.raises(ConfiguracaoStorageError, match="boto3"):
        criar_storage(config)


def test_s3_factory_passes_endpoint_and_region_lazily(monkeypatch):
    client = FakeS3Client()
    captured = {}

    class FakeBoto3:
        @staticmethod
        def client(service, **kwargs):
            captured["service"] = service
            captured["kwargs"] = kwargs
            return client

    fake_exceptions = SimpleNamespace(
        BotoCoreError=FakeS3Error,
        ClientError=FakeS3Error,
    )

    def fake_import(name):
        if name == "boto3":
            return FakeBoto3
        if name == "botocore.exceptions":
            return fake_exceptions
        raise AssertionError("Unexpected import")

    monkeypatch.setattr(
        "infra.storage.storage.importlib.import_module", fake_import
    )
    config = ConfiguracaoStorage(
        provider="s3",
        s3_bucket="fictional-bucket",
        s3_region="eu-west-1",
        s3_endpoint_url="https://s3.example",
        s3_access_key_id="FAKE_ACCESS_KEY",
        s3_secret_access_key="FAKE_SECRET_KEY",
    )

    assert isinstance(criar_storage(config), S3ImageStorage)
    assert captured == {
        "service": "s3",
        "kwargs": {
            "region_name": "eu-west-1",
            "endpoint_url": "https://s3.example",
            "aws_access_key_id": "FAKE_ACCESS_KEY",
            "aws_secret_access_key": "FAKE_SECRET_KEY",
        },
    }


def test_local_route_serves_files_securely_and_s3_has_no_route(tmp_path):
    local = local_storage(tmp_path)
    stored = local.salvar_imagem(PNG)
    local_app = create_app(local)

    response = local_app.test_client().get(stored.url)

    assert response.status_code == 200
    assert response.data == PNG
    assert response.mimetype == "image/png"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["Cache-Control"] == (
        "public, max-age=31536000, immutable"
    )
    assert local_app.test_client().get("/media/anuncios/").status_code == 404

    s3_app = create_app(s3_storage())
    assert "/media/<path:chave>" not in {
        rule.rule for rule in s3_app.url_map.iter_rules()
    }


def test_app_initializes_storage_from_config_and_registers_custom_prefix(
    local_app,
):
    storage = local_app.extensions["image_storage"]
    stored = storage.salvar_imagem(PNG)

    response = local_app.test_client().get(stored.url)

    assert local_app.config["STORAGE_PROVIDER"] == "local"
    assert local_app.config["STORAGE_LOCAL_URL_BASE"] == "/images"
    assert local_app.config["MAX_CONTENT_LENGTH"] is None
    assert stored.url.startswith("/images/")
    assert response.status_code == 200
    assert response.data == PNG


def test_app_config_overrides_environment_storage_values(
    monkeypatch, tmp_path
):
    monkeypatch.setenv("STORAGE_PROVIDER", "invalid")

    app = create_app(
        config={
            "STORAGE_PROVIDER": "local",
            "STORAGE_LOCAL_ROOT": tmp_path,
        }
    )

    assert isinstance(app.extensions["image_storage"], LocalImageStorage)


@pytest.mark.parametrize(
    "config",
    [
        {"STORAGE_PROVIDER": "invalid"},
        {"STORAGE_PROVIDER": "s3", "STORAGE_S3_BUCKET": ""},
    ],
)
def test_invalid_storage_configuration_fails_app_initialization(config):
    with pytest.raises(ConfiguracaoStorageError):
        create_app(config=config)


@pytest.mark.parametrize(
    "path",
    [
        "/images/not-a-valid-key",
        "/images/../outside.jpg",
        "/images/%2e%2e/outside.jpg",
        "/images/anuncios%2f..%2foutside.jpg",
        "/images/anuncios%5c..%5coutside.jpg",
    ],
)
def test_local_media_route_rejects_invalid_and_traversal_keys(
    local_app, path
):
    response = local_app.test_client().get(path)

    assert response.status_code == 404


def test_local_media_route_returns_404_for_missing_files(local_app):
    path = f"/images/anuncios/{'a' * 32}.png"

    response = local_app.test_client().get(path)

    assert response.status_code == 404


@pytest.mark.parametrize("path", ["/images/", "/images/anuncios/"])
def test_local_media_route_does_not_list_directories(local_app, path):
    response = local_app.test_client().get(path)

    assert response.status_code == 404


def test_s3_app_does_not_register_local_media_route():
    app = create_app(s3_storage())

    assert "/media/<path:chave>" not in {
        rule.rule for rule in app.url_map.iter_rules()
    }
