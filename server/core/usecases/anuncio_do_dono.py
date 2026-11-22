"""Shared rule: only the owner may manage an advertisement (spec 007)."""

from server.core.entities.ad import Ad
from server.core.interfaces.anuncio_editavel_repository_interface import (
    AnuncioEditavelRepositoryInterface,
)
from server.core.usecases.erros import (
    AnuncioDeOutroUsuario,
    AnuncioNaoEncontrado,
)


def buscar_anuncio_do_dono(
    anuncios: AnuncioEditavelRepositoryInterface,
    ad_id: int,
    usuario_id: int,
) -> Ad:
    """Return the ad if `usuario_id` owns it.

    Ads without a registered owner cannot be managed by anyone (RN1).
    """
    anuncio = anuncios.buscar_por_id(ad_id)
    if anuncio is None:
        raise AnuncioNaoEncontrado()
    if anuncio.usuario_id is None or anuncio.usuario_id != usuario_id:
        raise AnuncioDeOutroUsuario()
    return anuncio
