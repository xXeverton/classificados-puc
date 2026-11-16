from server.app import create_app


def test_health_endpoint_returns_ok_and_allows_configured_origin():
    app = create_app(
        {
            "DATABASE_URL": "sqlite:///:memory:",
            "CORS_ORIGINS": ["https://frontend.example"],
        }
    )

    response = app.test_client().get(
        "/health",
        headers={"Origin": "https://frontend.example"},
    )

    assert response.status_code == 200
    assert response.json == {"status": "ok"}
    assert response.headers["Access-Control-Allow-Origin"] == (
        "https://frontend.example"
    )
    app.extensions["database_engine"].dispose()
