from datetime import UTC, datetime, timedelta

import pytest

from server.core.entities.sessao import Sessao
from server.core.entities.token_de_confirmacao import TokenDeConfirmacao
from server.core.entities.usuario import Usuario
from server.infra.db.database import create_session_factory
from server.infra.gateways.sessao_repository_sqlalchemy import (
    SessaoRepositorySQLAlchemy,
)
from server.infra.gateways.token_confirmacao_repository_sqlalchemy import (
    TokenConfirmacaoRepositorySQLAlchemy,
)
from server.infra.gateways.usuario_repository_sqlalchemy import (
    UsuarioRepositorySQLAlchemy,
)

AGORA = datetime(2026, 11, 20, 12, 0, tzinfo=UTC)
VALIDADE = timedelta(minutes=15)


@pytest.fixture
def session_factory(database_engine):
    return create_session_factory(database_engine)


@pytest.fixture
def usuario(session_factory) -> Usuario:
    return UsuarioRepositorySQLAlchemy(session_factory).salvar(
        Usuario(
            nome="Ana",
            email="ana@aluno.puc-rio.br",
            nome_usuario="ana",
            vinculo="aluno",
            senha_hash="hash",
        )
    )


@pytest.fixture
def tokens(session_factory):
    return TokenConfirmacaoRepositorySQLAlchemy(session_factory)


@pytest.fixture
def sessoes(session_factory):
    return SessaoRepositorySQLAlchemy(session_factory)


def novo_token(usuario, token_hash="h1", expira_em=AGORA + VALIDADE):
    return TokenDeConfirmacao(
        usuario_id=usuario.id, token_hash=token_hash, expira_em=expira_em
    )


def test_token_repository_saves_and_finds_by_hash(tokens, usuario):
    salvo = tokens.salvar(novo_token(usuario))

    assert salvo.id is not None
    assert tokens.buscar_por_hash("h1") == salvo
    assert tokens.buscar_por_hash("outro") is None


def test_token_repository_updates_usage(tokens, usuario):
    salvo = tokens.salvar(novo_token(usuario))

    tokens.salvar(salvo.usar(AGORA))

    assert tokens.buscar_por_hash("h1").usado_em == AGORA


def test_existe_valido_considers_usage_and_expiration(tokens, usuario):
    assert not tokens.existe_valido_do_usuario(usuario.id, AGORA)

    tokens.salvar(novo_token(usuario))

    assert tokens.existe_valido_do_usuario(usuario.id, AGORA + VALIDADE)
    assert not tokens.existe_valido_do_usuario(
        usuario.id, AGORA + VALIDADE + timedelta(seconds=1)
    )


def test_invalidar_do_usuario_marks_unused_tokens_as_used(tokens, usuario):
    usado_antes = AGORA - timedelta(minutes=1)
    tokens.salvar(novo_token(usuario, "h1").usar(usado_antes))
    tokens.salvar(novo_token(usuario, "h2"))

    tokens.invalidar_do_usuario(usuario.id, AGORA)

    assert tokens.buscar_por_hash("h1").usado_em == usado_antes
    assert tokens.buscar_por_hash("h2").usado_em == AGORA
    assert not tokens.existe_valido_do_usuario(usuario.id, AGORA)


def test_session_repository_saves_finds_and_revokes(sessoes, usuario):
    salva = sessoes.salvar(
        Sessao(
            usuario_id=usuario.id,
            token_hash="s1",
            criada_em=AGORA,
            expira_em=AGORA + timedelta(hours=8),
        )
    )
    assert sessoes.buscar_por_hash("s1") == salva
    assert sessoes.buscar_por_hash("outra") is None

    sessoes.salvar(salva.revogar(AGORA))

    assert not sessoes.buscar_por_hash("s1").esta_ativa(AGORA)


def test_removing_user_removes_its_tokens_and_sessions(
    session_factory, tokens, sessoes, usuario
):
    tokens.salvar(novo_token(usuario))
    sessoes.salvar(
        Sessao(
            usuario_id=usuario.id,
            token_hash="s1",
            criada_em=AGORA,
            expira_em=AGORA + timedelta(hours=8),
        )
    )

    UsuarioRepositorySQLAlchemy(session_factory).remover(usuario.id)

    assert tokens.buscar_por_hash("h1") is None
    assert sessoes.buscar_por_hash("s1") is None
