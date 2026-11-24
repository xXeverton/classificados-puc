"""Public domain representation of advertisement details."""

from dataclasses import dataclass

from server.core.entities.ad import Ad
from server.core.entities.contato import Contato


@dataclass(frozen=True)
class AdvertiserSummary:
    """Public information about the advertiser of an advertisement."""

    nome_exibicao: str
    vinculo: str
    foto_url: str | None
    contatos: tuple[Contato, ...]

    def __post_init__(self) -> None:
        nome = self.nome_exibicao.strip()
        if not nome:
            raise ValueError("Nome de exibição é obrigatório.")
        if self.vinculo not in {"aluno", "funcionario"}:
            raise ValueError("Vínculo público inválido.")

        object.__setattr__(self, "nome_exibicao", nome)
        object.__setattr__(self, "contatos", tuple(self.contatos))


@dataclass(frozen=True)
class AdDetails:
    """Advertisement, its public advertiser summary and viewer ownership."""

    ad: Ad
    advertiser: AdvertiserSummary
    is_owner: bool = False
