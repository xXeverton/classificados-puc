"""Rotas da prévia de publicação de anúncios."""

from flask import Flask, redirect, render_template, request, url_for

from use_cases.identidade_autenticada import Autenticador


def registrar_rota_novo_anuncio(
    app: Flask, autenticador: Autenticador
) -> None:
    """Registra a página e protege seu acesso com a porta de autenticação."""

    @app.get("/")
    def inicio():
        return redirect(url_for("novo_anuncio"))

    @app.get("/anuncios/novo")
    def novo_anuncio():
        if autenticador.usuario_atual() is None:
            return redirect(
                url_for("login_indisponivel", next=request.path)
            )
        return render_template("anuncios/novo.html")

    @app.get("/login")
    def login_indisponivel():
        return render_template("anuncios/login_indisponivel.html"), 503
