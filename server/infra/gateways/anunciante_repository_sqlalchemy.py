"""SQLAlchemy adapter for advertiser profiles and their contacts."""

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, sessionmaker

from server.core.entities.anunciante import Anunciante
from server.core.entities.contato import Contato
from server.core.interfaces.anunciante_repository_interface import (
    AnuncianteRepositoryInterface,
)
from server.infra.db.models import AnuncianteModel, ContatoAnuncianteModel


class AnuncianteRepositorySQLAlchemy(AnuncianteRepositoryInterface):

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def buscar_por_usuario_id(self, usuario_id: int) -> Anunciante | None:
        with self._session_factory() as session:
            model = self._buscar_model(session, usuario_id)
            return None if model is None else self._to_entity(session, model)

    def salvar(self, anunciante: Anunciante) -> Anunciante:
        """Save the profile and replace its contacts in one transaction."""
        with self._session_factory.begin() as session:
            model = self._buscar_model(session, anunciante.usuario_id)
            if model is None:
                model = AnuncianteModel(usuario_id=anunciante.usuario_id)
                session.add(model)

            model.nome_exibicao = anunciante.nome_exibicao
            model.foto_url = anunciante.foto_url
            session.flush()

            session.execute(
                delete(ContatoAnuncianteModel).where(
                    ContatoAnuncianteModel.anunciante_id == model.id
                )
            )
            session.add_all(
                ContatoAnuncianteModel(
                    anunciante_id=model.id,
                    posicao=posicao,
                    tipo=contato.tipo.value,
                    codigo_pais=contato.codigo_pais,
                    valor=contato.valor,
                    rotulo=contato.rotulo,
                )
                for posicao, contato in enumerate(anunciante.contatos)
            )
            session.flush()
            return self._to_entity(session, model)

    @staticmethod
    def _buscar_model(
        session: Session, usuario_id: int
    ) -> AnuncianteModel | None:
        return session.scalars(
            select(AnuncianteModel).where(
                AnuncianteModel.usuario_id == usuario_id
            )
        ).one_or_none()

    @staticmethod
    def _to_entity(session: Session, model: AnuncianteModel) -> Anunciante:
        contatos = session.scalars(
            select(ContatoAnuncianteModel)
            .where(ContatoAnuncianteModel.anunciante_id == model.id)
            .order_by(ContatoAnuncianteModel.posicao)
        ).all()
        return Anunciante(
            id=model.id,
            usuario_id=model.usuario_id,
            nome_exibicao=model.nome_exibicao,
            contatos=tuple(
                Contato(
                    tipo=contato.tipo,
                    valor=contato.valor,
                    codigo_pais=contato.codigo_pais,
                    rotulo=contato.rotulo,
                )
                for contato in contatos
            ),
            foto_url=model.foto_url,
        )
