import sqlite3
from collections.abc import Iterator
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
import re
import time

import pytest

from domain.anuncio import (
    CATEGORIAS,
    ESTADOS_CONSERVACAO,
    Anuncio,
)
from infra.db.database import connect_database, initialize_database


@pytest.fixture
def connection() -> Iterator[sqlite3.Connection]:
    database = connect_database(":memory:")
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
    return connection.execute("SELECT last_insert_rowid()").fetchone()[0]


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
    assert connection.execute("PRAGMA user_version").fetchone()[0] == 1


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


def insert_anuncio(connection, **overrides):
    anuncio = {
        "titulo": "Bicicleta urbana",
        "descricao": "Em bom estado.",
        "preco": "100.00",
        "categoria": "produto",
        "estado_conservacao": "novo",
    }
    if "id_anunciante" not in overrides:
        user_count = connection.execute(
            "SELECT COUNT(*) FROM usuarios"
        ).fetchone()[0]
        anuncio["id_anunciante"] = insert_usuario(
            connection,
            email=f"ana-{user_count}@aluno.puc-rio.br",
            matricula=f"seed-{user_count}",
        )
    anuncio.update(overrides)
    columns = ", ".join(anuncio)
    placeholders = ", ".join("?" for _ in anuncio)
    return connection.execute(
        f"INSERT INTO anuncios ({columns}) VALUES ({placeholders})",
        tuple(anuncio.values()),
    )


def test_initialize_database_creates_anuncios_and_indexes(connection):
    columns = connection.execute("PRAGMA table_info(anuncios)").fetchall()
    indexes = {
        row[1] for row in connection.execute("PRAGMA index_list(anuncios)")
    }
    foreign_key = connection.execute(
        "PRAGMA foreign_key_list(anuncios)"
    ).fetchone()

    assert [column[1] for column in columns] == [
        "id",
        "id_anunciante",
        "titulo",
        "descricao",
        "preco",
        "categoria",
        "estado_conservacao",
        "created_at",
    ]
    assert {
        "idx_anuncios_id_anunciante",
        "idx_anuncios_categoria",
        "idx_anuncios_created_at",
        "idx_anuncios_categoria_created_at",
    } <= indexes
    assert foreign_key[2:4] == ("usuarios", "id_anunciante")
    assert foreign_key[6] == "CASCADE"
    tables = {
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
        )
    }
    assert tables == {"usuarios", "anuncios"}


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("preco", "-0.01"),
        ("preco", "10000000000.00"),
        ("preco", "1.001"),
        ("preco", "not-a-number"),
        ("categoria", "outro"),
        ("estado_conservacao", "quebrado"),
        ("titulo", ""),
        ("titulo", "abcd"),
        ("titulo", " titulo"),
        ("titulo", "titulo "),
        ("titulo", "x" * 81),
        ("descricao", ""),
        ("descricao", "   "),
        ("descricao", "x" * 501),
    ],
)
def test_anuncios_reject_invalid_values(connection, field, value):
    with pytest.raises(sqlite3.IntegrityError):
        insert_anuncio(connection, **{field: value})


def test_anuncios_accepts_zero_price_and_sets_utc_timestamp(connection):
    user_id = insert_usuario(connection)
    connection.execute(
        """
        INSERT INTO anuncios (
            id_anunciante, titulo, descricao, preco, categoria
        ) VALUES (?, 'Item gratis', 'Item sem custo', 0, 'evento')
        """,
        (user_id,),
    )

    price, created_at = connection.execute(
        "SELECT preco, created_at FROM anuncios"
    ).fetchone()
    assert price == 0
    assert re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z", created_at
    )
    parsed = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    assert parsed.tzinfo == timezone.utc


@pytest.mark.parametrize("categoria", CATEGORIAS)
def test_anuncios_accept_each_category(connection, categoria):
    insert_anuncio(connection, categoria=categoria, estado_conservacao=None)


