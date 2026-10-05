"""Testes do log próprio (P-006) e do nível dos loggers do httpx (P-001)."""

import logging
import re

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.logging_setup import ACCESS_LOGGER, AccessLogMiddleware, configure_logging


@pytest.fixture
def client():
    app = FastAPI()
    app.add_middleware(AccessLogMiddleware)

    @app.get("/ping")
    def ping():
        return {"ok": True}

    @app.get("/tiles/{z}/{x}/{y}.png")
    def tile(z: int, x: int, y: int):
        return {"ok": True}

    @app.get("/boom")
    def boom():
        raise RuntimeError("falha simulada")

    return TestClient(app, raise_server_exceptions=False)


def access_lines(caplog):
    return [r.getMessage() for r in caplog.records if r.name == ACCESS_LOGGER]


def test_p_006_access_log_has_method_path_status_duration(client, caplog):
    """P-006: a linha tem método, caminho, status e duração, sem a query string."""
    caplog.set_level(logging.INFO, logger=ACCESS_LOGGER)

    client.get("/ping?lat=-18.91&lon=-48.27")

    [line] = access_lines(caplog)
    assert re.fullmatch(r"GET /ping 200 \d+ms", line)
    assert "-18.91" not in caplog.text
    assert "-48.27" not in caplog.text


def test_p_006_access_log_hides_path_params(client, caplog):
    """P-006: rota com coordenadas no caminho registra o modelo da rota, não os valores."""
    caplog.set_level(logging.INFO, logger=ACCESS_LOGGER)

    client.get("/tiles/10/377/571.png")

    [line] = access_lines(caplog)
    assert re.fullmatch(r"GET /tiles/\{z\}/\{x\}/\{y\}\.png 200 \d+ms", line)
    assert "377" not in caplog.text
    assert "571" not in caplog.text


def test_p_006_access_log_uses_path_when_no_route_matches(client, caplog):
    """P-006: sem rota encontrada, registra o caminho sem a query string."""
    caplog.set_level(logging.INFO, logger=ACCESS_LOGGER)

    client.get("/nao-existe?q=Uberlandia")

    [line] = access_lines(caplog)
    assert re.fullmatch(r"GET /nao-existe 404 \d+ms", line)


def test_p_006_access_log_records_500_on_exception(client, caplog):
    """P-006: uma exceção na rota é registrada com status 500."""
    caplog.set_level(logging.INFO, logger=ACCESS_LOGGER)

    response = client.get("/boom")

    assert response.status_code == 500
    [line] = access_lines(caplog)
    assert re.fullmatch(r"GET /boom 500 \d+ms", line)


def test_p_001_httpx_loggers_at_warning():
    """P-001: httpx e httpcore em WARNING, porque em INFO registram a URL com o appid."""
    configure_logging()
    configure_logging()

    assert logging.getLogger("httpx").level == logging.WARNING
    assert logging.getLogger("httpcore").level == logging.WARNING
    assert len(logging.getLogger("app").handlers) == 1
