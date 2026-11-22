"""Use case that deletes expired ads kept past their retention period."""

from dataclasses import dataclass

from server.core.interfaces.deletable_ad_repository_interface import (
    DeletableAdRepository,
)
from server.core.interfaces.relogio_interface import RelogioInterface


@dataclass(frozen=True)
class DeletedAds:
    deleted: int
    image_keys: list[str]


class DeleteExpiredAds:
    """Permanently delete expired ads past `Ad.RETENTION_AFTER_EXPIRY`."""

    def __init__(
        self,
        repository: DeletableAdRepository,
        relogio: RelogioInterface,
    ) -> None:
        self._repository = repository
        self._relogio = relogio

    def execute(self) -> DeletedAds:
        """Delete old expired ads; return how many and their photo keys."""
        now = self._relogio.agora()
        ids = [
            ad.id
            for ad in self._repository.list_expired_ads()
            if ad.can_be_deleted(now)
        ]
        if not ids:
            return DeletedAds(deleted=0, image_keys=[])
        keys = self._repository.delete_expired(ids)
        return DeletedAds(
            deleted=len(keys),
            image_keys=[key for key in keys if key is not None],
        )
