"""Command-line entry points, run by a scheduler instead of over HTTP."""

import os
from datetime import datetime, timezone
from pathlib import Path

import click
from flask import Flask
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from server.api.demo_data import (
    DEMO_EMAIL,
    DEMO_USERNAME,
    create_demo_data,
)
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
    session_factory: sessionmaker[Session],
    database_engine: Engine,
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

    @app.cli.command("criar-dados-demo")
    def criar_dados_demo() -> None:
        """Create the local demo account and sample ads."""
        if os.environ.get("ALLOW_DEMO_DATA") != "1":
            raise click.ClickException(
                "Defina ALLOW_DEMO_DATA=1 para habilitar dados demo."
            )
        if not _is_default_local_database(database_engine):
            raise click.ClickException(
                "Dados demo só podem ser criados no SQLite local padrão."
            )
        password = os.environ.get("DEMO_PASSWORD")
        if not password or len(password) < 8:
            raise click.ClickException(
                "Defina DEMO_PASSWORD com pelo menos 8 caracteres."
            )
        try:
            count = create_demo_data(
                session_factory,
                password,
                datetime.now(timezone.utc),
            )
        except ValueError as error:
            raise click.ClickException(str(error)) from error

        click.echo(
            f"Conta demo pronta: {DEMO_USERNAME} ({DEMO_EMAIL})."
        )
        click.echo(f"{count} anúncio(s) de exemplo criado(s).")


def _is_default_local_database(engine: Engine) -> bool:
    if engine.dialect.name != "sqlite":
        return False
    database = engine.url.database
    if not database or database == ":memory:":
        return False
    expected = Path(__file__).resolve().parents[1] / "database" / "db.sqlite3"
    return Path(database).resolve() == expected.resolve()
