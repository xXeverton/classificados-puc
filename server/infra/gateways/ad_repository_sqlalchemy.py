"""SQLAlchemy adapter for the advertisement repository interface."""

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, sessionmaker

from server.core.entities.ad import Ad
from server.core.interfaces.ad_repository_interface import AdRepository
from server.infra.db.models import AdModel


class AdRepositorySQLAlchemy(AdRepository):
    """Query available advertisements through SQLAlchemy."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

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
        filters = [AdModel.status == "published"]
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
            models = session.scalars(
                select(AdModel)
                .where(*filters)
                .order_by(AdModel.created_at.desc())
                .offset((page - 1) * per_page)
                .limit(per_page)
            ).all()
            return [self._to_entity(model) for model in models], total

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
