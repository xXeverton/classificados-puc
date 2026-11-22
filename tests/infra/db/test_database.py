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


ANUNCIANTE_PADRAO = {"nome_exibicao": "Ana Vendas"}


def insert_anunciante(engine: Engine, usuario_id: int, **overrides) -> int:
    return insert(
        engine,
        "anunciantes",
        {"usuario_id": usuario_id, **ANUNCIANTE_PADRAO, **overrides},
    )


def insert_contato(engine: Engine, anunciante_id: int, /, **overrides) -> int:
    valores = {
        "anunciante_id": anunciante_id,
        "posicao": 0,
        "tipo": "email",
        "valor": "ana@gmail.com",
        "codigo_pais": None,
        "rotulo": None,
    }
    valores.update(overrides)
    return insert(engine, "contatos_anunciante", valores)


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
        "usuario_id",
        "estado_conservacao",
        "preco_a_combinar",
        "image_key",
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
        "usuario_id": "INTEGER",
        "estado_conservacao": "TEXT",
        "preco_a_combinar": "BOOLEAN",
        "image_key": "TEXT",
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


def test_initialize_database_creates_anunciantes_table(database_engine):
    inspector = inspect(database_engine)

    assert {
        column["name"]: (str(column["type"]).upper(), column["nullable"])
        for column in inspector.get_columns("anunciantes")
    } == {
        "id": ("INTEGER", False),
        "usuario_id": ("INTEGER", False),
        "nome_exibicao": ("TEXT", False),
        "foto_url": ("TEXT", True),
    }
    [foreign_key] = inspector.get_foreign_keys("anunciantes")
    assert foreign_key["referred_table"] == "usuarios"
    assert foreign_key["options"].get("ondelete") == "CASCADE"
    assert "AUTOINCREMENT" in create_statement(
        database_engine, "anunciantes"
    ).upper()


def test_initialize_database_creates_contatos_anunciante_table(
    database_engine,
):
    inspector = inspect(database_engine)

    assert {
        column["name"]: (str(column["type"]).upper(), column["nullable"])
        for column in inspector.get_columns("contatos_anunciante")
    } == {
        "id": ("INTEGER", False),
        "anunciante_id": ("INTEGER", False),
        "posicao": ("INTEGER", False),
        "tipo": ("TEXT", False),
        "codigo_pais": ("TEXT", True),
        "valor": ("TEXT", False),
        "rotulo": ("TEXT", True),
    }
    [foreign_key] = inspector.get_foreign_keys("contatos_anunciante")
    assert foreign_key["referred_table"] == "anunciantes"
    assert foreign_key["options"].get("ondelete") == "CASCADE"


def test_advertiser_tables_are_added_to_a_database_that_has_usuarios(
    tmp_path,
):
    engine = database.create_database_engine(
        f"sqlite:///{tmp_path / 'antigo.sqlite3'}"
    )
    try:
        with engine.begin() as connection:
            connection.execute(
                text("CREATE TABLE usuarios (id INTEGER PRIMARY KEY)")
            )
            connection.execute(text("INSERT INTO usuarios (id) VALUES (1)"))

        database.initialize_database(engine)

        assert {"anunciantes", "contatos_anunciante"} <= set(
            inspect(engine).get_table_names()
        )
        assert count(engine, "usuarios") == 1
    finally:
        engine.dispose()


def test_anunciantes_requires_existing_usuario(database_engine):
    with pytest.raises(IntegrityError):
        insert_anunciante(database_engine, 999)


def test_anunciantes_allows_one_profile_per_usuario(database_engine):
    usuario_id = insert_usuario(database_engine)
    insert_anunciante(database_engine, usuario_id)

    with pytest.raises(IntegrityError):
        insert_anunciante(database_engine, usuario_id)


def test_anunciantes_requires_usuario_id_and_display_name(database_engine):
    usuario_id = insert_usuario(database_engine)

    with pytest.raises(IntegrityError):
        insert_anunciante(database_engine, None)
    with pytest.raises(IntegrityError):
        insert_anunciante(database_engine, usuario_id, nome_exibicao=None)


@pytest.mark.parametrize("value", ["", " "])
def test_anunciantes_rejects_blank_display_name_and_photo(
    database_engine, value
):
    usuario_id = insert_usuario(database_engine)

    with pytest.raises(IntegrityError):
        insert_anunciante(database_engine, usuario_id, nome_exibicao=value)
    with pytest.raises(IntegrityError):
        insert_anunciante(database_engine, usuario_id, foto_url=value)


