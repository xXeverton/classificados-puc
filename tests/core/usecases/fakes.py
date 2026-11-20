"""In-memory test doubles for the core interfaces."""

import re
from dataclasses import dataclass, replace
from datetime import UTC, datetime, timedelta

from server.core.entities.sessao import Sessao
from server.core.entities.token_de_confirmacao import TokenDeConfirmacao
from server.core.entities.usuario import Usuario
from server.core.interfaces.enviador_de_email_interface import (
    EnviadorDeEmailInterface,
)
from server.core.interfaces.gerador_de_token_interface import (
    GeradorDeTokenInterface,
)
from server.core.interfaces.hasher_de_senha_interface import (
    HasherDeSenhaInterface,
)
from server.core.interfaces.relogio_interface import RelogioInterface
from server.core.interfaces.sessao_repository_interface import (
    SessaoRepositoryInterface,
)
from server.core.interfaces.token_de_confirmacao_repository_interface import (
    TokenDeConfirmacaoRepositoryInterface,
)
from server.core.interfaces.usuario_repository_interface import (
    UsuarioRepositoryInterface,
)

INICIO = datetime(2026, 11, 20, 12, 0, tzinfo=UTC)


class UsuarioRepositoryEmMemoria(UsuarioRepositoryInterface):

    def __init__(self) -> None:
        self.usuarios: dict[int, Usuario] = {}
        self._proximo_id = 1

    def buscar_por_id(self, usuario_id: int) -> Usuario | None:
        return self.usuarios.get(usuario_id)

    def buscar_por_email(self, email: str) -> Usuario | None:
        return next(
            (u for u in self.usuarios.values() if u.email == email), None
        )

    def buscar_por_identificador_alternativo(
        self, valor: str
    ) -> Usuario | None:
        return next(
            (
                u
                for u in self.usuarios.values()
                if valor in (u.nome_usuario, u.matricula)
            ),
            None,
        )

    def salvar(self, usuario: Usuario) -> Usuario:
        if usuario.id is None:
            usuario = replace(usuario, id=self._proximo_id)
            self._proximo_id += 1
        self.usuarios[usuario.id] = usuario
        return usuario

    def remover(self, usuario_id: int) -> None:
        self.usuarios.pop(usuario_id, None)


class TokenDeConfirmacaoRepositoryEmMemoria(
    TokenDeConfirmacaoRepositoryInterface
):

    def __init__(self) -> None:
        self.tokens: dict[int, TokenDeConfirmacao] = {}
        self._proximo_id = 1

    def salvar(self, token: TokenDeConfirmacao) -> TokenDeConfirmacao:
        if token.id is None:
            token = replace(token, id=self._proximo_id)
            self._proximo_id += 1
        self.tokens[token.id] = token
        return token

    def buscar_por_hash(self, token_hash: str) -> TokenDeConfirmacao | None:
        return next(
            (t for t in self.tokens.values() if t.token_hash == token_hash),
            None,
        )

    def invalidar_do_usuario(self, usuario_id: int, agora: datetime) -> None:
        for token in list(self.tokens.values()):
            if token.usuario_id == usuario_id and not token.foi_usado():
                self.tokens[token.id] = replace(token, usado_em=agora)

    def existe_valido_do_usuario(
        self, usuario_id: int, agora: datetime
    ) -> bool:
        return any(
            t.usuario_id == usuario_id and t.esta_valido(agora)
            for t in self.tokens.values()
        )


class SessaoRepositoryEmMemoria(SessaoRepositoryInterface):

    def __init__(self) -> None:
        self.sessoes: dict[int, Sessao] = {}
        self._proximo_id = 1

    def salvar(self, sessao: Sessao) -> Sessao:
        if sessao.id is None:
            sessao = replace(sessao, id=self._proximo_id)
            self._proximo_id += 1
        self.sessoes[sessao.id] = sessao
        return sessao

    def buscar_por_hash(self, token_hash: str) -> Sessao | None:
        return next(
            (s for s in self.sessoes.values() if s.token_hash == token_hash),
            None,
        )


class RelogioFalso(RelogioInterface):

    def __init__(self, inicio: datetime = INICIO) -> None:
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

    @property
    def token(self) -> str:
        encontrado = re.search(r"[?&]token=([^\s&]+)", self.corpo)
        if encontrado is None:
            raise AssertionError("E-mail sem link de confirmação.")
        return encontrado.group(1)


class EnviadorDeEmailFalso(EnviadorDeEmailInterface):

    def __init__(self) -> None:
        self.enviados: list[EmailEnviado] = []

    def enviar(self, destinatario: str, assunto: str, corpo: str) -> None:
        self.enviados.append(EmailEnviado(destinatario, assunto, corpo))

    @property
    def ultimo(self) -> EmailEnviado:
        return self.enviados[-1]


class GeradorDeTokenFalso(GeradorDeTokenInterface):

    def __init__(self) -> None:
        self._contador = 0

    def gerar(self) -> str:
        self._contador += 1
        return f"token-{self._contador}"


class HasherDeSenhaFalso(HasherDeSenhaInterface):

    def gerar_hash(self, senha: str) -> str:
        return f"hash:{senha}"

    def verificar(self, senha: str, senha_hash: str) -> bool:
        return senha_hash == self.gerar_hash(senha)
