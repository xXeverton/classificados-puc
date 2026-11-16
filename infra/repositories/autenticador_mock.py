"""Mock temporário de identidade até a implementação da autenticação."""

from use_cases.identidade_autenticada import UsuarioAutenticado


class AutenticadorMock:
    """MOCK TEMPORÁRIO: identidade fixa, sem sessão ou credenciais reais."""

    def __init__(
        self, usuario: UsuarioAutenticado | None = None
    ) -> None:
        self._usuario = usuario

    def usuario_atual(self) -> UsuarioAutenticado | None:
        """Retorna a identidade simulada; vazio por padrão e fail-closed."""
        return self._usuario
