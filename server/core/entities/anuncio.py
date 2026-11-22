"""Announcement creation data and business constraints."""

from dataclasses import dataclass
from decimal import Decimal

CATEGORIAS = ("produto", "servico", "evento")
ESTADOS_CONSERVACAO = ("novo", "usado_regular")
TITULO_MIN_CARACTERES = 5
TITULO_MAX_CARACTERES = 80
DESCRICAO_MAX_CARACTERES = 500
PRECO_MAXIMO = Decimal("9999999999.99")
PRAZO_EXPIRACAO_DIAS = 30


@dataclass(frozen=True)
class Anuncio:
    usuario_id: int
    titulo: str
    descricao: str
    categoria: str
    preco: Decimal | None
    estado_conservacao: str | None = None
    image_key: str | None = None

    def __post_init__(self) -> None:
        if (
            isinstance(self.usuario_id, bool)
            or not isinstance(self.usuario_id, int)
            or self.usuario_id < 1
        ):
            raise ValueError("usuario_id: anunciante inválido.")
        if not isinstance(self.titulo, str) or not (
            TITULO_MIN_CARACTERES
            <= len(self.titulo)
            <= TITULO_MAX_CARACTERES
        ):
            raise ValueError("titulo: entre 5 e 80 caracteres.")
        if self.titulo != self.titulo.strip():
            raise ValueError("titulo: remova espaços nas extremidades.")
        if (
            not isinstance(self.descricao, str)
            or not self.descricao.strip()
            or len(self.descricao) > DESCRICAO_MAX_CARACTERES
        ):
            raise ValueError("descricao: até 500 caracteres e obrigatória.")
        if self.categoria not in CATEGORIAS:
            raise ValueError("categoria: selecione uma categoria válida.")
        if self.categoria == "produto":
            if self.estado_conservacao not in ESTADOS_CONSERVACAO:
                raise ValueError(
                    "estado_conservacao: inválido para produto."
                )
        elif self.estado_conservacao is not None:
            raise ValueError("estado_conservacao: não se aplica.")
        if self.preco is not None and (
            not isinstance(self.preco, Decimal)
            or not self.preco.is_finite()
            or self.preco < 0
            or self.preco > PRECO_MAXIMO
            or self.preco.as_tuple().exponent < -2
        ):
            raise ValueError(
                "preco: informe valor válido com até 2 casas."
            )
