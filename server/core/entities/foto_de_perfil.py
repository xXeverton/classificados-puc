"""Profile photo: its format comes from the file content, not the name."""

from dataclasses import dataclass
from enum import Enum

from server.core.entities.politicas_perfil import TAMANHO_MAXIMO_FOTO_BYTES

_MENSAGEM_TAMANHO = "A foto deve ter no máximo 2 MB."
_MENSAGEM_FORMATO = "A foto deve ser uma imagem JPG, PNG ou WEBP."


class FormatoDeFoto(Enum):
    """The value is the file extension used when storing the photo."""

    JPEG = "jpg"
    PNG = "png"
    WEBP = "webp"


def _detectar_formato(conteudo: bytes) -> FormatoDeFoto | None:
    if conteudo.startswith(b"\xff\xd8\xff"):
        return FormatoDeFoto.JPEG
    if conteudo.startswith(b"\x89PNG\r\n\x1a\n"):
        return FormatoDeFoto.PNG
    if conteudo[:4] == b"RIFF" and conteudo[8:12] == b"WEBP":
        return FormatoDeFoto.WEBP
    return None


@dataclass(frozen=True)
class FotoDePerfil:
    conteudo: bytes
    formato: FormatoDeFoto

    @classmethod
    def de_bytes(cls, conteudo: bytes) -> "FotoDePerfil":
        """Validate size and signature; raise ValueError when invalid."""
        if len(conteudo) > TAMANHO_MAXIMO_FOTO_BYTES:
            raise ValueError(_MENSAGEM_TAMANHO)
        formato = _detectar_formato(conteudo)
        if formato is None:
            raise ValueError(_MENSAGEM_FORMATO)
        return cls(conteudo, formato)
