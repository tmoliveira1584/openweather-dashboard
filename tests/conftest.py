"""Fixtures compartilhadas: chave falsa, JSON das fixtures, app simulado e servidor para e2e.

Nenhum teste usa a internet nem a cota: o provedor é simulado com httpx.MockTransport e,
nos testes de ponta a ponta, o navegador só alcança o servidor local e imagens falsas.
"""

import base64
import json
import re
import socket
import threading
import time
from pathlib import Path

import anyio
import httpx
import pytest
import uvicorn

from app.config import API_KEY_VAR
from app.main import create_app

TESTS_DIR = Path(__file__).parent
FIXTURES_DIR = TESTS_DIR / "fixtures"
E2E_DIR = TESTS_DIR / "e2e"

FAKE_KEY = "chave-falsa-de-teste"

# PNG transparente de 1x1, no lugar das tiles do CARTO e dos ícones do OpenWeatherMap.
TRANSPARENT_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
)
FAKE_IMAGE_URL = re.compile(
    r"^https://([a-d]\.)?basemaps\.cartocdn\.com/|^https://openweathermap\.org/img/wn/"
)


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(items):
    """Todo teste em tests/e2e/ recebe o marcador e2e, antes da seleção por -m."""
    for item in items:
        if E2E_DIR in Path(item.path).parents:
            item.add_marker(pytest.mark.e2e)


@pytest.fixture
def fake_key(monkeypatch):
    """Chave falsa no ambiente. A chave real nunca entra nos testes (P-001)."""
    monkeypatch.setenv(API_KEY_VAR, FAKE_KEY)
    return FAKE_KEY


@pytest.fixture
def load_json():
    """Carrega um arquivo de tests/fixtures/ pelo nome."""

    def load(name: str):
        return json.loads((FIXTURES_DIR / name).read_text(encoding="utf-8"))

    return load


@pytest.fixture
def make_mock_app():
    """Fábrica de apps com o provedor simulado: make_mock_app(handler) -> FastAPI.

    `handler` recebe um httpx.Request e devolve um httpx.Response.
    """
    clients = []

    def make(handler):
        http = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        clients.append(http)
        return create_app(client=http)

    yield make
    for http in clients:
        anyio.run(http.aclose)


def _provider_must_not_be_called(request: httpx.Request) -> httpx.Response:
    raise AssertionError(f"Teste de ponta a ponta tentou chamar o provedor ({request.url.host})")


@pytest.fixture(scope="session")
def live_server():
    """Backend numa thread, em porta livre, para os testes de ponta a ponta. Devolve a URL."""
    http = httpx.AsyncClient(transport=httpx.MockTransport(_provider_must_not_be_called))
    config = uvicorn.Config(create_app(client=http), log_level="warning", access_log=False)
    server = uvicorn.Server(config)

    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    thread = threading.Thread(target=server.run, kwargs={"sockets": [sock]}, daemon=True)
    thread.start()

    deadline = time.monotonic() + 10
    while not server.started:
        if time.monotonic() > deadline or not thread.is_alive():
            raise RuntimeError("O servidor de testes não iniciou.")
        time.sleep(0.02)

    yield f"http://127.0.0.1:{port}"

    server.should_exit = True
    thread.join(timeout=5)
    sock.close()
    anyio.run(http.aclose)


@pytest.fixture(scope="session")
def base_url(live_server):
    """Faz o page.goto("/") apontar para o live_server."""
    return live_server


@pytest.fixture
def page(page, base_url):
    """Página do Chrome sem internet.

    - arquivos do servidor local: seguem normalmente;
    - /api/* sem simulação no teste: abortado (o teste precisa simular com page.route);
    - tiles do CARTO e ícones do OpenWeatherMap: PNG transparente;
    - qualquer outro endereço: abortado.

    Rotas registradas depois, dentro do teste, têm prioridade sobre esta.
    """

    def offline(route):
        url = route.request.url
        if url.startswith(f"{base_url}/api/"):
            route.abort()
        elif url.startswith(f"{base_url}/"):
            route.continue_()
        elif FAKE_IMAGE_URL.match(url):
            route.fulfill(
                status=200,
                content_type="image/png",
                headers={"Access-Control-Allow-Origin": "*"},
                body=TRANSPARENT_PNG,
            )
        else:
            route.abort()

    page.route("**/*", offline)
    return page
