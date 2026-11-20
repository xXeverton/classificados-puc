import pytest
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine import Engine

from server.infra.db import database

USUARIO_PADRAO = {
    "nome": "Ana",
    "email": "ana@aluno.puc-rio.br",
    "nome_usuario": "ana",
    "matricula": "123",
    "vinculo": "aluno",
    "senha_hash": "hash",
}


def insert(engine: Engine, table: str, values: dict) -> int:
    columns = ", ".join(values)
    parameters = ", ".join(f":{column}" for column in values)
    with engine.begin() as connection:
        result = connection.execute(
            text(f"INSERT INTO {table} ({columns}) VALUES ({parameters})"),
            values,
        )
        return result.lastrowid


def insert_usuario(engine: Engine, **overrides) -> int:
    return insert(engine, "usuarios", {**USUARIO_PADRAO, **overrides})


def insert_token(engine: Engine, usuario_id: int, token_hash="t") -> int:
    return insert(
        engine,
        "tokens_confirmacao",
        {
            "usuario_id": usuario_id,
            "token_hash": token_hash,
            "expira_em": "2026-11-20 12:15:00.000000",
        },
    )


def insert_sessao(engine: Engine, usuario_id: int, token_hash="s") -> int:
    return insert(
        engine,
        "sessoes",
        {
            "usuario_id": usuario_id,
            "token_hash": token_hash,
            "criada_em": "2026-11-20 12:00:00.000000",
            "expira_em": "2026-11-20 20:00:00.000000",
        },
    )


def count(engine: Engine, table: str) -> int:
    with engine.connect() as connection:
        return connection.execute(
            text(f"SELECT count(*) FROM {table}")
        ).scalar_one()


def create_statement(engine: Engine, table: str) -> str:
    with engine.connect() as connection:
        return connection.execute(
            text(
                "SELECT sql FROM sqlite_master "
                "WHERE type = 'table' AND name = :table"
            ),
            {"table": table},
        ).scalar_one()


def test_initialize_database_creates_usuarios_table(database_engine):
    columns = inspect(database_engine).get_columns("usuarios")

    assert {
        column["name"]: (str(column["type"]).upper(), column["nullable"])
        for column in columns
    } == {
        "id": ("INTEGER", False),
        "nome": ("TEXT", False),
        "email": ("TEXT", False),
        "nome_usuario": ("TEXT", False),
        "matricula": ("TEXT", True),
        "vinculo": ("TEXT", False),
        "senha_hash": ("TEXT", False),
        "confirmado_em": ("DATETIME", True),
        "tentativas_login_falhas": ("INTEGER", False),
        "bloqueado_ate": ("DATETIME", True),
    }
    assert columns[0]["primary_key"] == 1
    assert "AUTOINCREMENT" in create_statement(
        database_engine, "usuarios"
    ).upper()


@pytest.mark.parametrize(
    ("table", "columns"),
    [
        (
            "tokens_confirmacao",
            ["id", "usuario_id", "token_hash", "expira_em", "usado_em"],
        ),
        (
            "sessoes",
            [
                "id", "usuario_id", "token_hash", "criada_em", "expira_em",
                "revogada_em",
            ],
        ),
    ],
)
def test_initialize_database_creates_token_tables(
    database_engine, table, columns
):
    inspector = inspect(database_engine)

    assert [c["name"] for c in inspector.get_columns(table)] == columns
    [foreign_key] = inspector.get_foreign_keys(table)
    assert foreign_key["referred_table"] == "usuarios"
    assert foreign_key["options"].get("ondelete") == "CASCADE"


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


def test_sqlite_foreign_keys_pragma_is_enabled(database_engine):
    with database_engine.connect() as connection:
        assert connection.execute(
            text("PRAGMA foreign_keys")
        ).scalar_one() == 1


@pytest.mark.parametrize(
    "column", ["nome", "email", "nome_usuario", "vinculo", "senha_hash"]
)
def test_usuarios_requires_mandatory_text_fields(database_engine, column):
    with pytest.raises(IntegrityError):
        insert_usuario(database_engine, **{column: None})


@pytest.mark.parametrize(
    "column",
    ["nome", "email", "nome_usuario", "matricula", "senha_hash"],
)
@pytest.mark.parametrize("value", ["", " "])
def test_usuarios_rejects_empty_or_whitespace_only_text(
    database_engine, column, value
):
    with pytest.raises(IntegrityError):
        insert_usuario(database_engine, **{column: value})


def test_usuarios_defaults_to_zero_failed_logins(database_engine):
    insert_usuario(database_engine)

    with database_engine.connect() as connection:
        assert connection.execute(
            text("SELECT tentativas_login_falhas FROM usuarios")
        ).scalar_one() == 0


def test_usuarios_rejects_negative_failed_logins(database_engine):
    with pytest.raises(IntegrityError):
        insert_usuario(database_engine, tentativas_login_falhas=-1)


def test_usuarios_rejects_at_sign_in_nome_usuario(database_engine):
    with pytest.raises(IntegrityError):
        insert_usuario(database_engine, nome_usuario="ana@puc")


@pytest.mark.parametrize("vinculo", ["aluno", "funcionario"])
def test_usuarios_accepts_known_vinculo(database_engine, vinculo):
    insert_usuario(database_engine, vinculo=vinculo)


@pytest.mark.parametrize("vinculo", ["", "terceirizado", "Aluno"])
def test_usuarios_rejects_unknown_vinculo(database_engine, vinculo):
    with pytest.raises(IntegrityError):
        insert_usuario(database_engine, vinculo=vinculo)


def test_usuarios_allows_many_null_matriculas(database_engine):
    insert_usuario(database_engine, matricula=None)
    insert_usuario(
        database_engine,
        email="bia@aluno.puc-rio.br",
        nome_usuario="bia",
        matricula=None,
    )

    assert count(database_engine, "usuarios") == 2


@pytest.mark.parametrize(
    "overrides",
    [
        {"nome_usuario": "bia", "matricula": "456"},
        {"email": "bia@aluno.puc-rio.br", "matricula": "456"},
        {"email": "bia@aluno.puc-rio.br", "nome_usuario": "bia"},
    ],
    ids=["email", "nome_usuario", "matricula"],
)
def test_usuarios_rejects_duplicate_unique_values(database_engine, overrides):
    insert_usuario(database_engine)

    with pytest.raises(IntegrityError):
        insert_usuario(database_engine, **overrides)


@pytest.mark.parametrize("table", ["tokens_confirmacao", "sessoes"])
def test_token_hash_is_unique(database_engine, table):
    usuario_id = insert_usuario(database_engine)
    inserir = insert_token if table == "tokens_confirmacao" else insert_sessao
    inserir(database_engine, usuario_id, "mesmo")

    with pytest.raises(IntegrityError):
        inserir(database_engine, usuario_id, "mesmo")


@pytest.mark.parametrize("table", ["tokens_confirmacao", "sessoes"])
def test_token_requires_existing_usuario(database_engine, table):
    inserir = insert_token if table == "tokens_confirmacao" else insert_sessao

    with pytest.raises(IntegrityError):
        inserir(database_engine, 999)


def test_removing_usuario_cascades_to_tokens_and_sessions(database_engine):
    usuario_id = insert_usuario(database_engine)
    insert_token(database_engine, usuario_id)
    insert_sessao(database_engine, usuario_id)

    with database_engine.begin() as connection:
        connection.execute(
            text("DELETE FROM usuarios WHERE id = :id"), {"id": usuario_id}
        )

    assert count(database_engine, "tokens_confirmacao") == 0
    assert count(database_engine, "sessoes") == 0
