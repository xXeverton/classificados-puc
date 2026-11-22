"""Use case that expires published advertisements past their period."""

from server.core.interfaces.expirable_ad_repository_interface import (
    ExpirableAdRepository,
)
from server.core.interfaces.relogio_interface import RelogioInterface


class ExpireAds:
    """Mark overdue published advertisements as expired."""

    def __init__(
        self,
        repository: ExpirableAdRepository,
        relogio: RelogioInterface,
    ) -> None:
        self._repository = repository
        self._relogio = relogio

    def execute(self) -> int:
        """Expire overdue ads and return how many were expired."""
        now = self._relogio.agora()
        overdue_ids = [
            ad.id
            for ad in self._repository.list_published_ads()
            if ad.is_overdue(now)
        ]
        if not overdue_ids:
            return 0
        return self._repository.mark_as_expired(overdue_ids)
