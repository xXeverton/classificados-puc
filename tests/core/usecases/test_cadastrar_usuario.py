from datetime import timedelta

import pytest

from server.core.entities.vinculo import Vinculo
from server.core.usecases.erros import (
    DadosInvalidos,
    EmailEmUso,
    IdentificadorEmUso,
    TokenInvalido,
)

QUINZE_MINUTOS_E_UM_SEGUNDO = timedelta(minutes=15, seconds=1)


def test_cadastro_creates_pending_account_and_sends_link(ambiente):
    usuario = ambiente.cadastrar_ana()

    assert usuario.id is not None
    assert not usuario.esta_confirmado()
    assert usuario.vinculo is Vinculo.ALUNO
    assert usuario.senha_hash != "senha-segura"
    assert ambiente.usuarios.buscar_por_id(usuario.id) == usuario
    assert ambiente.enviador.ultimo.destinatario == usuario.email


@pytest.mark.parametrize("email", ["ana@gmail.com", "ana@puc.br"])
def test_cadastro_rejects_non_institutional_email(ambiente, email):
    with pytest.raises(DadosInvalidos, match="institucionais"):
        ambiente.cadastrar_ana(email=email)

    assert ambiente.usuarios.usuarios == {}
    assert ambiente.enviador.enviados == []


def test_cadastro_rejects_email_of_confirmed_account(ambiente):
    ambiente.cadastrar_confirmado()

    with pytest.raises(EmailEmUso):
        ambiente.cadastrar_ana(
            email="ANA@aluno.puc-rio.br", nome_usuario="outra",
            matricula=None,
        )


def test_cadastro_rejects_short_password(ambiente):
    with pytest.raises(DadosInvalidos, match="8 caracteres"):
        ambiente.cadastrar_ana(senha="1234567")

    assert ambiente.usuarios.usuarios == {}


@pytest.mark.parametrize(
    ("campo", "valor"),
    [("nome", ""), ("vinculo", ""), ("vinculo", "terceirizado")],
)
def test_cadastro_rejects_missing_name_or_invalid_vinculo(
    ambiente, campo, valor
):
    with pytest.raises(DadosInvalidos):
        ambiente.cadastrar_ana(**{campo: valor})

    assert ambiente.usuarios.usuarios == {}


def test_cadastro_rejects_username_with_at_sign(ambiente):
    with pytest.raises(DadosInvalidos, match="@"):
        ambiente.cadastrar_ana(nome_usuario="ana@puc")


def test_cadastro_rejects_username_in_use(ambiente):
    ambiente.cadastrar_confirmado()

    with pytest.raises(IdentificadorEmUso, match="Nome de usuário"):
        ambiente.cadastrar_ana(
            email="bia@aluno.puc-rio.br", nome_usuario="ANA",
            matricula=None,
        )


def test_cadastro_without_matricula_creates_account(ambiente):
    usuario = ambiente.cadastrar_ana(matricula=None)

    assert usuario.matricula is None
    assert ambiente.usuarios.buscar_por_id(usuario.id) is not None


def test_two_accounts_without_matricula_can_coexist(ambiente):
    ambiente.cadastrar_ana(matricula="")

    outra = ambiente.cadastrar_ana(
        email="bia@aluno.puc-rio.br", nome_usuario="bia", matricula=""
    )

    assert outra.matricula is None


def test_cadastro_rejects_matricula_in_use(ambiente):
    ambiente.cadastrar_confirmado()

    with pytest.raises(IdentificadorEmUso, match="Matrícula"):
        ambiente.cadastrar_ana(
            email="bia@aluno.puc-rio.br", nome_usuario="bia",
        )


def test_cadastro_rejects_username_equal_to_other_accounts_matricula(
    ambiente,
):
    ambiente.cadastrar_confirmado()

    with pytest.raises(IdentificadorEmUso, match="Identificador"):
        ambiente.cadastrar_ana(
            email="bia@aluno.puc-rio.br", nome_usuario="2310001",
            matricula=None,
        )


def test_cadastro_rejects_matricula_equal_to_other_accounts_username(
    ambiente,
):
    ambiente.cadastrar_confirmado()

    with pytest.raises(IdentificadorEmUso, match="Identificador"):
        ambiente.cadastrar_ana(
            email="bia@aluno.puc-rio.br", nome_usuario="bia",
            matricula="ana",
        )


def test_username_may_equal_own_matricula(ambiente):
    usuario = ambiente.cadastrar_ana(nome_usuario="2310001")

    assert usuario.nome_usuario == usuario.matricula


def test_cadastro_replaces_pending_account_and_invalidates_old_links(
    ambiente,
):
    primeiro = ambiente.cadastrar_ana()
    link_antigo = ambiente.enviador.ultimo.token

    segundo = ambiente.cadastrar_ana(
        nome="Ana Maria", nome_usuario="anamaria", matricula=None,
        vinculo="funcionario", senha="outra-senha",
    )

    assert segundo.id == primeiro.id
    assert list(ambiente.usuarios.usuarios.values()) == [segundo]
    assert segundo.nome == "Ana Maria"
    assert segundo.senha_hash == "hash:outra-senha"
    assert len(ambiente.enviador.enviados) == 2
    with pytest.raises(TokenInvalido):
        ambiente.confirmar.executar(link_antigo)
    assert ambiente.confirmar.executar(
        ambiente.enviador.ultimo.token
    ).esta_confirmado()


def test_pending_account_keeps_identifiers_while_link_is_valid(ambiente):
    ambiente.cadastrar_ana()
    ambiente.relogio.avancar(timedelta(minutes=15))

    with pytest.raises(IdentificadorEmUso):
        ambiente.cadastrar_ana(email="bia@aluno.puc-rio.br")


def test_pending_account_releases_identifiers_after_link_expires(ambiente):
    pendente = ambiente.cadastrar_ana()
    ambiente.relogio.avancar(QUINZE_MINUTOS_E_UM_SEGUNDO)

    nova = ambiente.cadastrar_ana(email="bia@aluno.puc-rio.br")

    assert nova.nome_usuario == "ana"
    assert nova.matricula == "2310001"
    assert ambiente.usuarios.buscar_por_id(pendente.id) is None


def test_expired_pending_account_releases_matricula_used_as_username(
    ambiente,
):
    ambiente.cadastrar_ana()
    ambiente.relogio.avancar(QUINZE_MINUTOS_E_UM_SEGUNDO)

    nova = ambiente.cadastrar_ana(
        email="bia@aluno.puc-rio.br", nome_usuario="2310001",
        matricula=None,
    )

    assert nova.nome_usuario == "2310001"


def test_confirmed_account_keeps_identifiers_forever(ambiente):
    ambiente.cadastrar_confirmado()
    ambiente.relogio.avancar(timedelta(days=30))

    with pytest.raises(IdentificadorEmUso):
        ambiente.cadastrar_ana(email="bia@aluno.puc-rio.br")
