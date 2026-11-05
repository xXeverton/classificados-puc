"""Ponto de entrada da aplicação Flask (camada Frameworks & Drivers)."""

from flask import Flask


def create_app() -> Flask:
    """Cria e configura a instância da aplicação Flask (app factory)."""
    app = Flask(__name__)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    # Registre aqui os blueprints definidos em app/routes/
    # Ex.: app.register_blueprint(task_bp)

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
