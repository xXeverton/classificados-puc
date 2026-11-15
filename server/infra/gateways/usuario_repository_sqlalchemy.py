"""SQLAlchemy adapter for the user repository interface."""

from sqlalchemy.orm import Session, sessionmaker

from server.core.entities.usuario import Usuario
from server.core.interfaces.usuario_repository_interface import (
    UsuarioRepositoryInterface,
)
from server.infra.db.models import UsuarioModel


class UsuarioRepositorySQLAlchemy(UsuarioRepositoryInterface):
    """Persist users through SQLAlchemy sessions."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def buscar_por_id(self, usuario_id: int) -> Usuario | None:
        with self._session_factory() as session:
            model = session.get(UsuarioModel, usuario_id)
            if model is None:
                return None
            return self._to_entity(model)

    def salvar(self, usuario: Usuario) -> Usuario:
        with self._session_factory.begin() as session:
            model = (
                session.get(UsuarioModel, usuario.id)
                if usuario.id is not None
                else None
            )
            if model is None:
                model = UsuarioModel(id=usuario.id)
                session.add(model)

            model.nome = usuario.nome
            model.email = usuario.email
            model.matricula = usuario.matricula
            model.vinculo = usuario.vinculo
            session.flush()
            return self._to_entity(model)

    @staticmethod
    def _to_entity(model: UsuarioModel) -> Usuario:
        return Usuario(
            id=model.id,
            nome=model.nome,
            email=model.email,
            matricula=model.matricula,
            vinculo=model.vinculo,
        )
