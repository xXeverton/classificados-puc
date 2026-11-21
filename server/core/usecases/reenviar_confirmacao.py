"""Send a new confirmation link to a pending account."""

from server.core.entities.usuario import normalizar_identificador
from server.core.interfaces.usuario_repository_interface import (
    UsuarioRepositoryInterface,
)
from server.core.usecases.emissor_de_confirmacao import EmissorDeConfirmacao


class ReenviarConfirmacao:
    """Behaves the same whether or not the e-mail has an account."""

    def __init__(
        self,
        usuarios: UsuarioRepositoryInterface,
        emissor: EmissorDeConfirmacao,
    ) -> None:
        self._usuarios = usuarios
        self._emissor = emissor

    def executar(self, email: str) -> None:
        usuario = self._usuarios.buscar_por_email(
            normalizar_identificador(email)
        )
        if usuario is None or usuario.esta_confirmado():
            return
        self._emissor.emitir(usuario)
