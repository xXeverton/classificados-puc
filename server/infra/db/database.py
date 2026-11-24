"""SQLAlchemy engine, session factory, and schema initialization."""

from pathlib import Path

from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.engine import Engine, URL, make_url
from sqlalchemy.orm import Session, sessionmaker

from server.infra.db.models import Base

_DATABASE_PATH = (
    Path(__file__).resolve().parents[2] / "database" / "db.sqlite3"
)
_ADS_MIGRATION = (
    Path(__file__).resolve().parent
    / "migrations"
    / "0002_ads_publication.sql"
)
_ADS_FIELD_CONSTRAINTS_MIGRATION = (
    Path(__file__).resolve().parent
    / "migrations"
    / "0003_ads_field_constraints.sql"
)

_EVENT_COLUMNS = (
    ("sem_preco", "BOOLEAN NOT NULL DEFAULT 0"),
    ("data_evento", "DATE"),
    ("horario_evento", "TIME"),
    ("local_evento", "TEXT"),
)
_ADS_SCHEMA_VERSION = 4


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
    """Create missing tables and safely extend existing ad databases."""
    Base.metadata.create_all(engine)
    if engine.dialect.name == "sqlite":
        _migrate_ads_table(engine)


def _migrate_ads_table(engine: Engine) -> None:
    if "ads" not in inspect(engine).get_table_names():
        return
    with engine.connect() as connection:
        schema = connection.execute(
            text(
                "SELECT sql FROM sqlite_master "
                "WHERE type = 'table' AND name = 'ads'"
            )
        ).scalar_one()
        columns = {
            column["name"]
            for column in inspect(connection).get_columns("ads")
        }
    has_publication_fields = (
        {"usuario_id", "estado_conservacao", "preco_a_combinar", "image_key"}
        <= columns
        and "'event'" in schema
    )
    if not has_publication_fields:
        _execute_sqlite_migration(engine, _ADS_MIGRATION)

    with engine.connect() as connection:
        version = connection.exec_driver_sql(
            "PRAGMA user_version"
        ).scalar_one()
    if version < 3:
        _execute_sqlite_migration(engine, _ADS_FIELD_CONSTRAINTS_MIGRATION)
    _add_event_columns(engine)


def _add_event_columns(engine: Engine) -> None:
    """Add the optional event columns (spec 015) to an existing `ads`.

    They are nullable, so existing rows are kept as they are. The table
    rebuilt by migration 0003 does not have them, hence the check.
    """
    with engine.begin() as connection:
        existentes = {
            column["name"]
            for column in inspect(connection).get_columns("ads")
        }
        for nome, tipo in _EVENT_COLUMNS:
            if nome not in existentes:
                connection.exec_driver_sql(
                    f"ALTER TABLE ads ADD COLUMN {nome} {tipo}"
                )
        connection.exec_driver_sql(
            f"PRAGMA user_version = {_ADS_SCHEMA_VERSION}"
        )


def _execute_sqlite_migration(engine: Engine, migration: Path) -> None:
    raw_connection = engine.raw_connection()
    try:
        raw_connection.driver_connection.executescript(
            migration.read_text(encoding="utf-8")
        )
    finally:
        raw_connection.close()
