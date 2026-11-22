"""Let the owner mark an ad as sold or reactivate it (spec 011)."""

from server.core.entities.ad import Ad
from server.core.interfaces.anuncio_editavel_repository_interface import (
    AnuncioEditavelRepositoryInterface,
)
from server.core.interfaces.relogio_interface import RelogioInterface
from server.core.usecases.anuncio_do_dono import buscar_anuncio_do_dono
from server.core.usecases.erros import (
    MudancaDeStatusInvalida,
    StatusInvalido,
)

VENDIDO = "sold"
PUBLICADO = "published"
EXPIRADO = "expired"


class AlterarStatusAnuncio:
    def __init__(
        self,
        anuncios: AnuncioEditavelRepositoryInterface,
        relogio: RelogioInterface,
    ) -> None:
        self._anuncios = anuncios
        self._relogio = relogio

    def executar(self, ad_id: int, usuario_id: int, novo_status) -> Ad:
        """Change the status to `sold` or back to `published`."""
        if novo_status not in (VENDIDO, PUBLICADO):
            raise StatusInvalido()
        anuncio = buscar_anuncio_do_dono(self._anuncios, ad_id, usuario_id)

        if novo_status == VENDIDO:
            if anuncio.status == VENDIDO:
                return anuncio
            return self._anuncios.alterar_status(ad_id, VENDIDO)

        if anuncio.status != VENDIDO:
            raise MudancaDeStatusInvalida()
        # Reactivating keeps the publication period (RN4): an ad past its
        # end comes back as expired, and the owner can renew it.
        if anuncio.publication_ends_at() <= self._relogio.agora():
            return self._anuncios.alterar_status(ad_id, EXPIRADO)
        return self._anuncios.alterar_status(ad_id, PUBLICADO)
