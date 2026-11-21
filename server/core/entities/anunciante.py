"""Advertiser profile: the optional extension of a member's profile."""

from dataclasses import dataclass, replace

from server.core.entities.contato import Contato
from server.core.entities.politicas_perfil import MAXIMO_CONTATOS


def _texto_ou_none(valor: str | None) -> str | None:
    if valor is None:
        return None
    return valor.strip() or None


@dataclass(frozen=True)
class Anunciante:
    """A saved advertiser profile is always complete: name and a contact."""

    usuario_id: int
    nome_exibicao: str
    contatos: tuple[Contato, ...]
    foto_url: str | None = None
    id: int | None = None

    def __post_init__(self) -> None:
        self._definir("nome_exibicao", self.nome_exibicao.strip())
        self._definir("contatos", tuple(self.contatos))
        self._definir("foto_url", _texto_ou_none(self.foto_url))

        if not self.nome_exibicao:
            raise ValueError("Nome de exibição é obrigatório.")
        if not self.contatos:
            raise ValueError("Informe ao menos um contato.")
        if len(self.contatos) > MAXIMO_CONTATOS:
            raise ValueError(
                f"Um perfil pode ter no máximo {MAXIMO_CONTATOS} contatos."
            )
        if len({self._chave(c) for c in self.contatos}) != len(self.contatos):
            raise ValueError("Há contatos repetidos.")

    def com_foto(self, foto_url: str) -> "Anunciante":
        return replace(self, foto_url=foto_url)

    def sem_foto(self) -> "Anunciante":
        return replace(self, foto_url=None)

    @staticmethod
    def _chave(contato: Contato) -> tuple[object, str | None, str]:
        """Identity of a contact, ignoring the label."""
        return (contato.tipo, contato.codigo_pais, contato.valor)

    def _definir(self, campo: str, valor: object) -> None:
        object.__setattr__(self, campo, valor)
