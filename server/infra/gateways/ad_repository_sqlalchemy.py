"""SQLAlchemy adapter for the advertisement repository interface."""

from datetime import datetime, timezone
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, sessionmaker

from server.core.entities.ad import Ad
from server.core.entities.anuncio import Anuncio
from server.core.interfaces.ad_repository_interface import AdRepository
from server.infra.db.models import AdModel, AnuncianteModel
from server.infra.storage.storage import ImageStorage


class AdRepositorySQLAlchemy(AdRepository):
    """Query available advertisements through SQLAlchemy."""

    def __init__(
        self,
        session_factory: sessionmaker[Session],
        image_storage: ImageStorage | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._image_storage = image_storage

    def list_published(
        self,
        page: int,
        per_page: int,
        search: str | None,
        ad_type: str | None,
    ) -> tuple[list[Ad], int]:
        agora = datetime.now(timezone.utc).replace(tzinfo=None)
        filters = [
            AdModel.status == "published",
            or_(
                AdModel.expires_at.is_(None),
                AdModel.expires_at > agora,
            ),
        ]
        if ad_type not in (None, "all"):
            filters.append(AdModel.type == ad_type)
        if search is not None:
            search_term = search.lower()
            filters.append(
                or_(
                    func.lower(AdModel.title).contains(search_term),
                    func.lower(AdModel.description).contains(search_term),
                    func.lower(AdModel.category).contains(search_term),
                )
            )

        with self._session_factory() as session:
            total = session.scalar(
                select(func.count())
                .select_from(AdModel)
                .where(*filters)
            ) or 0
            rows = session.execute(
                select(AdModel, AnuncianteModel.nome_exibicao)
                .outerjoin(
                    AnuncianteModel,
                    AnuncianteModel.usuario_id == AdModel.usuario_id,
                )
                .where(*filters)
                .order_by(AdModel.created_at.desc())
                .offset((page - 1) * per_page)
                .limit(per_page)
            ).all()
            return [
                self._to_entity(model, nome_anunciante)
                for model, nome_anunciante in rows
            ], total

    def publish(
        self,
        anuncio: Anuncio,
        nome_anunciante: str,
        criado_em: datetime,
        expira_em: datetime,
    ) -> Ad:
        tipo = {
            "produto": "product",
            "servico": "service",
            "evento": "event",
        }[anuncio.categoria]
        model = AdModel(
            title=anuncio.titulo,
            description=anuncio.descricao,
            type=tipo,
            category=anuncio.categoria,
            price=float(anuncio.preco or 0),
            image_url=None,
            created_at=criado_em,
            status="published",
            expires_at=expira_em,
            usuario_id=anuncio.usuario_id,
            estado_conservacao=anuncio.estado_conservacao,
            preco_a_combinar=anuncio.preco is None,
            image_key=anuncio.image_key,
        )
        with self._session_factory.begin() as session:
            session.add(model)
            session.flush()
            return self._to_entity(model, nome_anunciante)

    def _to_entity(
        self, model: AdModel, nome_anunciante: str | None = None
    ) -> Ad:
        image_url = model.image_url
        if model.image_key is not None and self._image_storage is not None:
            image_url = self._image_storage.obter_url(model.image_key)
        return Ad(
            id=model.id,
            title=model.title,
            description=model.description,
            type=model.type,
            category=model.category,
            price=None if model.preco_a_combinar else model.price,
            image_url=image_url,
            created_at=model.created_at,
            status=model.status,
            expires_at=model.expires_at,
            nome_anunciante=nome_anunciante,
            estado_conservacao=model.estado_conservacao,
            preco_a_combinar=model.preco_a_combinar,
        )
