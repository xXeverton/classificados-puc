import sqlite3
from collections.abc import Iterator

import pytest

from infra.db.database import initialize_database


@pytest.fixture
def connection() -> Iterator[sqlite3.Connection]:
    database = sqlite3.connect(":memory:")
    initialize_database(database)
    yield database
    database.close()


def insert_usuario(connection, **overrides):
    user = {
        "nome": "Ana",
        "email": "ana@aluno.puc-rio.br",
        "matricula": "123",
        "vinculo": "aluno",
    }
    user.update(overrides)
    columns = ", ".join(user)
    placeholders = ", ".join("?" for _ in user)
    connection.execute(
        f"INSERT INTO usuarios ({columns}) VALUES ({placeholders})",
        tuple(user.values()),
    )


def test_initialize_database_creates_usuarios_table(connection):
    columns = connection.execute("PRAGMA table_info(usuarios)").fetchall()

    assert [column[1] for column in columns] == [
        "id",
        "nome",
        "email",
        "matricula",
        "vinculo",
    ]
    assert {column[1]: column[2] for column in columns} == {
        "id": "INTEGER",
        "nome": "TEXT",
        "email": "TEXT",
        "matricula": "TEXT",
        "vinculo": "TEXT",
    }
    assert next(column[5] for column in columns if column[1] == "id") == 1
    assert all(
        column[3] == 1 for column in columns if column[1] != "id"
    )


@pytest.mark.parametrize("column", ["nome", "email", "matricula", "vinculo"])
def test_usuarios_requires_all_text_fields(connection, column):
    with pytest.raises(sqlite3.IntegrityError):
        insert_usuario(connection, **{column: None})


@pytest.mark.parametrize("column", ["nome", "email", "matricula", "vinculo"])
@pytest.mark.parametrize("value", ["", " "])
def test_usuarios_rejects_empty_or_whitespace_only_text(
    connection, column, value
):
    with pytest.raises(sqlite3.IntegrityError):
        insert_usuario(connection, **{column: value})


def test_usuarios_rejects_duplicate_email(connection):
    insert_usuario(connection)

    with pytest.raises(sqlite3.IntegrityError):
        insert_usuario(
            connection,
            email="ana@aluno.puc-rio.br",
            matricula="456",
        )


def test_usuarios_rejects_duplicate_matricula(connection):
    insert_usuario(connection)

    with pytest.raises(sqlite3.IntegrityError):
        insert_usuario(
            connection,
            email="bia@aluno.puc-rio.br",
            matricula="123",
        )
