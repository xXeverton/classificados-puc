"""SQLite repository for persisted announcements."""

import sqlite3
from decimal import Decimal

from domain.anuncio import Anuncio, AnuncioPublicado


class RepositorioAnuncioSQLite:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def salvar(self, anuncio: Anuncio) -> AnuncioPublicado:
        cursor = self._connection.execute(
            """
            INSERT INTO anuncios (
                id_anunciante, titulo, descricao, preco, categoria,
                estado_conservacao
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                anuncio.id_anunciante,
                anuncio.titulo,
                anuncio.descricao,
                (
                    format(anuncio.preco, ".2f")
                    if anuncio.preco is not None
                    else None
                ),
                anuncio.categoria,
                anuncio.estado_conservacao,
            ),
        )
        self._connection.commit()

        row = self._connection.execute(
            """
            SELECT
                a.id, a.id_anunciante, u.nome, a.titulo, a.categoria,
                a.estado_conservacao, a.descricao, a.preco, a.created_at
            FROM anuncios AS a
            JOIN usuarios AS u ON u.id = a.id_anunciante
            WHERE a.id = ?
            """,
            (cursor.lastrowid,),
        ).fetchone()
        if row is None:
            raise RuntimeError("Persisted announcement was not found")

        return AnuncioPublicado(
            id=row["id"],
            id_anunciante=row["id_anunciante"],
            nome_anunciante=row["nome"],
            titulo=row["titulo"],
            categoria=row["categoria"],
            estado_conservacao=row["estado_conservacao"],
            descricao=row["descricao"],
            preco=(
                Decimal(str(row["preco"]))
                if row["preco"] is not None
                else None
            ),
            created_at=row["created_at"],
        )
