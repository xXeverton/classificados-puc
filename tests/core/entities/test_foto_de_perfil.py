import pytest

from server.core.entities.foto_de_perfil import FormatoDeFoto, FotoDePerfil
from server.core.entities.politicas_perfil import TAMANHO_MAXIMO_FOTO_BYTES

JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 16
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16
WEBP = b"RIFF\x24\x00\x00\x00WEBPVP8 " + b"\x00" * 16


def preencher(cabecalho: bytes, tamanho: int) -> bytes:
    return cabecalho + b"\x00" * (tamanho - len(cabecalho))


@pytest.mark.parametrize(
    ("conteudo", "formato", "extensao"),
    [
        (JPEG, FormatoDeFoto.JPEG, "jpg"),
        (PNG, FormatoDeFoto.PNG, "png"),
        (WEBP, FormatoDeFoto.WEBP, "webp"),
    ],
)
def test_format_comes_from_the_file_signature(conteudo, formato, extensao):
    foto = FotoDePerfil.de_bytes(conteudo)

    assert foto.formato is formato
    assert foto.formato.value == extensao
    assert foto.conteudo == conteudo


def test_exactly_the_maximum_size_is_accepted():
    conteudo = preencher(JPEG, TAMANHO_MAXIMO_FOTO_BYTES)

    assert FotoDePerfil.de_bytes(conteudo).conteudo == conteudo


def test_one_byte_over_the_maximum_is_refused():
    conteudo = preencher(JPEG, TAMANHO_MAXIMO_FOTO_BYTES + 1)

    with pytest.raises(ValueError, match="2 MB"):
        FotoDePerfil.de_bytes(conteudo)


@pytest.mark.parametrize(
    "conteudo",
    [
        b"",
        b"GIF89a" + b"\x00" * 16,
        b"%PDF-1.7\n" + b"\x00" * 16,
        b"isto nao e uma imagem, mesmo com nome .jpg",
        b"RIFF\x24\x00\x00\x00WAVEfmt " + b"\x00" * 16,
        b"\xff\xd8",
    ],
)
def test_empty_or_unknown_content_is_refused(conteudo):
    with pytest.raises(ValueError):
        FotoDePerfil.de_bytes(conteudo)
