"""Profile photo storage on the local disk."""

import re
import secrets
from pathlib import Path

from server.core.entities.foto_de_perfil import FotoDePerfil
from server.core.interfaces.armazenamento_de_foto_interface import (
    ArmazenamentoDeFotoInterface,
)

PREFIXO_URL = "/fotos-perfil/"
# Exactly the names this class generates: no "/", "\" or "..".
_NOME_GERADO = re.compile(r"[A-Za-z0-9_-]+\.(?:jpg|png|webp)")


class ArmazenamentoDeFotoLocal(ArmazenamentoDeFotoInterface):

    def __init__(self, diretorio: Path | str) -> None:
        self._diretorio = Path(diretorio)

    def salvar(self, foto: FotoDePerfil) -> str:
        self._diretorio.mkdir(parents=True, exist_ok=True)
        nome = f"{secrets.token_urlsafe(32)}.{foto.formato.value}"
        (self._diretorio / nome).write_bytes(foto.conteudo)
        return PREFIXO_URL + nome

    def ler(self, foto_url: str) -> bytes | None:
        arquivo = self._arquivo(foto_url)
        if arquivo is None or not arquivo.is_file():
            return None
        return arquivo.read_bytes()

    def remover(self, foto_url: str) -> None:
        arquivo = self._arquivo(foto_url)
        if arquivo is not None:
            arquivo.unlink(missing_ok=True)

    def _arquivo(self, foto_url: str) -> Path | None:
        """Path of a photo created here, or None for any other name."""
        if not foto_url.startswith(PREFIXO_URL):
            return None
        nome = foto_url[len(PREFIXO_URL):]
        if _NOME_GERADO.fullmatch(nome) is None:
            return None
        return self._diretorio / nome
