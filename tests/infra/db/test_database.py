import pytest
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine import Engine

from server.infra.db import database


def insert_usuario(engine: Engine, **overrides: str | None) -> None:
    usuario = {
        "nome": "Ana",
        "email": "ana@aluno.puc-rio.br",
        "matricula": "123",
        "vinculo": "aluno",
    }
    usuario.update(overrides)
    columns = ", ".join(usuario)
    parameters = ", ".join(f":{column}" for column in usuario)
    statement = text(
        f"INSERT INTO usuarios ({columns}) VALUES ({parameters})"
    )
    with engine.begin() as connection:
        connection.execute(statement, usuario)


def test_initialize_database_creates_usuarios_table(database_engine):
    columns = inspect(database_engine).get_columns("usuarios")

    assert [column["name"] for column in columns] == [
        "id",
        "nome",
        "email",
        "matricula",
        "vinculo",
    ]
    assert {
        column["name"]: str(column["type"]).upper() for column in columns
    } == {
        "id": "INTEGER",
        "nome": "TEXT",
        "email": "TEXT",
        "matricula": "TEXT",
        "vinculo": "TEXT",
    }
    assert columns[0]["primary_key"] == 1
    assert all(
        not column["nullable"]
        for column in columns
        if column["name"] != "id"
    )
    with database_engine.connect() as connection:
        create_statement = connection.execute(
            text(
                "SELECT sql FROM sqlite_master "
                "WHERE type = 'table' AND name = 'usuarios'"
            )
        ).scalar_one()
    assert "AUTOINCREMENT" in create_statement.upper()


def test_initialize_database_creates_ads_table(database_engine):
    columns = inspect(database_engine).get_columns("ads")

    assert [column["name"] for column in columns] == [
        "id",
        "title",
        "description",
        "type",
        "category",
        "price",
        "image_url",
        "created_at",
        "status",
        "expires_at",
    ]
    assert {
        column["name"]: str(column["type"]).upper() for column in columns
    } == {
        "id": "INTEGER",
        "title": "TEXT",
        "description": "TEXT",
        "type": "TEXT",
        "category": "TEXT",
        "price": "FLOAT",
        "image_url": "TEXT",
        "created_at": "DATETIME",
        "status": "TEXT",
        "expires_at": "DATETIME",
    }
    assert columns[0]["primary_key"] == 1
    assert all(
        not column["nullable"]
        for column in columns
        if column["name"]
        in {"title", "type", "category", "price", "created_at", "status"}
    )


def insert_ad(engine: Engine, **overrides):
    ad = {
        "title": "Bicicleta usada",
        "description": "Bicicleta em bom estado.",
        "type": "product",
        "category": "Esportes",
        "price": 450.0,
        "image_url": None,
        "created_at": "2026-11-12 10:00:00",
        "status": "published",
        "expires_at": None,
    }
    ad.update(overrides)
    columns = ", ".join(ad)
    parameters = ", ".join(f":{column}" for column in ad)
    statement = text(
        f"INSERT INTO ads ({columns}) VALUES ({parameters})",
    )
    with engine.begin() as connection:
        connection.execute(statement, ad)


@pytest.mark.parametrize(
    "column",
    ["title", "type", "category", "price", "created_at", "status"],
)
def test_ads_requires_all_non_nullable_fields(database_engine, column):
    with pytest.raises(IntegrityError):
        insert_ad(database_engine, **{column: None})


@pytest.mark.parametrize(
    ("column", "value"),
    [
        ("title", " "),
        ("category", ""),
        ("type", "other"),
        ("status", "draft"),
    ],
)
def test_ads_rejects_invalid_constrained_values(
    database_engine,
    column,
    value,
):
    with pytest.raises(IntegrityError):
        insert_ad(database_engine, **{column: value})


def test_ads_allows_optional_description_and_image(database_engine):
    insert_ad(
        database_engine,
        description=None,
        image_url=None,
    )

    with database_engine.connect() as connection:
        row = connection.execute(
            text(
                "SELECT description, image_url FROM ads "
                "WHERE title = :title"
            ),
            {"title": "Bicicleta usada"},
        ).one()

    assert row == (None, None)


def test_default_database_engine_creates_database_directory(
    tmp_path, monkeypatch
):
    database_path = tmp_path / "database" / "db.sqlite3"
    monkeypatch.setattr(database, "_DATABASE_PATH", database_path)

    engine = database.create_database_engine()
    try:
        database.initialize_database(engine)
        assert database_path.is_file()
    finally:
        engine.dispose()


@pytest.mark.parametrize("column", ["nome", "email", "matricula", "vinculo"])
def test_usuarios_requires_all_text_fields(database_engine, column):
    with pytest.raises(IntegrityError):
        insert_usuario(database_engine, **{column: None})


@pytest.mark.parametrize("column", ["nome", "email", "matricula", "vinculo"])
@pytest.mark.parametrize("value", ["", " "])
def test_usuarios_rejects_empty_or_whitespace_only_text(
    database_engine, column, value
):
    with pytest.raises(IntegrityError):
        insert_usuario(database_engine, **{column: value})


def test_usuarios_rejects_duplicate_email(database_engine):
    insert_usuario(database_engine)

    with pytest.raises(IntegrityError):
        insert_usuario(
            database_engine,
            email="ana@aluno.puc-rio.br",
            matricula="456",
        )


def test_usuarios_rejects_duplicate_matricula(database_engine):
    insert_usuario(database_engine)

    with pytest.raises(IntegrityError):
        insert_usuario(
            database_engine,
            email="bia@aluno.puc-rio.br",
            matricula="123",
        )
