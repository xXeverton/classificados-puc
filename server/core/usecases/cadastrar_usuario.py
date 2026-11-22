"""Register a pending account and send its confirmation link."""

from dataclasses import replace

from server.core.entities.senha import validar_senha
from server.core.entities.usuario import Usuario
from server.core.interfaces.hasher_de_senha_interface import (
    HasherDeSenhaInterface,
)
from server.core.interfaces.relogio_interface import RelogioInterface
from server.core.interfaces.token_de_confirmacao_repository_interface import (
    TokenDeConfirmacaoRepositoryInterface,
)
from server.core.interfaces.usuario_repository_interface import (
    UsuarioRepositoryInterface,
)
from server.core.usecases.emissor_de_confirmacao import EmissorDeConfirmacao
from server.core.usecases.erros import (
    DadosInvalidos,
    EmailEmUso,
    IdentificadorEmUso,
)

_MENSAGEM_EM_USO = {
    "nome_usuario": "Nome de usuário já está em uso.",
    "matricula": "Matrícula já está em uso.",
}


class CadastrarUsuario:

    def __init__(
        self,
        usuarios: UsuarioRepositoryInterface,
        tokens: TokenDeConfirmacaoRepositoryInterface,
        hasher_senha: HasherDeSenhaInterface,
        relogio: RelogioInterface,
        emissor: EmissorDeConfirmacao,
    ) -> None:
        self._usuarios = usuarios
        self._tokens = tokens
        self._hasher_senha = hasher_senha
        self._relogio = relogio
        self._emissor = emissor

    def executar(
        self,
        *,
        nome: str,
        email: str,
        nome_usuario: str,
        vinculo: str,
        senha: str,
        matricula: str | None = None,
    ) -> Usuario:
        try:
            validar_senha(senha)
            usuario = Usuario(
                nome=nome,
                email=email,
                nome_usuario=nome_usuario,
                matricula=matricula,
                vinculo=vinculo,
                senha_hash=self._hasher_senha.gerar_hash(senha),
            )
        except ValueError as erro:
            raise DadosInvalidos(str(erro)) from erro

        usuario = self._substituir_pendente_com_mesmo_email(usuario)
        self._garantir_identificador_livre(usuario, "nome_usuario")
        if usuario.matricula is not None:
            self._garantir_identificador_livre(usuario, "matricula")

        salvo = self._usuarios.salvar(usuario)
        self._emissor.emitir(salvo)
        return salvo

    def _substituir_pendente_com_mesmo_email(
        self, usuario: Usuario
    ) -> Usuario:
        """RN9: a pending account with this e-mail is overwritten."""
        existente = self._usuarios.buscar_por_email(usuario.email)
        if existente is None:
            return usuario
        if existente.esta_confirmado():
            raise EmailEmUso()
        return replace(usuario, id=existente.id)

    def _garantir_identificador_livre(
        self, usuario: Usuario, campo: str
    ) -> None:
        """RN12/RN13: username and registration are unique among both."""
        valor = getattr(usuario, campo)
        dono = self._usuarios.buscar_por_identificador_alternativo(valor)
        if dono is None or (usuario.id is not None and dono.id == usuario.id):
            return
        if self._reserva_expirou(dono):
            self._usuarios.remover(dono.id)
            return
        if getattr(dono, campo) == valor:
            raise IdentificadorEmUso(_MENSAGEM_EM_USO[campo])
        raise IdentificadorEmUso()

    def _reserva_expirou(self, dono: Usuario) -> bool:
        return not dono.esta_confirmado() and not (
            self._tokens.existe_valido_do_usuario(
                dono.id, self._relogio.agora()
            )
        )
