from datetime import timedelta

import pytest

from domain.erros import (
    MENSAGEM_CREDENCIAIS_INVALIDAS,
    CredenciaisInvalidas,
    EmailNaoInstitucional,
    LoginBloqueado,
)
from domain.usuario import Vinculo
from infra.repositories.memoria import (
    TentativasLoginRepositoryMemoria,
    UsuarioRepositoryMemoria,
)
from tests.fakes import (
    RelogioControlado,
    ServicoTokenFalso,
    VerificadorSenhaFalso,
    criar_usuario,
)
from use_cases.autenticacao import EntrarComEmail

EMAIL = "ana@aluno.puc-rio.br"
EMAIL_INEXISTENTE = "ninguem@puc-rio.br"
SENHA_CORRETA = "senha-correta"


@pytest.fixture
def relogio():
    return RelogioControlado()


@pytest.fixture
def usuarios():
    return UsuarioRepositoryMemoria([criar_usuario()])


@pytest.fixture
def tentativas():
    return TentativasLoginRepositoryMemoria()


@pytest.fixture
def entrar(usuarios, tentativas, relogio):
    return EntrarComEmail(
        usuarios=usuarios,
        tentativas=tentativas,
        verificador_senha=VerificadorSenhaFalso(),
        servico_token=ServicoTokenFalso(),
        relogio=relogio,
    )


def errar_senha(entrar, vezes, email=EMAIL):
    for _ in range(vezes):
        with pytest.raises(CredenciaisInvalidas):
            entrar.executar(email, "senha-errada")


def test_ca1_credenciais_validas_emitem_sessao(entrar):
    sessao = entrar.executar(EMAIL, SENHA_CORRETA)

    assert sessao.token == "token-1"


def test_email_com_maiusculas_e_espacos_e_aceito(entrar):
    assert entrar.executar("  Ana@ALUNO.puc-rio.br ", SENHA_CORRETA).token


def test_funcionario_com_email_puc_rio_entra(usuarios, entrar):
    usuarios.adicionar(
        criar_usuario(
            id=2, email="joao@puc-rio.br", vinculo=Vinculo.FUNCIONARIO
        )
    )

    assert entrar.executar("joao@puc-rio.br", SENHA_CORRETA).token == "token-2"


def test_ca2_senha_errada_e_recusada_com_mensagem_padrao(entrar):
    with pytest.raises(CredenciaisInvalidas) as erro:
        entrar.executar(EMAIL, "senha-errada")

    assert str(erro.value) == MENSAGEM_CREDENCIAIS_INVALIDAS


def test_ca2_email_nao_cadastrado_tem_a_mesma_mensagem(entrar):
    with pytest.raises(CredenciaisInvalidas) as erro:
        entrar.executar(EMAIL_INEXISTENTE, SENHA_CORRETA)

    assert str(erro.value) == MENSAGEM_CREDENCIAIS_INVALIDAS


@pytest.mark.parametrize(
    "email", ["ana@gmail.com", "ana@ccc.puc-rio.br", "ana"]
)
def test_ca5_email_fora_dos_dominios_e_recusado(entrar, email):
    with pytest.raises(EmailNaoInstitucional):
        entrar.executar(email, SENHA_CORRETA)


def test_ca5_email_fora_dos_dominios_nao_conta_tentativa(
    entrar, tentativas
):
    for _ in range(5):
        with pytest.raises(EmailNaoInstitucional):
            entrar.executar("ana@gmail.com", "x")

    assert tentativas.obter("ana@gmail.com").falhas_consecutivas == 0


def test_usuario_sem_senha_cadastrada_nao_entra(usuarios, entrar):
    usuarios.adicionar(criar_usuario(senha_hash=None))

    with pytest.raises(CredenciaisInvalidas):
        entrar.executar(EMAIL, SENHA_CORRETA)


def test_terceirizado_nao_entra_mesmo_com_senha_correta(usuarios, entrar):
    usuarios.adicionar(criar_usuario(vinculo=Vinculo.TERCEIRIZADO))

    with pytest.raises(CredenciaisInvalidas):
        entrar.executar(EMAIL, SENHA_CORRETA)


def test_ca3_cinco_erros_bloqueiam_mesmo_com_senha_correta(entrar):
    errar_senha(entrar, 5)

    with pytest.raises(LoginBloqueado) as erro:
        entrar.executar(EMAIL, SENHA_CORRETA)

    assert erro.value.segundos_restantes == 600


def test_ca3_erros_com_variacao_de_maiusculas_contam_juntos(entrar):
    errar_senha(entrar, 4)
    errar_senha(entrar, 1, email="ANA@aluno.puc-rio.br")

    with pytest.raises(LoginBloqueado):
        entrar.executar(EMAIL, SENHA_CORRETA)


def test_ca3_quatro_erros_ainda_permitem_entrar(entrar):
    errar_senha(entrar, 4)

    assert entrar.executar(EMAIL, SENHA_CORRETA).token


def test_ca3_acerto_zera_a_contagem_de_erros(entrar):
    errar_senha(entrar, 4)
    entrar.executar(EMAIL, SENHA_CORRETA)
    errar_senha(entrar, 4)

    assert entrar.executar(EMAIL, SENHA_CORRETA).token


def test_ca3_bloqueio_informa_o_tempo_restante(entrar, relogio):
    errar_senha(entrar, 5)
    relogio.avancar(timedelta(minutes=7, seconds=30))

    with pytest.raises(LoginBloqueado) as erro:
        entrar.executar(EMAIL, SENHA_CORRETA)

    assert erro.value.segundos_restantes == 150


def test_ca4_apos_10_minutos_o_login_volta_a_funcionar(entrar, relogio):
    errar_senha(entrar, 5)
    relogio.avancar(timedelta(minutes=10))

    assert entrar.executar(EMAIL, SENHA_CORRETA).token


def test_bloqueio_e_por_email(usuarios, entrar):
    usuarios.adicionar(criar_usuario(id=2, email="bia@aluno.puc-rio.br"))
    errar_senha(entrar, 5)

    assert entrar.executar("bia@aluno.puc-rio.br", SENHA_CORRETA).token


def test_email_nao_cadastrado_tambem_e_bloqueado(entrar):
    errar_senha(entrar, 5, email=EMAIL_INEXISTENTE)

    with pytest.raises(LoginBloqueado):
        entrar.executar(EMAIL_INEXISTENTE, "qualquer")
