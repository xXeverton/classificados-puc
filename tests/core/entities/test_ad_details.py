from datetime import UTC, datetime

from server.core.entities.ad import Ad
from server.core.entities.ad_details import AdDetails, AdvertiserSummary
from server.core.entities.contato import Contato
from server.core.entities.tipo_de_contato import TipoDeContato


def test_ad_details_accepts_one_optional_photo_and_public_advertiser():
    ad = Ad(
        title="Bicicleta",
        description="Bicicleta em bom estado.",
        type="product",
        category="Esportes",
        price=450.0,
        image_url="/uploads/anuncios/bicicleta.jpg",
        created_at=datetime(2026, 11, 21, 12, 0, tzinfo=UTC),
        status="published",
        estado_conservacao="usado_regular",
    )
    advertiser = AdvertiserSummary(
        nome_exibicao="Ana PUC",
        vinculo="aluno",
        foto_url="/fotos-perfil/ana.jpg",
        contatos=(Contato(TipoDeContato.EMAIL, "ana@puc-rio.br"),),
    )

    details = AdDetails(ad=ad, advertiser=advertiser)

    assert details.ad.image_url == "/uploads/anuncios/bicicleta.jpg"
    assert details.advertiser.nome_exibicao == "Ana PUC"
    assert len(details.advertiser.contatos) == 1


def test_ad_details_accepts_ad_without_photo():
    ad = Ad(
        title="Aulas de inglês",
        description="Aulas particulares.",
        type="service",
        category="Educação",
        price=None,
        image_url=None,
        created_at=datetime(2026, 11, 21, 12, 0, tzinfo=UTC),
        status="published",
    )
    advertiser = AdvertiserSummary(
        nome_exibicao="Ana PUC",
        vinculo="funcionario",
        foto_url=None,
        contatos=(Contato(TipoDeContato.EMAIL, "ana@puc-rio.br"),),
    )

    details = AdDetails(ad=ad, advertiser=advertiser)

    assert details.ad.image_url is None
    assert details.advertiser.foto_url is None
