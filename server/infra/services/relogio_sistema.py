"""System clock in UTC."""

from datetime import UTC, datetime

from server.core.interfaces.relogio_interface import RelogioInterface


class RelogioSistema(RelogioInterface):

    def agora(self) -> datetime:
        return datetime.now(UTC)
