"""Use case for publishing an announcement."""

from typing import Protocol

from domain.anuncio import Anuncio, AnuncioPublicado


class RepositorioAnuncios(Protocol):
    def salvar(self, anuncio: Anuncio) -> AnuncioPublicado:
        """Persist the announcement and return its public details."""


class PublicarAnuncio:
    def __init__(self, repositorio: RepositorioAnuncios) -> None:
        self._repositorio = repositorio

    def executar(self, anuncio: Anuncio) -> AnuncioPublicado:
        return self._repositorio.salvar(anuncio)
