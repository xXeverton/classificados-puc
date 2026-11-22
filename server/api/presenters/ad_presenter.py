"""HTTP response schemas and presenter for advertisements."""

from datetime import datetime

from pydantic import BaseModel

from server.core.entities.ad import Ad
from server.core.entities.ad_details import AdDetails


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
    status: str | None = None
    expires_at: datetime | None = None


class AdsFeedViewSchema(BaseModel):
    """Public response returned for the advertisements feed."""

    items: list[AdViewSchema]
    page: int
    per_page: int
    total_pages: int
    total_items: int
    message: str | None = None


class AdvertiserDetailsViewSchema(BaseModel):
    display_name: str
    affiliation: str
    photo_url: str | None
    contacts: list[dict[str, object]]


class AdDetailsViewSchema(BaseModel):
    ad: AdViewSchema
    advertiser: AdvertiserDetailsViewSchema


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
        status=ad.status,
        expires_at=ad.expires_at,
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


def apresenta_detalhes(details: AdDetails) -> AdDetailsViewSchema:
    """Convert advertisement details into the protected API contract."""
    advertiser = details.advertiser
    contacts: list[dict[str, object]] = [
        {
            "tipo": contato.tipo.value,
            "codigo_pais": contato.codigo_pais,
            "valor": contato.valor,
            "rotulo": contato.rotulo,
            "link_de_conversa": (
                contato.link_de_conversa()
                if contato.tipo.value == "whatsapp"
                else None
            ),
        }
        for contato in advertiser.contatos
    ]
    ad = apresenta_ad(details.ad)
    return AdDetailsViewSchema(
        ad=ad,
        advertiser=AdvertiserDetailsViewSchema(
            display_name=advertiser.nome_exibicao,
            affiliation=advertiser.vinculo,
            photo_url=advertiser.foto_url,
            contacts=contacts,
        ),
    )
