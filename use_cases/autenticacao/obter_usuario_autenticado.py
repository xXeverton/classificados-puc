"""Caso de uso: identificar o usuário dono de um token de sessão."""

from domain.erros import TokenInvalido
from domain.usuario import Usuario
from use_cases.autenticacao.portas import ServicoToken, UsuarioRepository


class ObterUsuarioAutenticado:
    def __init__(
        self, servico_token: ServicoToken, usuarios: UsuarioRepository
    ) -> None:
        self._servico_token = servico_token
        self._usuarios = usuarios

    def executar(self, token: str) -> Usuario:
        usuario_id = self._servico_token.validar(token)
        usuario = self._usuarios.buscar_por_id(usuario_id)
        if usuario is None or not usuario.pode_acessar():
            raise TokenInvalido()
        return usuario
