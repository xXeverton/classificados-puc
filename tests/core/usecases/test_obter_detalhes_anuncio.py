from datetime import UTC, datetime

import pytest

from server.core.entities.ad import Ad
from server.core.entities.anunciante import Anunciante
from server.core.entities.contato import Contato
from server.core.entities.tipo_de_contato import TipoDeContato
from server.core.entities.usuario import Usuario
from server.core.interfaces.ad_repository_interface import AdRepository
from server.core.interfaces.anunciante_repository_interface import (
    AnuncianteRepositoryInterface,
)
from server.core.interfaces.usuario_repository_interface import (
    UsuarioRepositoryInterface,
)
from server.core.usecases.erros import (
    AnuncioExcluido,
    AnuncioExpirado,
    AnuncioNaoEncontrado,
    AnuncioNaoPublicado,
    AnuncioVendido,
    DadosInvalidos,
    EmailNaoConfirmado,
    UsuarioNaoAutenticado,
)
from server.core.usecases.obter_detalhes_anuncio import (
    ObterDetalhesAnuncio,
)


class InMemoryAdRepository(AdRepository):
    def __init__(self, ads):
        self.ads = {ad.id: ad for ad in ads if ad.id is not None}

    def buscar_por_id(self, anuncio_id):
        return self.ads.get(anuncio_id)

    def list_published(
        self,
        page,
        per_page,
        search,
        ad_type,
        category=None,
        min_price=None,
        max_price=None,
    ):
        raise NotImplementedError

    def publish(
        self,
        anuncio,
        nome_anunciante,
        criado_em,
        expira_em,
    ):
        raise NotImplementedError


class InMemoryAdvertiserRepository(AnuncianteRepositoryInterface):
    def __init__(self, advertiser):
        self.advertiser = advertiser

    def buscar_por_usuario_id(self, usuario_id):
        if self.advertiser.usuario_id == usuario_id:
            return self.advertiser
        return None

    def salvar(self, anunciante):
        raise NotImplementedError


class InMemoryUserRepository(UsuarioRepositoryInterface):
    def __init__(self, users):
        self.users = {user.id: user for user in users}

    def buscar_por_id(self, usuario_id):
        return self.users.get(usuario_id)

    def buscar_por_email(self, email):
        return next(
            (user for user in self.users.values() if user.email == email),
            None,
        )

    def buscar_por_identificador_alternativo(self, valor):
        return next(
            (
                user
                for user in self.users.values()
                if valor in (user.nome_usuario, user.matricula)
            ),
            None,
        )

    def salvar(self, usuario):
        raise NotImplementedError

    def remover(self, usuario_id):
        raise NotImplementedError


def make_user(*, confirmed=True, usuario_id=10, vinculo="aluno"):
    return Usuario(
        nome="Ana",
        email="ana@aluno.puc-rio.br",
        nome_usuario="ana123",
        matricula="123",
        vinculo=vinculo,
        senha_hash="hash",
        confirmado_em=(
            datetime(2026, 11, 20, 12, 0, tzinfo=UTC)
            if confirmed
            else None
        ),
        id=usuario_id,
    )


def make_ad(status="published", ad_id=1):
    return Ad(
        id=ad_id,
        title="Bicicleta",
        description="Bicicleta em bom estado.",
        type="product",
        category="Esportes",
        price=450.0,
        image_url="/uploads/anuncios/bicicleta.jpg",
        created_at=datetime(2026, 11, 21, 12, 0, tzinfo=UTC),
        status=status,
        usuario_id=20,
        estado_conservacao="usado_regular",
    )


def make_advertiser():
    contact = Contato(TipoDeContato.EMAIL, "ana@puc-rio.br")
    return Anunciante(
        id=3,
        usuario_id=20,
        nome_exibicao="Ana PUC",
        foto_url="/fotos-perfil/ana.jpg",
        contatos=(contact,),
    )


def make_use_case(ad):
    owner = make_user(usuario_id=20)
    return ObterDetalhesAnuncio(
        anuncios=InMemoryAdRepository([ad]),
        anunciantes=InMemoryAdvertiserRepository(make_advertiser()),
        usuarios=InMemoryUserRepository([owner]),
    )


def test_returns_public_details_for_confirmed_authenticated_user():
    details = make_use_case(make_ad()).executar(
        usuario=make_user(),
        anuncio_id=1,
    )

    assert details.ad.title == "Bicicleta"
    assert details.ad.image_url == "/uploads/anuncios/bicicleta.jpg"
    assert details.advertiser.nome_exibicao == "Ana PUC"
    assert details.advertiser.vinculo == "aluno"
    assert details.advertiser.contatos[0].valor == "ana@puc-rio.br"


def test_rejects_missing_session():
    with pytest.raises(UsuarioNaoAutenticado):
        make_use_case(make_ad()).executar(
            usuario=None,
            anuncio_id=1,
        )


def test_rejects_unconfirmed_account():
    with pytest.raises(EmailNaoConfirmado):
        make_use_case(make_ad()).executar(
            usuario=make_user(confirmed=False),
            anuncio_id=1,
        )


@pytest.mark.parametrize("anuncio_id", [0, -1, True])
def test_rejects_invalid_ad_id(anuncio_id):
    with pytest.raises(DadosInvalidos):
        make_use_case(make_ad()).executar(
            usuario=make_user(),
            anuncio_id=anuncio_id,
        )


def test_reports_ad_not_found():
    with pytest.raises(AnuncioNaoEncontrado):
        make_use_case(make_ad()).executar(
            usuario=make_user(),
            anuncio_id=999,
        )


@pytest.mark.parametrize(
    ("status", "error"),
    [
        ("deleted", AnuncioExcluido),
        ("sold", AnuncioVendido),
        ("expired", AnuncioExpirado),
        ("draft", AnuncioNaoPublicado),
        ("unpublished", AnuncioNaoPublicado),
    ],
)
def test_reports_unavailable_ad_state(status, error):
    with pytest.raises(error):
        make_use_case(make_ad(status=status)).executar(
            usuario=make_user(),
            anuncio_id=1,
        )
