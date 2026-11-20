from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

from server.core.entities.usuario import Usuario
from server.core.entities.vinculo import Vinculo
from server.infra.db.database import create_session_factory
from server.infra.gateways.usuario_repository_sqlalchemy import (
    UsuarioRepositorySQLAlchemy,
)

AGORA = datetime(2026, 11, 20, 12, 0, tzinfo=UTC)


@pytest.fixture
def repository(database_engine):
    return UsuarioRepositorySQLAlchemy(create_session_factory(database_engine))


def criar_usuario(**overrides) -> Usuario:
    dados = {
        "nome": "Ana",
        "email": "ana@aluno.puc-rio.br",
        "nome_usuario": "ana",
        "matricula": "123",
        "vinculo": Vinculo.ALUNO,
        "senha_hash": "hash",
    }
    dados.update(overrides)
    return Usuario(**dados)


def test_repository_saves_and_retrieves_user(repository):
    saved_user = repository.salvar(criar_usuario())

    assert saved_user.id is not None
    assert repository.buscar_por_id(saved_user.id) == saved_user


def test_repository_persists_account_state_fields(repository):
    saved_user = repository.salvar(criar_usuario())
    atualizado = replace(
        saved_user,
        vinculo=Vinculo.FUNCIONARIO,
        matricula=None,
        confirmado_em=AGORA,
        tentativas_login_falhas=3,
        bloqueado_ate=AGORA + timedelta(minutes=10),
    )

    repository.salvar(atualizado)

    carregado = repository.buscar_por_id(saved_user.id)
    assert carregado == atualizado
    assert carregado.confirmado_em.tzinfo is not None


def test_repository_returns_none_for_unknown_user(repository):
    assert repository.buscar_por_id(999) is None
    assert repository.buscar_por_email("x@aluno.puc-rio.br") is None
    assert repository.buscar_por_identificador_alternativo("x") is None


def test_repository_finds_user_by_email(repository):
    saved_user = repository.salvar(criar_usuario())

    assert repository.buscar_por_email("ana@aluno.puc-rio.br") == saved_user


@pytest.mark.parametrize("valor", ["ana", "123"])
def test_repository_finds_user_by_username_or_matricula(repository, valor):
    saved_user = repository.salvar(criar_usuario())
    repository.salvar(
        criar_usuario(
            email="bia@aluno.puc-rio.br", nome_usuario="bia", matricula=None
        )
    )

    assert repository.buscar_por_identificador_alternativo(valor) == (
        saved_user
    )


def test_repository_removes_user(repository):
    saved_user = repository.salvar(criar_usuario())

    repository.remover(saved_user.id)

    assert repository.buscar_por_id(saved_user.id) is None
