"""Pure password rules."""

TAMANHO_MINIMO_SENHA = 8


def validar_senha(senha: str) -> None:
    """Raise ValueError when the password does not meet the minimum rules."""
    if len(senha) < TAMANHO_MINIMO_SENHA:
        raise ValueError(
            f"Senha deve ter no mínimo {TAMANHO_MINIMO_SENHA} caracteres."
        )
