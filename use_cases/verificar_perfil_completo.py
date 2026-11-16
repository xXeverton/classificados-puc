"""Porta para consultar a completude do perfil do anunciante."""

from typing import Protocol

CHAVE_EXTENSAO_PERFIL_COMPLETO = "verificador_perfil_completo"


class VerificadorPerfilCompleto(Protocol):
    def esta_completo(self, id_usuario: int) -> bool:
        """Informa se os dados de perfil necessários estão preenchidos."""
