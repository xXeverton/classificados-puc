"""HTTP response schemas and presenter for advertisements."""

from datetime import datetime

from pydantic import BaseModel

from server.core.entities.ad import Ad


class AdViewSchema(BaseModel):
    """Public fields returned for an advertisement card."""

    id: int | None
    title: str
    description: str | None
    type: str
    category: str
    price: float | None
    image_url: str | None
    created_at: datetime
    nome_anunciante: str | None = None
    estado_conservacao: str | None = None
    preco_a_combinar: bool = False


class AdsFeedViewSchema(BaseModel):
    """Public response returned for the advertisements feed."""

    items: list[AdViewSchema]
    page: int
    per_page: int
    total_pages: int
    total_items: int
    message: str | None = None


def apresenta_ad(ad: Ad) -> AdViewSchema:
    """Convert an Ad entity into its public card representation."""
    return AdViewSchema(
        id=ad.id,
        title=ad.title,
        description=ad.description,
        type=ad.type,
        category=ad.category,
        price=ad.price,
        image_url=ad.image_url,
        created_at=ad.created_at,
        nome_anunciante=ad.nome_anunciante,
        estado_conservacao=ad.estado_conservacao,
        preco_a_combinar=ad.preco_a_combinar,
    )


def apresenta_feed(result: dict[str, object]) -> AdsFeedViewSchema:
    """Convert a ListAds result into the public feed response."""
    return AdsFeedViewSchema(
        items=[
            apresenta_ad(ad)
            for ad in result["items"]
        ],
        page=result["page"],
        per_page=result["per_page"],
        total_pages=result["total_pages"],
        total_items=result["total_items"],
        message=result.get("message"),
    )