@pytest.mark.parametrize("estado", ESTADOS_CONSERVACAO)
def test_anuncios_accept_each_conservation_state(connection, estado):
    insert_anuncio(connection, estado_conservacao=estado)


def test_anuncios_accept_null_price_and_maximum_price(connection):
    insert_anuncio(connection, preco=None)
    insert_anuncio(
        connection,
        titulo="Preco maximo permitido",
        preco="9999999999.99",
    )

    prices = connection.execute(
        "SELECT preco FROM anuncios ORDER BY id"
    ).fetchall()
    assert prices == [(None,), (9999999999.99,)]


def test_anuncios_accept_title_and_description_boundaries(connection):
    insert_anuncio(connection, titulo="abcde", descricao="x" * 500)
    insert_anuncio(
        connection,
        titulo="x" * 80,
        descricao="Descricao valida",
        categoria="evento",
        estado_conservacao=None,
    )

    assert connection.execute(
        "SELECT COUNT(*) FROM anuncios"
    ).fetchone()[0] == 2


def test_anuncios_feed_joins_user_and_orders_newest_first(connection):
    user_id = insert_usuario(connection)
    older_id = insert_anuncio(
        connection,
        id_anunciante=user_id,
        titulo="Anuncio mais antigo",
        categoria="produto",
    ).lastrowid
    time.sleep(0.01)
    newer_id = insert_anuncio(
        connection,
        id_anunciante=user_id,
        titulo="Anuncio mais recente",
        categoria="evento",
        estado_conservacao=None,
    ).lastrowid

    feed = connection.execute(
        """
        SELECT anuncios.id, anuncios.created_at, usuarios.nome
        FROM anuncios
        JOIN usuarios ON usuarios.id = anuncios.id_anunciante
        ORDER BY anuncios.created_at DESC
        """
    ).fetchall()

    assert [row[0] for row in feed] == [newer_id, older_id]
    assert all(row[2] == "Ana" for row in feed)
    assert feed[0][1] >= feed[1][1]


def test_anuncios_require_existing_user_and_cascade_on_delete(connection):
    with pytest.raises(sqlite3.IntegrityError):
        insert_anuncio(connection, id_anunciante=999)

    user_id = insert_usuario(connection)
    insert_anuncio(connection, id_anunciante=user_id)
    connection.execute("DELETE FROM usuarios WHERE id = ?", (user_id,))

    assert connection.execute(
        "SELECT COUNT(*) FROM anuncios"
    ).fetchone()[0] == 0


def test_user_without_announcements_is_valid(connection):
    user_id = insert_usuario(connection)

    assert connection.execute(
        "SELECT COUNT(*) FROM anuncios WHERE id_anunciante = ?", (user_id,)
    ).fetchone()[0] == 0


def test_foreign_keys_are_enabled_on_each_new_connection(tmp_path):
    database_path = tmp_path / "classifieds.sqlite"
    first_connection = connect_database(database_path)
    initialize_database(first_connection)
    first_connection.close()

    second_connection = connect_database(database_path)
    try:
        foreign_keys_enabled = second_connection.execute(
            "PRAGMA foreign_keys"
        ).fetchone()[0]
        assert foreign_keys_enabled == 1
        with pytest.raises(sqlite3.IntegrityError):
            insert_anuncio(second_connection, id_anunciante=999)
    finally:
        second_connection.close()


