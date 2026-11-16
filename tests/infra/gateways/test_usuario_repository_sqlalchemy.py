from server.core.entities.usuario import Usuario
from server.infra.gateways.usuario_repository_sqlalchemy import (
    UsuarioRepositorySQLAlchemy,
)
from server.infra.db.database import create_session_factory


def test_repository_saves_and_retrieves_user(database_engine):
    repository = UsuarioRepositorySQLAlchemy(
        create_session_factory(database_engine)
    )
    usuario = Usuario(
        nome="Ana",
        email="ana@aluno.puc-rio.br",
        matricula="123",
        vinculo="aluno",
    )

    saved_user = repository.salvar(usuario)

    assert saved_user.id is not None
    assert repository.buscar_por_id(saved_user.id) == saved_user


def test_repository_returns_none_for_unknown_user(database_engine):
    repository = UsuarioRepositorySQLAlchemy(
        create_session_factory(database_engine)
    )

    assert repository.buscar_por_id(999) is None
