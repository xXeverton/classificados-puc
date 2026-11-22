"""Let the owner permanently delete an advertisement."""

from server.core.interfaces.anuncio_editavel_repository_interface import (
    AnuncioEditavelRepositoryInterface,
)
from server.core.usecases.anuncio_do_dono import buscar_anuncio_do_dono


class ExcluirAnuncio:
    def __init__(self, anuncios: AnuncioEditavelRepositoryInterface) -> None:
        self._anuncios = anuncios

    def executar(self, ad_id: int, usuario_id: int) -> str | None:
        """Delete the ad and return its photo key, so it can be removed."""
        anuncio = buscar_anuncio_do_dono(self._anuncios, ad_id, usuario_id)
        self._anuncios.excluir(ad_id)
        return anuncio.image_key
