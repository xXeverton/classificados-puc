"""Mock temporário do perfil de anunciante até a implementação da US02."""

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class PerfilAnuncianteMock:
    """Dados em memória usados somente para simular a completude do perfil."""

    nome_exibicao: str | None
    foto: str | None
    whatsapp: str | None
    email: str | None

    def esta_completo(self) -> bool:
        return all(
            isinstance(valor, str) and bool(valor.strip())
            for valor in (
                self.nome_exibicao,
                self.foto,
                self.whatsapp,
                self.email,
            )
        )


class VerificadorPerfilCompletoMock:
    """MOCK TEMPORÁRIO: trocar pela consulta ao perfil persistido da US02."""

    def __init__(
        self,
        perfis: Mapping[int, PerfilAnuncianteMock] | None = None,
    ) -> None:
        self._perfis = dict(perfis or {})

    def esta_completo(self, id_usuario: int) -> bool:
        perfil = self._perfis.get(id_usuario)
        return perfil is not None and perfil.esta_completo()

    def definir_perfil(
        self, id_usuario: int, perfil: PerfilAnuncianteMock
    ) -> None:
        """Define dados de perfil simulados para testes e desenvolvimento."""
        self._perfis[id_usuario] = perfil
