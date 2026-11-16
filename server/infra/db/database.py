"""SQLAlchemy engine, session factory, and schema initialization."""

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, URL, make_url
from sqlalchemy.orm import Session, sessionmaker

from server.infra.db.models import Base

_DATABASE_PATH = (
    Path(__file__).resolve().parents[2] / "database" / "db.sqlite3"
)


def create_database_engine(database_url: str | None = None) -> Engine:
    """Create the engine, defaulting to the project's SQLite file."""
    if database_url is None:
        _DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
        database_url = URL.create("sqlite", database=str(_DATABASE_PATH))

    engine_options = {}
    if make_url(database_url).get_backend_name() == "sqlite":
        engine_options["connect_args"] = {"check_same_thread": False}
    return create_engine(database_url, **engine_options)


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Create sessions bound to the given engine."""
    return sessionmaker(bind=engine, expire_on_commit=False)


def initialize_database(engine: Engine) -> None:
    """Create tables declared by the SQLAlchemy models when they are absent."""
    Base.metadata.create_all(engine)
