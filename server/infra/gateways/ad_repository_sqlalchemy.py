"""SQLAlchemy adapter for the advertisement repository interface."""

from datetime import datetime, timezone

from sqlalchemy import func, or_, select, update
from sqlalchemy.orm import Session, sessionmaker

from server.core.entities.ad import Ad
from server.core.entities.anuncio import Anuncio
from server.core.interfaces.ad_repository_interface import AdRepository
from server.core.interfaces.expirable_ad_repository_interface import (
    ExpirableAdRepository,
)
from server.infra.db.models import AdModel, AnuncianteModel
from server.infra.storage.storage import ImageStorage


class AdRepositorySQLAlchemy(AdRepository, ExpirableAdRepository):
    """Query, publish, and expire advertisements through SQLAlchemy."""

    def __init__(
        self,
        session_factory: sessionmaker[Session],
        image_storage: ImageStorage | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._image_storage = image_storage

    def buscar_por_id(self, anuncio_id: int) -> Ad | None:
        with self._session_factory() as session:
            model = session.scalars(
                select(AdModel).where(AdModel.id == anuncio_id)
            ).one_or_none()
            if model is None:
                return None
            return self._to_entity(model)

    def list_published(
        self,
        page: int,
        per_page: int,
        search: str | None,
        ad_type: str | None,
        category: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
    ) -> tuple[list[Ad], int]:
        agora = datetime.now(timezone.utc)
        filters = [
            AdModel.status == "published",
            or_(
                AdModel.expires_at.is_(None),
                AdModel.expires_at > agora,
            ),
        ]
        if category is not None:
            filters.append(
                func.lower(AdModel.category) == category.lower()
            )
        if min_price is not None:
            filters.append(AdModel.price >= min_price)
        if max_price is not None:
            filters.append(AdModel.price <= max_price)
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

    def list_published_ads(self) -> list[Ad]:
        with self._session_factory() as session:
            models = session.scalars(
                select(AdModel).where(AdModel.status == "published")
            ).all()
            return [self._to_entity(model) for model in models]

    def mark_as_expired(self, ad_ids: list[int]) -> int:
        if not ad_ids:
            return 0
        with self._session_factory.begin() as session:
            result = session.execute(
                update(AdModel)
                .where(
                    AdModel.id.in_(ad_ids),
                    AdModel.status == "published",
                )
                .values(status="expired")
            )
            return result.rowcount

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
        created_at = model.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        else:
            created_at = created_at.astimezone(timezone.utc)
        return Ad(
            id=model.id,
            title=model.title,
            description=model.description,
            type=model.type,
            category=model.category,
            price=None if model.preco_a_combinar else model.price,
            image_url=image_url,
            created_at=created_at,
            status=model.status,
            expires_at=model.expires_at,
            nome_anunciante=nome_anunciante,
            estado_conservacao=model.estado_conservacao,
            preco_a_combinar=model.preco_a_combinar,
            usuario_id=model.usuario_id,
        )
