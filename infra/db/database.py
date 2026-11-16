"""Database schema initialization helpers."""

import sqlite3
from pathlib import Path

_SCHEMA_PATH = Path(__file__).with_name("schema.sql")
_MIGRATIONS_PATH = Path(__file__).with_name("migrations")
_MIGRATIONS = (
    (1, _MIGRATIONS_PATH / "0001_create_anuncios.up.sql"),
)


def connect_database(database: str | Path) -> sqlite3.Connection:
    """Open a SQLite connection with foreign-key enforcement enabled."""
    connection = sqlite3.connect(database)
    try:
        _enable_foreign_keys(connection)
    except (sqlite3.Error, RuntimeError):
        connection.close()
        raise
    return connection


def _enable_foreign_keys(connection: sqlite3.Connection) -> None:
    connection.execute("PRAGMA foreign_keys = ON")
    if connection.execute("PRAGMA foreign_keys").fetchone()[0] != 1:
        raise RuntimeError(
            "SQLite foreign key enforcement could not be enabled"
        )


def initialize_database(connection: sqlite3.Connection) -> None:
    """Create the base schema and apply each migration once."""
    if connection.in_transaction:
        raise RuntimeError(
            "initialize_database must run outside an active transaction"
        )

    _enable_foreign_keys(connection)
    schema = _SCHEMA_PATH.read_text(encoding="utf-8")
    connection.executescript(schema)

    current_version = connection.execute("PRAGMA user_version").fetchone()[0]
    latest_version = _MIGRATIONS[-1][0]
    if current_version > latest_version:
        raise RuntimeError(
            f"Database version {current_version} is newer than supported "
            f"version {latest_version}"
        )

    for version, migration_path in _MIGRATIONS:
        if version <= current_version:
            continue
        migration = migration_path.read_text(encoding="utf-8")
        try:
            connection.executescript(migration)
        except sqlite3.Error:
            if connection.in_transaction:
                connection.rollback()
            raise
