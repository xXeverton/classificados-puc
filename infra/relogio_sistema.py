"""Relógio real em UTC."""

from datetime import datetime, timezone


class RelogioSistema:
    def agora(self) -> datetime:
        return datetime.now(timezone.utc)
