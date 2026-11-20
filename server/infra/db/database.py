"""SQLAlchemy engine, session factory, and schema initialization."""

from pathlib import Path

from sqlalchemy import create_engine, event
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
    is_sqlite = make_url(database_url).get_backend_name() == "sqlite"
    if is_sqlite:
        engine_options["connect_args"] = {"check_same_thread": False}
    engine = create_engine(database_url, **engine_options)
    if is_sqlite:
        event.listen(engine, "connect", _enable_sqlite_foreign_keys)
    return engine


def _enable_sqlite_foreign_keys(dbapi_connection, _connection_record) -> None:
    """SQLite only enforces foreign keys (and ON DELETE) when asked to."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Create sessions bound to the given engine."""
    return sessionmaker(bind=engine, expire_on_commit=False)


def initialize_database(engine: Engine) -> None:
    """Create tables declared by the SQLAlchemy models when they are absent."""
    Base.metadata.create_all(engine)
