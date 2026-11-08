"""Database schema initialization helpers."""

import sqlite3
from pathlib import Path

_SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def initialize_database(connection: sqlite3.Connection) -> None:
    """Create the database tables on the provided SQLite connection."""
    schema = _SCHEMA_PATH.read_text(encoding="utf-8")
    connection.executescript(schema)
