"""SQLAlchemy adapter that also deletes old expired ads (spec 008)."""

from sqlalchemy import select

from server.core.entities.ad import Ad
from server.core.interfaces.deletable_ad_repository_interface import (
    DeletableAdRepository,
)
from server.infra.db.models import AdModel
from server.infra.gateways.ad_repository_sqlalchemy import (
    AdRepositorySQLAlchemy,
)


class DeletableAdRepositorySQLAlchemy(
    AdRepositorySQLAlchemy, DeletableAdRepository
):
    """Advertisement repository plus listing and deleting expired ads."""

    def list_expired_ads(self) -> list[Ad]:
        with self._session_factory() as session:
            models = session.scalars(
                select(AdModel).where(AdModel.status == "expired")
            ).all()
            return [self._to_entity(model) for model in models]

    def delete_expired(self, ad_ids: list[int]) -> list[str | None]:
        if not ad_ids:
            return []
        with self._session_factory.begin() as session:
            # Re-check the status, so an ad renewed between the listing and
            # this call is not deleted.
            models = session.scalars(
                select(AdModel).where(
                    AdModel.id.in_(ad_ids),
                    AdModel.status == "expired",
                )
            ).all()
            keys = [model.image_key for model in models]
            for model in models:
                session.delete(model)
            return keys
