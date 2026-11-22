"""Command-line entry points, run by a scheduler instead of over HTTP."""

import click
from flask import Flask

from server.core.usecases.expire_ads import ExpireAds


def register_commands(app: Flask, expire_ads: ExpireAds) -> None:
    """Register the maintenance commands on the Flask CLI."""

    @app.cli.command("expirar-anuncios")
    def expirar_anuncios() -> None:
        """Expira os anúncios publicados cujo prazo terminou."""
        expirados = expire_ads.execute()
        click.echo(f"{expirados} anúncio(s) expirado(s).")
