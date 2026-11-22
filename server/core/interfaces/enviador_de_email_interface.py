"""Outbound e-mail contract."""

from abc import ABC, abstractmethod


class EnviadorDeEmailInterface(ABC):

    @abstractmethod
    def enviar(self, destinatario: str, assunto: str, corpo: str) -> None:
        """Send a plain-text e-mail or raise on failure."""
