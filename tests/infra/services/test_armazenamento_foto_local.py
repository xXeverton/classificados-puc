import re

import pytest

from server.core.entities.foto_de_perfil import FormatoDeFoto, FotoDePerfil
from server.infra.services.armazenamento_foto_local import (
    ArmazenamentoDeFotoLocal,
)

JPEG = FotoDePerfil(b"\xff\xd8\xff\xe0jpeg", FormatoDeFoto.JPEG)
PNG = FotoDePerfil(b"\x89PNG\r\n\x1a\npng", FormatoDeFoto.PNG)
WEBP = FotoDePerfil(b"RIFF\x00\x00\x00\x00WEBPwebp", FormatoDeFoto.WEBP)


@pytest.fixture
def pasta(tmp_path):
    return tmp_path / "fotos"


@pytest.fixture
def armazenamento(pasta):
    return ArmazenamentoDeFotoLocal(pasta)


@pytest.mark.parametrize(
    ("foto", "extensao"), [(JPEG, "jpg"), (PNG, "png"), (WEBP, "webp")]
)
def test_save_returns_url_with_random_name_and_format_extension(
    armazenamento, foto, extensao
):
    foto_url = armazenamento.salvar(foto)

    assert re.fullmatch(
        rf"/fotos-perfil/[A-Za-z0-9_-]{{43}}\.{extensao}", foto_url
    )


def test_save_creates_the_folder_and_writes_the_bytes(
    armazenamento, pasta
):
    assert not pasta.exists()

    foto_url = armazenamento.salvar(JPEG)

    arquivo = pasta / foto_url.rsplit("/", 1)[1]
    assert arquivo.read_bytes() == JPEG.conteudo


def test_same_photo_saved_twice_gets_different_names(armazenamento):
    assert armazenamento.salvar(JPEG) != armazenamento.salvar(JPEG)


def test_read_returns_the_saved_bytes(armazenamento):
    foto_url = armazenamento.salvar(PNG)

    assert armazenamento.ler(foto_url) == PNG.conteudo


def test_read_of_missing_photo_returns_none(armazenamento):
    assert armazenamento.ler("/fotos-perfil/naoexiste.jpg") is None


def test_remove_deletes_the_file(armazenamento, pasta):
    foto_url = armazenamento.salvar(JPEG)

    armazenamento.remover(foto_url)

    assert armazenamento.ler(foto_url) is None
    assert list(pasta.iterdir()) == []


def test_removing_a_missing_photo_does_not_fail(armazenamento):
    armazenamento.remover("/fotos-perfil/naoexiste.jpg")


@pytest.mark.parametrize(
    "foto_url",
    [
        "/fotos-perfil/../segredo.jpg",
        "/fotos-perfil/..%2Fsegredo.jpg",
        "/fotos-perfil/sub/segredo.jpg",
        "/fotos-perfil/..\\segredo.jpg",
        "/fotos-perfil/segredo.txt",
        "/fotos-perfil/.jpg",
        "/outra-pasta/segredo.jpg",
        "../segredo.jpg",
        "segredo.jpg/",
        "",
    ],
)
def test_unsafe_names_are_refused_for_read_and_remove(
    armazenamento, pasta, tmp_path, foto_url
):
    armazenamento.salvar(JPEG)
    segredo = tmp_path / "segredo.jpg"
    segredo.write_bytes(b"segredo")

    assert armazenamento.ler(foto_url) is None
    armazenamento.remover(foto_url)

    assert segredo.read_bytes() == b"segredo"
    assert len(list(pasta.iterdir())) == 1
