"""Pure domain representation of an advertisement."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import ClassVar

PUBLISHED = "published"


@dataclass(frozen=True)
class Ad:
    """An advertisement that can be displayed in the feed."""

    PUBLICATION_PERIOD: ClassVar[timedelta] = timedelta(days=30)

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
    usuario_id: int | None = None

    def publication_ends_at(self) -> datetime:
        """End of the publication period.

        `expires_at` holds the end set at publication or by the last
        renewal; ads without it fall back to the default period.
        """
        if self.expires_at is not None:
            return self.expires_at
        return self.created_at + self.PUBLICATION_PERIOD

    def is_overdue(self, now: datetime) -> bool:
        """Tell whether a published ad has reached the end of its period."""
        return self.status == PUBLISHED and now >= self.publication_ends_at()
