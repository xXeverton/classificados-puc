"""Implementações falsas das portas, para testes sem efeitos externos."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from domain.erros import TokenInvalido
from domain.usuario import Usuario, Vinculo
from use_cases.autenticacao.portas import SessaoAutenticada

INSTANTE_INICIAL = datetime(2026, 11, 12, 12, 0, tzinfo=timezone.utc)


class RelogioControlado:
    def __init__(self, inicio: datetime = INSTANTE_INICIAL) -> None:
        self._agora = inicio

    def agora(self) -> datetime:
        return self._agora

    def avancar(self, intervalo: timedelta) -> None:
        self._agora += intervalo


@dataclass(frozen=True)
class EmailEnviado:
    destinatario: str
    assunto: str
    corpo: str


class EnviadorEmailFalso:
    def __init__(self) -> None:
        self.enviados: list[EmailEnviado] = []

    def enviar(self, destinatario: str, assunto: str, corpo: str) -> None:
        self.enviados.append(EmailEnviado(destinatario, assunto, corpo))


class VerificadorSenhaFalso:
    """Considera `hash:<senha>` o hash de `<senha>`."""

    @staticmethod
    def gerar_hash(senha: str) -> str:
        return f"hash:{senha}"

    def verificar(self, senha: str, senha_hash: str) -> bool:
        return senha_hash == self.gerar_hash(senha)


class ServicoTokenFalso:
    _PREFIXO = "token-"

    def emitir(self, usuario_id: int) -> SessaoAutenticada:
        return SessaoAutenticada(f"{self._PREFIXO}{usuario_id}", 3600)

    def validar(self, token: str) -> int:
        if not token.startswith(self._PREFIXO):
            raise TokenInvalido()
        return int(token[len(self._PREFIXO):])


def criar_usuario(**sobrescritas) -> Usuario:
    dados = {
        "id": 1,
        "nome": "Ana",
        "email": "ana@aluno.puc-rio.br",
        "matricula": "2310001",
        "vinculo": Vinculo.ALUNO,
        "senha_hash": VerificadorSenhaFalso.gerar_hash("senha-correta"),
    }
    dados.update(sobrescritas)
    return Usuario(**dados)
