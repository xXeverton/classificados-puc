"""Use case for retrieving public advertisement details."""

from server.core.entities.ad_details import AdDetails, AdvertiserSummary
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
    PerfilNaoEncontrado,
    UsuarioNaoAutenticado,
)


class ObterDetalhesAnuncio:
    """Return public details only to an authenticated confirmed member."""

    def __init__(
        self,
        anuncios: AdRepository,
        anunciantes: AnuncianteRepositoryInterface,
        usuarios: UsuarioRepositoryInterface,
    ) -> None:
        self._anuncios = anuncios
        self._anunciantes = anunciantes
        self._usuarios = usuarios

    def executar(
        self,
        usuario: Usuario | None,
        anuncio_id: int,
    ) -> AdDetails:
        if usuario is None:
            raise UsuarioNaoAutenticado()
        if not usuario.esta_confirmado():
            raise EmailNaoConfirmado()
        if isinstance(anuncio_id, bool) or not isinstance(anuncio_id, int):
            raise DadosInvalidos(
                "O identificador do anúncio deve ser inteiro."
            )
        if anuncio_id < 1:
            raise DadosInvalidos(
                "O identificador do anúncio deve ser positivo."
            )

        ad = self._anuncios.buscar_por_id(anuncio_id)
        if ad is None:
            raise AnuncioNaoEncontrado()

        if ad.status == "deleted":
            raise AnuncioExcluido()
        if ad.status == "sold":
            raise AnuncioVendido()
        if ad.status == "expired":
            raise AnuncioExpirado()
        if ad.status != "published":
            raise AnuncioNaoPublicado()

        if ad.usuario_id is None:
            raise PerfilNaoEncontrado()
        advertiser = self._anunciantes.buscar_por_usuario_id(ad.usuario_id)
        if advertiser is None:
            raise PerfilNaoEncontrado()
        owner = self._usuarios.buscar_por_id(ad.usuario_id)
        if owner is None:
            raise AnuncioNaoEncontrado()

        summary = AdvertiserSummary(
            nome_exibicao=advertiser.nome_exibicao,
            vinculo=owner.vinculo.value,
            foto_url=advertiser.foto_url,
            contatos=advertiser.contatos,
        )
        return AdDetails(
            ad=ad,
            advertiser=summary,
            is_owner=ad.usuario_id == usuario.id,
        )
