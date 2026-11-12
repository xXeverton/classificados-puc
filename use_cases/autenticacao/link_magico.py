"""Casos de uso do link mágico enviado por e-mail (plano B do EN01)."""

import hashlib
import secrets
from datetime import timedelta
from urllib.parse import urlencode

from domain.autenticacao import VALIDADE_LINK_MAGICO, LinkMagico
from domain.email_institucional import validar_email_institucional
from domain.erros import TokenInvalido
from use_cases.autenticacao.portas import (
    EnviadorEmail,
    LinkMagicoRepository,
    Relogio,
    ServicoToken,
    SessaoAutenticada,
    UsuarioRepository,
)

ASSUNTO_LINK_MAGICO = "Seu link de acesso"
_BYTES_TOKEN = 32


def calcular_hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class SolicitarLinkMagico:
    def __init__(
        self,
        usuarios: UsuarioRepository,
        links: LinkMagicoRepository,
        enviador_email: EnviadorEmail,
        relogio: Relogio,
        url_base: str,
        validade: timedelta = VALIDADE_LINK_MAGICO,
    ) -> None:
        self._usuarios = usuarios
        self._links = links
        self._enviador_email = enviador_email
        self._relogio = relogio
        self._url_base = url_base
        self._validade = validade

    def executar(self, email: str) -> None:
        """Para e-mails institucionais, não informa se estão cadastrados:
        o retorno é sempre o mesmo (RN6). Outros domínios são recusados.
        """
        email = validar_email_institucional(email)
        usuario = self._usuarios.buscar_por_email(email)
        if usuario is None or not usuario.pode_acessar():
            return

        token = secrets.token_urlsafe(_BYTES_TOKEN)
        self._links.salvar(
            LinkMagico(
                token_hash=calcular_hash_token(token),
                usuario_id=usuario.id,
                expira_em=self._relogio.agora() + self._validade,
            )
        )
        self._enviador_email.enviar(
            destinatario=usuario.email,
            assunto=ASSUNTO_LINK_MAGICO,
            corpo=self._montar_corpo(usuario.nome, token),
        )

    def _montar_corpo(self, nome: str, token: str) -> str:
        link = f"{self._url_base}?{urlencode({'token': token})}"
        minutos = int(self._validade.total_seconds() // 60)
        return (
            f"Olá, {nome}!\n\n"
            f"Use o link abaixo para entrar na plataforma:\n{link}\n\n"
            f"Ele vale por {minutos} minutos e só pode ser usado uma vez. "
            "Se você não pediu este acesso, ignore este e-mail."
        )


class EntrarComLinkMagico:
    def __init__(
        self,
        links: LinkMagicoRepository,
        usuarios: UsuarioRepository,
        servico_token: ServicoToken,
        relogio: Relogio,
    ) -> None:
        self._links = links
        self._usuarios = usuarios
        self._servico_token = servico_token
        self._relogio = relogio

    def executar(self, token: str) -> SessaoAutenticada:
        token_hash = calcular_hash_token(token)
        link = self._links.buscar_por_token_hash(token_hash)
        if link is None or not link.pode_ser_usado(self._relogio.agora()):
            raise TokenInvalido()

        self._links.marcar_como_usado(token_hash)

        usuario = self._usuarios.buscar_por_id(link.usuario_id)
        if usuario is None or not usuario.pode_acessar():
            raise TokenInvalido()
        return self._servico_token.emitir(usuario.id)
