"""Let the owner change the editable fields of an advertisement."""

from server.core.entities.ad import Ad
from server.core.entities.anuncio import Anuncio
from server.core.interfaces.anuncio_editavel_repository_interface import (
    AnuncioEditavelRepositoryInterface,
)
from server.core.usecases.anuncio_do_dono import buscar_anuncio_do_dono
from server.core.usecases.erros import CategoriaNaoEditavel


class EditarAnuncio:
    def __init__(self, anuncios: AnuncioEditavelRepositoryInterface) -> None:
        self._anuncios = anuncios

    def executar(self, ad_id: int, anuncio: Anuncio) -> Ad:
        """Save `anuncio` over the ad; `anuncio.usuario_id` is the editor."""
        atual = buscar_anuncio_do_dono(
            self._anuncios, ad_id, anuncio.usuario_id
        )
        # The category defines the ad type and which fields apply (RN3).
        if anuncio.categoria != atual.category:
            raise CategoriaNaoEditavel()
        return self._anuncios.atualizar(ad_id, anuncio)
