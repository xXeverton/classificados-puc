"""Preview route for the new-ad form."""

from flask import Flask, redirect, render_template, url_for


def registrar_rota_novo_anuncio(app: Flask) -> None:
    """Register the visual preview; it does not create announcements."""

    @app.get("/")
    def inicio():
        return redirect(url_for("novo_anuncio"))

    @app.get("/anuncios/novo")
    def novo_anuncio():
        return render_template("anuncios/novo.html")
