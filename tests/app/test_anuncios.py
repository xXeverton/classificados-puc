from app.main import create_app


def test_new_ad_page_renders_visual_preview():
    client = create_app().test_client()

    response = client.get("/anuncios/novo")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Prévia da tela" in html
    assert "Novo anúncio" in html
    assert 'id="titulo"' in html
    assert 'id="categoria"' in html
    assert 'id="estado_conservacao"' in html
    assert 'id="descricao"' in html
    assert 'id="preco"' in html
    assert 'type="button" disabled' in html


def test_home_redirects_to_new_ad_preview():
    response = create_app().test_client().get("/")

    assert response.status_code == 302
    assert response.headers["Location"] == "/anuncios/novo"
