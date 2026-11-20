"""Log in with e-mail, username, or registration number plus password."""

from dataclasses import dataclass
from datetime import datetime, timedelta

from server.core.entities.politicas_autenticacao import hash_de_token
from server.core.entities.sessao import Sessao
from server.core.entities.usuario import Usuario, normalizar_identificador
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
from server.core.interfaces.usuario_repository_interface import (
    UsuarioRepositoryInterface,
)
from server.core.usecases.erros import (
    ContaBloqueada,
    CredenciaisInvalidas,
    EmailNaoConfirmado,
)


@dataclass(frozen=True)
class ResultadoAutenticacao:
    token: str
    expira_em: datetime


class Autenticar:

    def __init__(
        self,
        usuarios: UsuarioRepositoryInterface,
        sessoes: SessaoRepositoryInterface,
        hasher_senha: HasherDeSenhaInterface,
        gerador_token: GeradorDeTokenInterface,
        relogio: RelogioInterface,
        duracao_sessao: timedelta,
    ) -> None:
        self._usuarios = usuarios
        self._sessoes = sessoes
        self._hasher_senha = hasher_senha
        self._gerador_token = gerador_token
        self._relogio = relogio
        self._duracao_sessao = duracao_sessao

    def executar(
        self, identificador: str, senha: str
    ) -> ResultadoAutenticacao:
        agora = self._relogio.agora()
        usuario = self._buscar(identificador)
        if usuario is None:
            raise CredenciaisInvalidas()
        if usuario.esta_bloqueado(agora):
            raise ContaBloqueada()
        if not self._hasher_senha.verificar(senha, usuario.senha_hash):
            self._usuarios.salvar(usuario.registrar_falha_de_login(agora))
            raise CredenciaisInvalidas()
        # Checked after the password so the account state is not revealed
        # to someone who does not know it.
        if not usuario.esta_confirmado():
            raise EmailNaoConfirmado()

        self._usuarios.salvar(usuario.registrar_login_bem_sucedido())
        return self._abrir_sessao(usuario, agora)

    def _buscar(self, identificador: str) -> Usuario | None:
        valor = normalizar_identificador(identificador)
        if not valor:
            return None
        if "@" in valor:
            return self._usuarios.buscar_por_email(valor)
        return self._usuarios.buscar_por_identificador_alternativo(valor)

    def _abrir_sessao(
        self, usuario: Usuario, agora: datetime
    ) -> ResultadoAutenticacao:
        token = self._gerador_token.gerar()
        sessao = self._sessoes.salvar(
            Sessao(
                usuario_id=usuario.id,
                token_hash=hash_de_token(token),
                criada_em=agora,
                expira_em=agora + self._duracao_sessao,
            )
        )
        return ResultadoAutenticacao(token=token, expira_em=sessao.expira_em)