@pytest.fixture
def anunciante_id(database_engine) -> int:
    usuario_id = insert_usuario(database_engine)
    return insert_anunciante(database_engine, usuario_id)


CONTATOS_VALIDOS = {
    "whatsapp_numero": {
        "tipo": "whatsapp", "codigo_pais": "55", "valor": "21999998888",
    },
    "whatsapp_link_wa_me": {
        "tipo": "whatsapp", "valor": "https://wa.me/5521999998888",
    },
    "whatsapp_link_mensagem": {
        "tipo": "whatsapp", "valor": "https://wa.me/message/ABCDEF123456",
    },
    "whatsapp_link_api": {
        "tipo": "whatsapp",
        "valor": "https://api.whatsapp.com/send?phone=5521999998888",
    },
    "telefone": {
        "tipo": "telefone", "codigo_pais": "55", "valor": "2133334444",
    },
    "telefone_8_digitos": {
        "tipo": "telefone", "codigo_pais": "1", "valor": "2345678",
    },
    "telefone_15_digitos": {
        "tipo": "telefone", "codigo_pais": "55", "valor": "1234567890123",
    },
    "email": {"tipo": "email", "valor": "ana@gmail.com"},
    "site": {"tipo": "site", "valor": "https://loja.com.br"},
    "link_sem_rotulo": {"tipo": "link", "valor": "https://x.com/ana"},
    "link_com_rotulo": {
        "tipo": "link", "valor": "https://instagram.com/ana",
        "rotulo": "Instagram",
    },
}


@pytest.mark.parametrize(
    "contato", CONTATOS_VALIDOS.values(), ids=CONTATOS_VALIDOS.keys()
)
def test_contatos_accepts_every_valid_kind(
    database_engine, anunciante_id, contato
):
    insert_contato(database_engine, anunciante_id, **contato)

    assert count(database_engine, "contatos_anunciante") == 1


CONTATOS_INVALIDOS = {
    "tipo_inexistente": {"tipo": "fax", "valor": "123"},
    "valor_vazio": {"valor": ""},
    "valor_so_espacos": {"valor": " "},
    "telefone_sem_codigo_pais": {"tipo": "telefone", "valor": "21999998888"},
    "email_com_codigo_pais": {"codigo_pais": "55"},
    "site_com_codigo_pais": {
        "tipo": "site", "valor": "https://loja.com.br", "codigo_pais": "55",
    },
    "link_com_codigo_pais": {
        "tipo": "link", "valor": "https://x.com/a", "codigo_pais": "55",
    },
    "numero_com_letras": {
        "tipo": "whatsapp", "codigo_pais": "55", "valor": "2199999abcd",
    },
    "numero_com_digitos_nao_ascii": {
        "tipo": "telefone", "codigo_pais": "55",
        "valor": "２１９９９９９８８８８",
    },
    "codigo_pais_com_letras": {
        "tipo": "telefone", "codigo_pais": "5a", "valor": "21999998888",
    },
    "codigo_pais_com_4_digitos": {
        "tipo": "telefone", "codigo_pais": "1234", "valor": "99998888",
    },
    "codigo_pais_vazio": {
        "tipo": "telefone", "codigo_pais": "", "valor": "21999998888",
    },
    "total_7_digitos": {
        "tipo": "telefone", "codigo_pais": "1", "valor": "234567",
    },
    "total_16_digitos": {
        "tipo": "whatsapp", "codigo_pais": "55", "valor": "12345678901234",
    },
    "whatsapp_link_http": {
        "tipo": "whatsapp", "valor": "http://wa.me/5521999998888",
    },
    "whatsapp_link_sem_caminho": {
        "tipo": "whatsapp", "valor": "https://wa.me/",
    },
    "whatsapp_link_host_falso": {
        "tipo": "whatsapp", "valor": "https://wa.me.evil.com/5521999998888",
    },
    "whatsapp_link_com_usuario": {
        "tipo": "whatsapp", "valor": "https://wa.me@evil.com/5521999998888",
    },
    "whatsapp_link_javascript": {
        "tipo": "whatsapp", "valor": "javascript:alert(1)",
    },
    "whatsapp_link_com_espaco": {
        "tipo": "whatsapp", "valor": "https://wa.me/5521 999998888",
    },
    "email_sem_arroba": {"valor": "ana"},
    "email_sem_nome": {"valor": "@gmail.com"},
    "site_http": {"tipo": "site", "valor": "http://loja.com.br"},
    "site_sem_esquema": {"tipo": "site", "valor": "loja.com.br"},
    "site_com_espaco": {"tipo": "site", "valor": "https://loja .com.br"},
    "link_ftp": {"tipo": "link", "valor": "ftp://x.com/a"},
    "rotulo_em_email": {"rotulo": "Meu e-mail"},
    "rotulo_em_site": {
        "tipo": "site", "valor": "https://loja.com.br", "rotulo": "Loja",
    },
    "rotulo_em_branco": {
        "tipo": "link", "valor": "https://x.com/a", "rotulo": " ",
    },
    "posicao_negativa": {"posicao": -1},
}


