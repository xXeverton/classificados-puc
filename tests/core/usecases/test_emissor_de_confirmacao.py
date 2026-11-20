from datetime import timedelta

from server.core.entities.politicas_autenticacao import hash_de_token
from server.core.entities.usuario import Usuario
from tests.core.usecases.conftest import URL_BASE


def salvar_usuario(ambiente) -> Usuario:
    return ambiente.usuarios.salvar(
        Usuario(
            nome="Ana",
            email="ana@aluno.puc-rio.br",
            nome_usuario="ana",
            vinculo="aluno",
            senha_hash="hash",
        )
    )


def test_emitir_stores_only_hash_valid_for_fifteen_minutes(ambiente):
    usuario = salvar_usuario(ambiente)

    ambiente.emissor.emitir(usuario)

    [token] = ambiente.tokens.tokens.values()
    assert token.usuario_id == usuario.id
    assert token.token_hash == hash_de_token("token-1")
    assert token.token_hash != "token-1"
    assert token.expira_em == ambiente.relogio.agora() + timedelta(
        minutes=15
    )


def test_emitir_sends_link_to_user_email(ambiente):
    usuario = salvar_usuario(ambiente)

    ambiente.emissor.emitir(usuario)

    email = ambiente.enviador.ultimo
    assert email.destinatario == "ana@aluno.puc-rio.br"
    assert f"{URL_BASE}?token=token-1" in email.corpo
    assert email.token == "token-1"


def test_emitir_invalidates_previous_tokens(ambiente):
    usuario = salvar_usuario(ambiente)
    ambiente.emissor.emitir(usuario)

    ambiente.emissor.emitir(usuario)

    agora = ambiente.relogio.agora()
    antigo = ambiente.tokens.buscar_por_hash(hash_de_token("token-1"))
    novo = ambiente.tokens.buscar_por_hash(hash_de_token("token-2"))
    assert not antigo.esta_valido(agora)
    assert novo.esta_valido(agora)
