"""Wire the use cases with in-memory doubles."""

from dataclasses import dataclass
from datetime import timedelta

import pytest

from server.core.usecases.autenticar import Autenticar
from server.core.usecases.cadastrar_usuario import CadastrarUsuario
from server.core.usecases.confirmar_email import ConfirmarEmail
from server.core.usecases.emissor_de_confirmacao import EmissorDeConfirmacao
from server.core.usecases.encerrar_sessao import EncerrarSessao
from server.core.usecases.obter_usuario_da_sessao import (
    ObterUsuarioDaSessao,
)
from server.core.usecases.reenviar_confirmacao import ReenviarConfirmacao
from tests.core.usecases.fakes import (
    EnviadorDeEmailFalso,
    GeradorDeTokenFalso,
    HasherDeSenhaFalso,
    RelogioFalso,
    SessaoRepositoryEmMemoria,
    TokenDeConfirmacaoRepositoryEmMemoria,
    UsuarioRepositoryEmMemoria,
)

URL_BASE = "http://front.example/confirmar-email"
DURACAO_SESSAO = timedelta(hours=8)
SENHA = "senha-segura"


@dataclass
class Ambiente:
    usuarios: UsuarioRepositoryEmMemoria
    tokens: TokenDeConfirmacaoRepositoryEmMemoria
    sessoes: SessaoRepositoryEmMemoria
    relogio: RelogioFalso
    enviador: EnviadorDeEmailFalso
    gerador: GeradorDeTokenFalso
    emissor: EmissorDeConfirmacao
    cadastrar: CadastrarUsuario
    confirmar: ConfirmarEmail
    reenviar: ReenviarConfirmacao
    autenticar: Autenticar
    encerrar: EncerrarSessao
    obter_usuario: ObterUsuarioDaSessao

    def cadastrar_ana(self, **overrides):
        dados = {
            "nome": "Ana",
            "email": "ana@aluno.puc-rio.br",
            "nome_usuario": "ana",
            "matricula": "2310001",
            "vinculo": "aluno",
            "senha": SENHA,
        }
        dados.update(overrides)
        return self.cadastrar.executar(**dados)

    def cadastrar_confirmado(self, **overrides):
        self.cadastrar_ana(**overrides)
        return self.confirmar.executar(self.enviador.ultimo.token)


@pytest.fixture
def ambiente() -> Ambiente:
    usuarios = UsuarioRepositoryEmMemoria()
    tokens = TokenDeConfirmacaoRepositoryEmMemoria()
    sessoes = SessaoRepositoryEmMemoria()
    relogio = RelogioFalso()
    enviador = EnviadorDeEmailFalso()
    gerador = GeradorDeTokenFalso()
    hasher = HasherDeSenhaFalso()
    emissor = EmissorDeConfirmacao(
        tokens, gerador, enviador, relogio, URL_BASE
    )
    return Ambiente(
        usuarios=usuarios,
        tokens=tokens,
        sessoes=sessoes,
        relogio=relogio,
        enviador=enviador,
        gerador=gerador,
        emissor=emissor,
        cadastrar=CadastrarUsuario(
            usuarios, tokens, hasher, relogio, emissor
        ),
        confirmar=ConfirmarEmail(usuarios, tokens, relogio),
        reenviar=ReenviarConfirmacao(usuarios, emissor),
        autenticar=Autenticar(
            usuarios, sessoes, hasher, gerador, relogio, DURACAO_SESSAO
        ),
        encerrar=EncerrarSessao(sessoes, relogio),
        obter_usuario=ObterUsuarioDaSessao(sessoes, usuarios, relogio),
    )
