"""Testes da montagem da aplicação: inicialização, página estática, log e acesso sem login
(P-002, P-006, P-025)."""

import logging
import re

import httpx
import pytest
from fastapi.testclient import TestClient

from app.clients.openweather import OpenWeatherClient
from app.config import API_KEY_VAR, ConfigError
from app.logging_setup import ACCESS_LOGGER
from app.main import create_app


def test_p_002_app_fails_to_start_without_api_key(monkeypatch):
    """P-002: sem a chave no ambiente, a aplicação não inicia."""
    monkeypatch.delenv(API_KEY_VAR, raising=False)

    with pytest.raises(ConfigError, match=API_KEY_VAR), TestClient(create_app()):
        pass


def test_p_025_no_route_requires_sign_up_or_login(fake_key):
    """P-025: não há rota de cadastro, login ou sessão, nenhum esquema de autenticação na API,
    e a página abre sem credenciais e sem gravar cookie."""
    with TestClient(create_app()) as client:
        page = client.get("/")
        schema = client.get("/openapi.json").json()

    paths = list(schema["paths"])
    assert paths
    assert not [
        p for p in paths if re.search(r"login|logout|sign|regist|auth|user|sess|account", p)
    ]
    assert "securitySchemes" not in schema.get("components", {})
    assert page.status_code == 200
    assert "set-cookie" not in page.headers


def test_setup_mock_app_skips_settings(monkeypatch, make_mock_app):
    """Com o provedor simulado, a inicialização não lê a chave nem cria cliente real."""
    monkeypatch.delenv(API_KEY_VAR, raising=False)
    app = make_mock_app(lambda request: httpx.Response(200, json={}))

    with TestClient(app):
        assert isinstance(app.state.client, OpenWeatherClient)
        assert not hasattr(app.state, "http")


def test_setup_serves_index_in_pt_br(fake_key):
    """A página é servida em / com o idioma pt-BR."""
    with TestClient(create_app()) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert '<html lang="pt-BR">' in response.text


@pytest.mark.parametrize(
    ("path", "content_type"),
    [
        ("leaflet.js", "javascript"),
        ("leaflet.css", "text/css"),
        ("images/marker-icon.png", "image/png"),
    ],
)
def test_setup_serves_vendored_leaflet(fake_key, path, content_type):
    """O Leaflet 1.9.4 é servido da cópia local, sem CDN (guardrail 2)."""
    with TestClient(create_app()) as client:
        response = client.get(f"/vendor/leaflet-1.9.4/{path}")

    assert response.status_code == 200
    assert content_type in response.headers["content-type"]


def test_setup_http_client_lifecycle(fake_key):
    """Um único httpx.AsyncClient, com tempo limite de 15 s, criado e fechado no lifespan."""
    app = create_app()

    with TestClient(app):
        http = app.state.http
        assert not http.is_closed
        assert http.timeout.connect == http.timeout.read == 15
        assert app.state.settings.openweather_api_key == fake_key

    assert http.is_closed


def test_p_006_requests_are_logged(fake_key, caplog):
    """P-006: o middleware de log está ligado na aplicação."""
    caplog.set_level(logging.INFO, logger=ACCESS_LOGGER)

    with TestClient(create_app()) as client:
        client.get("/?lat=-18.91&lon=-48.27")

    lines = [r.getMessage() for r in caplog.records if r.name == ACCESS_LOGGER]
    assert len(lines) == 1
    assert re.fullmatch(r"GET / 200 \d+ms", lines[0])
