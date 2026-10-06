"""Fumaça com o provedor real: uma chamada a cada rota do backend (arquitetura, seção 9.1).

Fica de fora por padrão (marcador `live`, excluído no `addopts`) porque usa a internet e a
cota: cerca de 11 chamadas ao OpenWeatherMap, sendo 5 da consulta de clima e 1 por alerta
ativo. Rode manualmente com `pytest -m live`. A chave vem do ambiente ou do `.env` e nunca é
escrita no teste, no log nem na saída (P-001).
"""

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import API_KEY_VAR
from app.main import create_app
from app.schemas.view import CitySearchResult, ReverseResult, WeatherView

pytestmark = pytest.mark.live

ENV_FILE = Path(__file__).parent.parent.parent / ".env"
UBERLANDIA = "lat=-18.92&lon=-48.28"  # cidade padrão, pública (P-006)
PNG_SIGNATURE = b"\x89PNG"


def env_file_key() -> str | None:
    """Chave do `.env`, lida sem biblioteca extra (guardrail 1)."""
    if not ENV_FILE.exists():
        return None
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        name, _, value = line.partition("=")
        if name.strip() == API_KEY_VAR:
            return value.strip().strip("\"'") or None
    return None


@pytest.fixture(scope="module")
def live_client():
    """Backend com o cliente real, a chave do ambiente ou do `.env`."""
    key = os.environ.get(API_KEY_VAR) or env_file_key()
    if not key:
        pytest.skip("Sem a chave do OpenWeatherMap no ambiente ou no .env")
    with pytest.MonkeyPatch.context() as patch:
        patch.setenv(API_KEY_VAR, key)
        with TestClient(create_app()) as client:
            yield client, key


def assert_no_key(response, key: str) -> None:
    """A chave não volta na resposta (P-001)."""
    assert key not in response.text
    assert key not in str(response.headers)


def test_live_weather_returns_the_view_model(live_client):
    """RF-004, ADR-013: a consulta de clima real faz as 5 chamadas da One Call 4.0 e devolve
    um view model válido, com as condições atuais e as previsões."""
    client, key = live_client

    response = client.get(f"/api/weather?{UBERLANDIA}")

    assert response.status_code == 200, response.json()
    view = WeatherView.model_validate(response.json())
    assert view.current is not None
    assert view.daily and view.hourly
    assert_no_key(response, key)


def test_live_search_finds_the_city(live_client):
    """RF-006: a busca real encontra Uberlândia com o rótulo do cabeçalho."""
    client, key = live_client

    response = client.get("/api/geo/search?q=Uberlândia")

    assert response.status_code == 200, response.json()
    result = CitySearchResult.model_validate(response.json())
    assert any(city.header_label == "Uberlândia, BR" for city in result.results)
    assert_no_key(response, key)


def test_live_reverse_names_the_coordinate(live_client):
    """RF-002, RN-009: a geocodificação reversa real dá o nome da cidade da coordenada."""
    client, key = live_client

    response = client.get(f"/api/geo/reverse?{UBERLANDIA}")

    assert response.status_code == 200, response.json()
    result = ReverseResult.model_validate(response.json())
    assert result.result is not None
    assert result.result.header_label.endswith(", BR")
    assert_no_key(response, key)


def test_live_precipitation_tile_is_a_png(live_client):
    """RF-047, RN-049: a tile real da camada de chuva chega como PNG pelo proxy."""
    client, key = live_client

    response = client.get("/api/tiles/precipitation/6/23/36.png")

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content.startswith(PNG_SIGNATURE)
    assert_no_key(response, key)
