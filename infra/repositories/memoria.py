"""Repositórios em memória.

Usados nos testes e, por enquanto, na aplicação: o schema SQLite ainda não
tem senha, tentativas de login nem links mágicos.
"""

from dataclasses import replace
from typing import Iterable, Optional

from domain.autenticacao import LinkMagico, TentativasLogin
from domain.usuario import Usuario


class UsuarioRepositoryMemoria:
    def __init__(self, usuarios: Iterable[Usuario] = ()) -> None:
        self._por_id: dict[int, Usuario] = {}
        for usuario in usuarios:
            self.adicionar(usuario)

    def adicionar(self, usuario: Usuario) -> None:
        self._por_id[usuario.id] = usuario

    def buscar_por_email(self, email: str) -> Optional[Usuario]:
        email = email.lower()
        return next(
            (u for u in self._por_id.values() if u.email.lower() == email),
            None,
        )

    def buscar_por_id(self, usuario_id: int) -> Optional[Usuario]:
        return self._por_id.get(usuario_id)


class TentativasLoginRepositoryMemoria:
    def __init__(self) -> None:
        self._por_email: dict[str, TentativasLogin] = {}

    def obter(self, email: str) -> TentativasLogin:
        return self._por_email.get(email, TentativasLogin())

    def salvar(self, email: str, tentativas: TentativasLogin) -> None:
        self._por_email[email] = tentativas

    def limpar(self, email: str) -> None:
        self._por_email.pop(email, None)


class LinkMagicoRepositoryMemoria:
    def __init__(self) -> None:
        self._por_hash: dict[str, LinkMagico] = {}

    def salvar(self, link: LinkMagico) -> None:
        self._por_hash[link.token_hash] = link

    def buscar_por_token_hash(self, token_hash: str) -> Optional[LinkMagico]:
        return self._por_hash.get(token_hash)

    def marcar_como_usado(self, token_hash: str) -> None:
        link = self._por_hash.get(token_hash)
        if link is not None:
            self._por_hash[token_hash] = replace(link, usado=True)
