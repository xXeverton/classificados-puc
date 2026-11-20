from datetime import UTC, datetime, timedelta

from server.core.entities.sessao import Sessao

AGORA = datetime(2026, 11, 20, 12, 0, tzinfo=UTC)


def criar_sessao() -> Sessao:
    return Sessao(
        usuario_id=1,
        token_hash="hash",
        criada_em=AGORA,
        expira_em=AGORA + timedelta(hours=8),
    )


def test_session_is_active_until_expiration():
    sessao = criar_sessao()

    assert sessao.esta_ativa(AGORA)
    assert not sessao.esta_ativa(AGORA + timedelta(hours=8))


def test_revoked_session_is_inactive():
    sessao = criar_sessao().revogar(AGORA)

    assert sessao.revogada_em == AGORA
    assert not sessao.esta_ativa(AGORA)