def test_anuncios_migration_down_up_and_initialization_is_idempotent(
    connection,
):
    migration_dir = Path(__file__).parents[3] / "infra" / "db" / "migrations"
    down = (migration_dir / "0001_create_anuncios.down.sql").read_text(
        encoding="utf-8"
    )
    connection.executescript(down)

    assert connection.execute("PRAGMA user_version").fetchone()[0] == 0
    assert connection.execute(
        "SELECT 1 FROM sqlite_master "
        "WHERE type = 'table' AND name = 'anuncios'"
    ).fetchone() is None

    initialize_database(connection)
    indexes = {
        row[1] for row in connection.execute("PRAGMA index_list(anuncios)")
    }
    assert {
        "idx_anuncios_id_anunciante",
        "idx_anuncios_categoria",
        "idx_anuncios_created_at",
        "idx_anuncios_categoria_created_at",
    } <= indexes
    assert connection.execute("PRAGMA user_version").fetchone()[0] == 1

    initialize_database(connection)
    assert connection.execute("PRAGMA user_version").fetchone()[0] == 1
    assert connection.execute(
        "PRAGMA foreign_key_list(anuncios)"
    ).fetchone()[2] == "usuarios"


def test_anuncios_queries_use_expected_indexes(connection):
    user_ids = [
        insert_usuario(
            connection,
            email=f"user{index}@example.com",
            matricula=f"matricula-{index}",
        )
        for index in range(20)
    ]
    for index in range(100):
        connection.execute(
            """
            INSERT INTO anuncios (
                id_anunciante, titulo, descricao, preco, categoria
            ) VALUES (?, ?, 'Descricao', ?, ?)
            """,
            (
                user_ids[index % len(user_ids)],
                f"Produto de teste {index:03}",
                str(index),
                CATEGORIAS[index % len(CATEGORIAS)],
            ),
        )
    connection.execute("ANALYZE")

    plans = {
        "usuario": connection.execute(
            "EXPLAIN QUERY PLAN "
            "SELECT * FROM anuncios WHERE id_anunciante = ?",
            (user_ids[0],),
        ).fetchone()[3],
        "categoria": connection.execute(
            "EXPLAIN QUERY PLAN "
            "SELECT * FROM anuncios WHERE categoria = ?",
            ("produto",),
        ).fetchone()[3],
        "recentes": connection.execute(
            "EXPLAIN QUERY PLAN "
            "SELECT * FROM anuncios ORDER BY created_at DESC"
        ).fetchone()[3],
    }

    assert "idx_anuncios_id_anunciante" in plans["usuario"]
    assert "idx_anuncios_categoria" in plans["categoria"]
    assert "idx_anuncios_created_at" in plans["recentes"]


def test_anuncios_seed_loads_in_empty_database(connection):
    seed = (
        Path(__file__).parents[3]
        / "infra"
        / "db"
        / "seeds"
        / "anuncios.sql"
    ).read_text(encoding="utf-8")
    connection.executescript(seed)

    assert connection.execute(
        "SELECT COUNT(*) FROM anuncios"
    ).fetchone()[0] == 3
    assert connection.execute(
        "SELECT COUNT(*) FROM anuncios WHERE preco = 0"
    ).fetchone()[0] == 1


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("titulo", ""),
        ("titulo", "abcd"),
        ("titulo", " titulo"),
        ("titulo", "x" * 81),
        ("descricao", ""),
        ("descricao", "   "),
        ("descricao", "x" * 501),
        ("preco", Decimal("-0.01")),
        ("preco", Decimal("10000000000.00")),
        ("preco", Decimal("1.001")),
        ("preco", 1.00),
        ("categoria", "other"),
        ("estado_conservacao", "danificado"),
    ],
)
def test_anuncio_model_validates_fields(field, value):
    values = {
        "id_anunciante": 1,
        "titulo": "Bicicleta urbana",
        "descricao": "Em bom estado.",
        "preco": Decimal("10.00"),
        "categoria": "produto",
    }
    values[field] = value

    with pytest.raises((TypeError, ValueError)):
        Anuncio(**values)


def test_anuncio_model_accepts_zero_price():
    anuncio = Anuncio(
        id_anunciante=1,
        titulo="Doacao gratuita",
        descricao="Item gratuito",
        preco=Decimal("0.00"),
        categoria="produto",
        estado_conservacao=None,
    )

    assert anuncio.preco == Decimal("0.00")
