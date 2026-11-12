"""Caso de uso: entrar com e-mail institucional e senha."""

import math

from domain.autenticacao import PoliticaBloqueio
from domain.email_institucional import validar_email_institucional
from domain.erros import CredenciaisInvalidas, LoginBloqueado
from use_cases.autenticacao.portas import (
    Relogio,
    ServicoToken,
    SessaoAutenticada,
    TentativasLoginRepository,
    UsuarioRepository,
    VerificadorSenha,
)


class EntrarComEmail:
    def __init__(
        self,
        usuarios: UsuarioRepository,
        tentativas: TentativasLoginRepository,
        verificador_senha: VerificadorSenha,
        servico_token: ServicoToken,
        relogio: Relogio,
        politica: PoliticaBloqueio = PoliticaBloqueio(),
    ) -> None:
        self._usuarios = usuarios
        self._tentativas = tentativas
        self._verificador_senha = verificador_senha
        self._servico_token = servico_token
        self._relogio = relogio
        self._politica = politica

    def executar(self, email: str, senha: str) -> SessaoAutenticada:
        # E-mail fora dos domínios aceitos é recusado antes de contar
        # tentativa (CA5).
        email = validar_email_institucional(email)
        agora = self._relogio.agora()
        tentativas = self._tentativas.obter(email)

        if tentativas.esta_bloqueado(agora):
            restante = (tentativas.bloqueado_ate - agora).total_seconds()
            raise LoginBloqueado(math.ceil(restante))

        usuario = self._usuarios.buscar_por_email(email)
        senha_confere = (
            usuario is not None
            and usuario.senha_hash is not None
            and self._verificador_senha.verificar(senha, usuario.senha_hash)
        )
        if not senha_confere:
            # Conta por e-mail, cadastrado ou não, para não revelar quem
            # está cadastrado (RN5).
            self._tentativas.salvar(
                email, tentativas.registrar_falha(agora, self._politica)
            )
            raise CredenciaisInvalidas()

        if not usuario.pode_acessar():
            raise CredenciaisInvalidas()

        self._tentativas.limpar(email)
        return self._servico_token.emitir(usuario.id)
