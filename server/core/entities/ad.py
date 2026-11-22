"""Pure domain representation of an advertisement."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Ad:
    """An advertisement that can be displayed in the feed."""

    title: str
    type: str
    category: str
    price: float | None
    created_at: datetime
    status: str
    description: str | None = None
    image_url: str | None = None
    expires_at: datetime | None = None
    id: int | None = None
    nome_anunciante: str | None = None
    estado_conservacao: str | None = None
    preco_a_combinar: bool = False
