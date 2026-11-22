"""SQLAlchemy adapter for the user repository interface."""

from sqlalchemy import delete, or_, select
from sqlalchemy.orm import Session, sessionmaker

from server.core.entities.usuario import Usuario
from server.core.interfaces.usuario_repository_interface import (
    UsuarioRepositoryInterface,
)
from server.infra.db.models import UsuarioModel


class UsuarioRepositorySQLAlchemy(UsuarioRepositoryInterface):
    """Persist users through SQLAlchemy sessions.

    Lookups compare stored values as-is: the `Usuario` entity normalizes
    e-mail, username, and registration before they are saved.
    """

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def buscar_por_id(self, usuario_id: int) -> Usuario | None:
        with self._session_factory() as session:
            model = session.get(UsuarioModel, usuario_id)
            return None if model is None else self._to_entity(model)

    def buscar_por_email(self, email: str) -> Usuario | None:
        return self._buscar_um(UsuarioModel.email == email)

    def buscar_por_identificador_alternativo(
        self, valor: str
    ) -> Usuario | None:
        return self._buscar_um(
            or_(
                UsuarioModel.nome_usuario == valor,
                UsuarioModel.matricula == valor,
            )
        )

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
            model.nome_usuario = usuario.nome_usuario
            model.matricula = usuario.matricula
            model.vinculo = usuario.vinculo.value
            model.senha_hash = usuario.senha_hash
            model.confirmado_em = usuario.confirmado_em
            model.tentativas_login_falhas = usuario.tentativas_login_falhas
            model.bloqueado_ate = usuario.bloqueado_ate
            session.flush()
            return self._to_entity(model)

    def remover(self, usuario_id: int) -> None:
        with self._session_factory.begin() as session:
            session.execute(
                delete(UsuarioModel).where(UsuarioModel.id == usuario_id)
            )

    def _buscar_um(self, condicao) -> Usuario | None:
        with self._session_factory() as session:
            model = session.scalars(
                select(UsuarioModel).where(condicao)
            ).one_or_none()
            return None if model is None else self._to_entity(model)

    @staticmethod
    def _to_entity(model: UsuarioModel) -> Usuario:
        return Usuario(
            id=model.id,
            nome=model.nome,
            email=model.email,
            nome_usuario=model.nome_usuario,
            matricula=model.matricula,
            vinculo=model.vinculo,
            senha_hash=model.senha_hash,
            confirmado_em=model.confirmado_em,
            tentativas_login_falhas=model.tentativas_login_falhas,
            bloqueado_ate=model.bloqueado_ate,
        )
