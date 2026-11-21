"""SQLAlchemy adapter for confirmation tokens."""

from datetime import datetime

from sqlalchemy import exists, select, update
from sqlalchemy.orm import Session, sessionmaker

from server.core.entities.token_de_confirmacao import TokenDeConfirmacao
from server.core.interfaces.token_de_confirmacao_repository_interface import (
    TokenDeConfirmacaoRepositoryInterface,
)
from server.infra.db.models import TokenDeConfirmacaoModel

Model = TokenDeConfirmacaoModel


class TokenConfirmacaoRepositorySQLAlchemy(
    TokenDeConfirmacaoRepositoryInterface
):

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def salvar(self, token: TokenDeConfirmacao) -> TokenDeConfirmacao:
        with self._session_factory.begin() as session:
            model = (
                session.get(Model, token.id) if token.id is not None else None
            )
            if model is None:
                model = Model(id=token.id)
                session.add(model)

            model.usuario_id = token.usuario_id
            model.token_hash = token.token_hash
            model.expira_em = token.expira_em
            model.usado_em = token.usado_em
            session.flush()
            return self._to_entity(model)

    def buscar_por_hash(self, token_hash: str) -> TokenDeConfirmacao | None:
        with self._session_factory() as session:
            model = session.scalars(
                select(Model).where(Model.token_hash == token_hash)
            ).one_or_none()
            return None if model is None else self._to_entity(model)

    def invalidar_do_usuario(self, usuario_id: int, agora: datetime) -> None:
        with self._session_factory.begin() as session:
            session.execute(
                update(Model)
                .where(Model.usuario_id == usuario_id)
                .where(Model.usado_em.is_(None))
                .values(usado_em=agora)
            )

    def existe_valido_do_usuario(
        self, usuario_id: int, agora: datetime
    ) -> bool:
        with self._session_factory() as session:
            return session.scalar(
                select(
                    exists()
                    .where(Model.usuario_id == usuario_id)
                    .where(Model.usado_em.is_(None))
                    .where(Model.expira_em >= agora)
                )
            )

    @staticmethod
    def _to_entity(model: Model) -> TokenDeConfirmacao:
        return TokenDeConfirmacao(
            id=model.id,
            usuario_id=model.usuario_id,
            token_hash=model.token_hash,
            expira_em=model.expira_em,
            usado_em=model.usado_em,
        )
