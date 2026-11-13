"""Request-scoped SQLite connection for Flask routes."""

import sqlite3
from pathlib import Path

from flask import Flask, current_app, g

from infra.db.database import connect_database, initialize_database


def get_db() -> sqlite3.Connection:
    """Return the initialized SQLite connection for the current request."""
    if "database" not in g:
        database_path = current_app.config["DATABASE"]
        if str(database_path) != ":memory:":
            Path(database_path).parent.mkdir(parents=True, exist_ok=True)

        connection = connect_database(database_path)
        connection.row_factory = sqlite3.Row
        try:
            initialize_database(connection)
        except (OSError, RuntimeError, sqlite3.Error):
            connection.close()
            raise
        g.database = connection
    return g.database


def _close_db(_error: BaseException | None = None) -> None:
    connection = g.pop("database", None)
    if connection is not None:
        connection.close()


def init_app(app: Flask) -> None:
    """Register connection cleanup at the end of each app context."""
    app.teardown_appcontext(_close_db)
