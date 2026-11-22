"""SQLAlchemy adapter for the advertisement repository interface."""

from sqlalchemy import func, or_, select, update
from sqlalchemy.orm import Session, sessionmaker

from server.core.entities.ad import Ad
from server.core.interfaces.ad_repository_interface import AdRepository
from server.core.interfaces.expirable_ad_repository_interface import (
    ExpirableAdRepository,
)
from server.infra.db.models import AdModel


class AdRepositorySQLAlchemy(AdRepository, ExpirableAdRepository):
    """Query and expire advertisements through SQLAlchemy."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def list_published(
        self,
        page: int,
        per_page: int,
        search: str | None,
        ad_type: str | None,
    ) -> tuple[list[Ad], int]:
        filters = [AdModel.status == "published"]
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
            models = session.scalars(
                select(AdModel)
                .where(*filters)
                .order_by(AdModel.created_at.desc())
                .offset((page - 1) * per_page)
                .limit(per_page)
            ).all()
            return [self._to_entity(model) for model in models], total

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

    @staticmethod
    def _to_entity(model: AdModel) -> Ad:
        return Ad(
            id=model.id,
            title=model.title,
            description=model.description,
            type=model.type,
            category=model.category,
            price=model.price,
            image_url=model.image_url,
            created_at=model.created_at,
            status=model.status,
            expires_at=model.expires_at,
        )