@pytest.mark.parametrize(
    "contato", CONTATOS_INVALIDOS.values(), ids=CONTATOS_INVALIDOS.keys()
)
def test_contatos_rejects_invalid_values(
    database_engine, anunciante_id, contato
):
    with pytest.raises(IntegrityError):
        insert_contato(database_engine, anunciante_id, **contato)


@pytest.mark.parametrize(
    "coluna", ["anunciante_id", "posicao", "tipo", "valor"]
)
def test_contatos_requires_mandatory_columns(
    database_engine, anunciante_id, coluna
):
    with pytest.raises(IntegrityError):
        insert_contato(database_engine, anunciante_id, **{coluna: None})


def test_contatos_requires_existing_anunciante(database_engine):
    with pytest.raises(IntegrityError):
        insert_contato(database_engine, 999)


def test_contatos_position_is_unique_per_anunciante(
    database_engine, anunciante_id
):
    insert_contato(database_engine, anunciante_id, posicao=0)
    insert_contato(
        database_engine, anunciante_id, posicao=1, valor="outro@gmail.com"
    )

    with pytest.raises(IntegrityError):
        insert_contato(
            database_engine, anunciante_id, posicao=1, valor="x@gmail.com"
        )


def test_contatos_same_position_is_allowed_for_other_anunciante(
    database_engine, anunciante_id
):
    outro_usuario = insert_usuario(
        database_engine,
        email="bia@aluno.puc-rio.br",
        nome_usuario="bia",
        matricula="456",
    )
    outro_anunciante = insert_anunciante(database_engine, outro_usuario)

    insert_contato(database_engine, anunciante_id, posicao=0)
    insert_contato(database_engine, outro_anunciante, posicao=0)

    assert count(database_engine, "contatos_anunciante") == 2


def test_contatos_allows_several_of_the_same_kind(
    database_engine, anunciante_id
):
    for posicao in range(3):
        insert_contato(
            database_engine,
            anunciante_id,
            posicao=posicao,
            tipo="link",
            valor=f"https://loja{posicao}.com.br",
        )

    assert count(database_engine, "contatos_anunciante") == 3


def test_removing_usuario_cascades_to_anunciante_and_contatos(
    database_engine,
):
    usuario_id = insert_usuario(database_engine)
    anunciante = insert_anunciante(database_engine, usuario_id)
    insert_contato(database_engine, anunciante)

    with database_engine.begin() as connection:
        connection.execute(
            text("DELETE FROM usuarios WHERE id = :id"), {"id": usuario_id}
        )

    assert count(database_engine, "anunciantes") == 0
    assert count(database_engine, "contatos_anunciante") == 0


def test_initialize_migrates_existing_ads_without_losing_rows():
    engine = database.create_database_engine("sqlite:///:memory:")
    with engine.begin() as connection:
        connection.exec_driver_sql(
            """
            CREATE TABLE ads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                type TEXT NOT NULL
                    CHECK (type IN ('product', 'service')),
                category TEXT NOT NULL,
                price REAL NOT NULL,
                image_url TEXT,
                created_at DATETIME NOT NULL,
                status TEXT NOT NULL,
                expires_at DATETIME
            )
            """
        )
        connection.execute(
            text(
                "INSERT INTO ads "
                "(title, type, category, price, created_at, status) "
                "VALUES ('Livro antigo', 'product', 'Livros', 12.5, "
                "'2026-11-20 12:00:00', 'published')"
            )
        )

    database.initialize_database(engine)
    database.initialize_database(engine)

    with engine.connect() as connection:
        row = connection.execute(
            text(
                "SELECT title, price, usuario_id, estado_conservacao, "
                "preco_a_combinar, image_key FROM ads"
            )
        ).one()
        version = connection.exec_driver_sql("PRAGMA user_version").scalar()

    assert row == ("Livro antigo", 12.5, None, None, 0, None)
    assert version == 2
    with pytest.raises(IntegrityError):
        with engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO ads "
                    "(title, type, category, price, created_at, status) "
                    "VALUES ('Outro evento', 'invalid', 'evento', 0, "
                    "'2026-11-20 12:00:00', 'published')"
                )
            )
    engine.dispose()
