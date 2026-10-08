"""Testes de segurança: a chave e a localização nunca vazam (RNF-004, RNF-005, P-001, P-006,
P-007, guardrail 13).

Cada cenário passa por todas as rotas, com sucesso e com falhas do provedor, e confere as
respostas, os cabeçalhos e todo o log capturado em nível DEBUG.
"""

import logging

import httpx
import pytest
from fastapi.testclient import TestClient

from app.logging_setup import ACCESS_LOGGER
from tests.fakes import FAKE_KEY

LAT, LON = "-18.92", "-48.28"
PATHS = [
    f"/api/weather?lat={LAT}&lon={LON}",
    "/api/geo/search?q=Santa%20Maria",
    f"/api/geo/reverse?lat={LAT}&lon={LON}",
    "/api/tiles/precipitation/6/23/35.png",
    f"/api/weather?lat=999&lon={LON}",
]
FAILURES = {
    "sucesso": {},
    "chave recusada": dict.fromkeys(["current", "direct", "reverse", "tile"], 401),
    "tempo esgotado": dict.fromkeys(["1day", "direct", "reverse", "tile"], httpx.ReadTimeout("x")),
    "sem rede": dict.fromkeys(["1min", "direct", "reverse", "tile"], httpx.ConnectError("x")),
    "falha no alerta": {"alert": 500, "direct": 500, "reverse": 500, "tile": 500},
}


def call_every_route(make_mock_app, fake_provider, caplog) -> tuple[list[httpx.Response], str]:
    """Chama todas as rotas e devolve as respostas e o texto de todo o log capturado."""
    caplog.set_level(logging.DEBUG)
    with TestClient(make_mock_app(fake_provider)) as client:
        responses = [client.get(path) for path in PATHS]
    log = "\n".join(f"{r.name} {r.getMessage()}" for r in caplog.records)
    return responses, log


def response_text(response: httpx.Response) -> str:
    headers = "\n".join(f"{name}: {value}" for name, value in response.headers.items())
    return f"{headers}\n{response.content.decode('latin-1')}"


@pytest.mark.parametrize("failures", FAILURES.values(), ids=FAILURES.keys())
def test_rnf_004_key_never_appears_in_responses_or_log(
    make_mock_app, fake_provider, caplog, failures
):
    """RNF-004, P-001: a chave não aparece em nenhuma resposta, cabeçalho ou linha de log."""
    fake_provider.overrides.update(failures)

    responses, log = call_every_route(make_mock_app, fake_provider, caplog)

    assert all(FAKE_KEY in r.url.params.get("appid", "") for r in fake_provider.requests)
    for response in responses:
        assert FAKE_KEY not in response_text(response)
        assert "appid" not in response_text(response)
    assert FAKE_KEY not in log
    assert "appid" not in log


@pytest.mark.parametrize("failures", FAILURES.values(), ids=FAILURES.keys())
def test_p_006_log_has_no_query_string_nor_coordinates(
    make_mock_app, fake_provider, caplog, failures
):
    """P-006, RNF-005: o log não traz query string, coordenadas, termo de busca nem os z/x/y
    das tiles."""
    fake_provider.overrides.update(failures)

    _, log = call_every_route(make_mock_app, fake_provider, caplog)

    access = [r.getMessage() for r in caplog.records if r.name == ACCESS_LOGGER]
    assert len(access) == len(PATHS)
    for forbidden in ("?", "lat", LAT, LON, "-18.9", "Santa", "/6/23/35"):
        assert forbidden not in log, forbidden


@pytest.mark.parametrize("failures", FAILURES.values(), ids=FAILURES.keys())
def test_rnf_005_responses_set_no_cookie_and_are_not_stored(
    make_mock_app, fake_provider, caplog, failures
):
    """RNF-005, P-007: nenhuma rota grava cookie no navegador, e toda resposta do `/api`, com
    as coordenadas consultadas, sai com `Cache-Control: no-store`."""
    fake_provider.overrides.update(failures)

    responses, _ = call_every_route(make_mock_app, fake_provider, caplog)

    for response in responses:
        assert "set-cookie" not in response.headers
        assert response.headers["cache-control"] == "no-store"


def test_p_001_http_libraries_do_not_log_urls_even_in_debug(
    make_mock_app, fake_provider, caplog, monkeypatch
):
    """P-001: httpx e httpcore ficam em WARNING; em INFO, registrariam a URL com a chave.

    Os níveis voltam ao padrão antes do teste: quem os ajusta tem de ser o `create_app`, e não
    um teste que rodou antes."""
    for name in ("httpx", "httpcore"):
        monkeypatch.setattr(logging.getLogger(name), "level", logging.NOTSET)

    call_every_route(make_mock_app, fake_provider, caplog)

    assert logging.getLogger("httpx").level == logging.WARNING
    assert not [r for r in caplog.records if r.name.startswith(("httpx", "httpcore"))]


def test_guardrail_13_pagination_links_never_reach_response_nor_log(
    make_mock_app, fake_provider, caplog
):
    """Guardrail 13, ADR-013: os links `next`/`prev`, que trazem a chave, são descartados."""
    fake_provider.with_links = True

    responses, log = call_every_route(make_mock_app, fake_provider, caplog)

    weather = responses[0]
    assert weather.status_code == 200
    for text in (weather.text, log):
        assert "data/4.0/onecall" not in text
        assert '"next"' not in text and '"prev"' not in text
        assert FAKE_KEY not in text
    # Nenhum link seguido: só as 5 chamadas da One Call e os 3 detalhes de alerta.
    weather_calls = [r for r in fake_provider.requests if "onecall" in r.url.path]
    assert len(weather_calls) == 8
    assert all("lat" in r.url.params or "/alert/" in r.url.path for r in weather_calls)


def test_p_001_provider_error_log_has_only_endpoint_code_and_status(
    make_mock_app, fake_provider, caplog
):
    """Seção 7.6: a falha do provedor vai para o log só com o endpoint, o código e o status."""
    fake_provider.overrides["current"] = 401

    call_every_route(make_mock_app, fake_provider, caplog)

    provider_lines = [r.getMessage() for r in caplog.records if r.name == "app.provider"]
    assert "Falha no provedor: onecall/current provider_unauthorized HTTP 401" in provider_lines
    assert all("erro simulado" not in line for line in provider_lines)
