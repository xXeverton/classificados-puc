"""Command-line entry points, run by a scheduler instead of over HTTP."""

import click
from flask import Flask

from server.core.usecases.delete_expired_ads import DeleteExpiredAds
from server.core.usecases.expire_ads import ExpireAds
from server.infra.storage.storage import (
    ChaveInvalidaError,
    ImageStorage,
    StorageIndisponivelError,
)


def register_commands(
    app: Flask,
    expire_ads: ExpireAds,
    delete_expired_ads: DeleteExpiredAds,
    image_storage: ImageStorage,
) -> None:
    """Register the maintenance commands on the Flask CLI."""

    @app.cli.command("expirar-anuncios")
    def expirar_anuncios() -> None:
        """Expira os anúncios publicados cujo prazo terminou."""
        expirados = expire_ads.execute()
        click.echo(f"{expirados} anúncio(s) expirado(s).")

    @app.cli.command("apagar-anuncios-expirados")
    def apagar_anuncios_expirados() -> None:
        """Apaga os anúncios expirados há 30 dias ou mais e suas fotos."""
        resultado = delete_expired_ads.execute()
        falhas = 0
        for chave in resultado.image_keys:
            try:
                image_storage.remover(chave)
            except (ChaveInvalidaError, StorageIndisponivelError):
                # The ad is already deleted; a photo left behind is only
                # logged (spec 008, RN4).
                falhas += 1
                app.logger.exception(
                    "Não foi possível apagar a foto de um anúncio expirado."
                )
        click.echo(f"{resultado.deleted} anúncio(s) apagado(s).")
        if falhas:
            click.echo(
                f"{falhas} foto(s) não puderam ser apagadas; veja o log."
            )
