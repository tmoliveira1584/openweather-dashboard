"""Fixtures dos testes de ponta a ponta: `/api/weather` simulado (ver `weather_api.py`)."""

import pytest
from playwright.sync_api import Page

from tests.e2e.weather_api import WeatherApi, weather_view


@pytest.fixture(scope="session")
def weather_views() -> dict[str, dict]:
    """`WeatherView` de Uberlândia e de Tóquio, montados uma vez por sessão."""
    return {city: weather_view(city) for city in ("uberlandia", "tokyo")}


@pytest.fixture
def weather_api(page: Page, weather_views) -> WeatherApi:
    """Simulação do `/api/weather` registrada na página do teste."""
    return WeatherApi(page, weather_views)
