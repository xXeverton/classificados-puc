"""Announcement creation model."""

from dataclasses import dataclass
from decimal import Decimal

CATEGORIAS = ("produto", "servico", "evento")
ESTADOS_CONSERVACAO = ("novo", "usado_regular")
TITULO_MIN_CARACTERES = 5
TITULO_MAX_CARACTERES = 80
DESCRICAO_MAX_CARACTERES = 500
PRECO_MAXIMO = Decimal("9999999999.99")


@dataclass(frozen=True)
class Anuncio:
    """Validated announcement fields; the database supplies ID and time."""

    id_anunciante: int
    titulo: str
    descricao: str
    categoria: str
    preco: Decimal | None = None
    estado_conservacao: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.titulo, str):
            raise TypeError("titulo must be a string")
        if not TITULO_MIN_CARACTERES <= len(self.titulo) <= (
            TITULO_MAX_CARACTERES
        ):
            raise ValueError(
                "titulo must contain between 5 and 80 characters"
            )
        if self.titulo != self.titulo.strip(" "):
            raise ValueError("titulo must not have leading or trailing spaces")
        if not isinstance(self.descricao, str):
            raise TypeError("descricao must be a string")
        if (
            not self.descricao.strip(" ")
            or len(self.descricao) > DESCRICAO_MAX_CARACTERES
        ):
            raise ValueError(
                "descricao must be non-empty and at most 500 characters"
            )
        if self.categoria not in CATEGORIAS:
            raise ValueError(f"categoria must be one of {CATEGORIAS}")
        if (
            self.estado_conservacao is not None
            and self.estado_conservacao not in ESTADOS_CONSERVACAO
        ):
            raise ValueError(
                "estado_conservacao must be null or one of "
                f"{ESTADOS_CONSERVACAO}"
            )
        if self.preco is not None and not isinstance(self.preco, Decimal):
            raise TypeError("preco must be a Decimal or None")
        if self.preco is not None and (
            not self.preco.is_finite()
            or self.preco < 0
            or self.preco > PRECO_MAXIMO
            or self.preco.as_tuple().exponent < -2
        ):
            raise ValueError(
                "preco must be between 0 and 9999999999.99 "
                "with at most two decimal places, or None"
            )


@dataclass(frozen=True)
class AnuncioPublicado:
    """Persisted announcement with response metadata."""

    id: int
    id_anunciante: int
    nome_anunciante: str
    titulo: str
    categoria: str
    estado_conservacao: str | None
    descricao: str
    preco: Decimal | None
    created_at: str
