"""Password hashing contract."""

from abc import ABC, abstractmethod


class HasherDeSenhaInterface(ABC):

    @abstractmethod
    def gerar_hash(self, senha: str) -> str:
        """Return a salted, one-way hash of the password."""

    @abstractmethod
    def verificar(self, senha: str, senha_hash: str) -> bool:
        """Tell whether the password matches the stored hash."""
