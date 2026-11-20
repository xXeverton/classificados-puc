"""SQLAlchemy adapter for authenticated sessions."""

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from server.core.entities.sessao import Sessao
from server.core.interfaces.sessao_repository_interface import (
    SessaoRepositoryInterface,
)
from server.infra.db.models import SessaoModel


class SessaoRepositorySQLAlchemy(SessaoRepositoryInterface):

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def salvar(self, sessao: Sessao) -> Sessao:
        with self._session_factory.begin() as session:
            model = (
                session.get(SessaoModel, sessao.id)
                if sessao.id is not None
                else None
            )
            if model is None:
                model = SessaoModel(id=sessao.id)
                session.add(model)

            model.usuario_id = sessao.usuario_id
            model.token_hash = sessao.token_hash
            model.criada_em = sessao.criada_em
            model.expira_em = sessao.expira_em
            model.revogada_em = sessao.revogada_em
            session.flush()
            return self._to_entity(model)

    def buscar_por_hash(self, token_hash: str) -> Sessao | None:
        with self._session_factory() as session:
            model = session.scalars(
                select(SessaoModel).where(SessaoModel.token_hash == token_hash)
            ).one_or_none()
            return None if model is None else self._to_entity(model)

    @staticmethod
    def _to_entity(model: SessaoModel) -> Sessao:
        return Sessao(
            id=model.id,
            usuario_id=model.usuario_id,
            token_hash=model.token_hash,
            criada_em=model.criada_em,
            expira_em=model.expira_em,
            revogada_em=model.revogada_em,
        )
