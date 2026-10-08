"""Testes das rotas `/api` com o provedor simulado (seções 6.1 e 6.4, RN-004, P-004)."""

import asyncio

import httpx
import pytest
from fastapi.testclient import TestClient

from app.clients.openweather import OpenWeatherClient
from app.domain.view_model import build_weather_view
from app.schemas.provider import OneCallBundle
from tests.fakes import CAPTURE_NOW, FAKE_KEY, TRANSPARENT_PNG

WEATHER = "/api/weather?lat=-18.92&lon=-48.28"
SEARCH = "/api/geo/search"
REVERSE = "/api/geo/reverse?lat=-18.92&lon=-48.28"
TILE = "/api/tiles/precipitation/6/23/35.png"

INVALID = {"error": "invalid_request"}


def forwarded_coords(fake_provider) -> set[tuple[str, str]]:
    """Coordenadas que a rota repassou ao provedor (os detalhes de alerta não as levam)."""
    return {
        (r.url.params["lat"], r.url.params["lon"])
        for r in fake_provider.requests
        if fake_provider.endpoint(r) != "alert"
    }


@pytest.fixture
def api(make_mock_app, fake_provider):
    with TestClient(make_mock_app(fake_provider)) as client:
        yield client


def assert_no_store(response):
    assert response.headers["cache-control"] == "no-store"


# --- /api/weather --------------------------------------------------------------------------


def test_rn_059_weather_returns_view_model(api, fake_provider, load_json):
    """Seção 6.1: `/api/weather` devolve o `WeatherView` montado a partir do pacote."""
    response = api.get(WEATHER)

    assert response.status_code == 200
    assert_no_store(response)
    view = response.json()
    assert view["timezone_offset"] == -10800
    assert view["current"]["alerts_label"] == "3 alertas"
    assert len(view["daily"]) == 10 and len(view["hourly"]) == 40 and len(view["minutely"]) == 60
    assert forwarded_coords(fake_provider) == {("-18.92", "-48.28")}


def test_rn_059_weather_matches_view_model_of_the_bundle(make_mock_app, fake_provider):
    """O JSON da rota é exatamente o view model do pacote do cliente (sem regra própria)."""

    async def bundle():
        async with httpx.AsyncClient(transport=httpx.MockTransport(fake_provider)) as http:
            return await OpenWeatherClient(http, FAKE_KEY, lambda: CAPTURE_NOW).weather(
                35.68, 139.69
            )

    expected = build_weather_view(OneCallBundle.model_validate(asyncio.run(bundle())))

    with TestClient(make_mock_app(fake_provider)) as client:
        response = client.get("/api/weather?lat=35.68&lon=139.69")

    assert response.json() == expected.model_dump(mode="json")


@pytest.mark.parametrize("coords", ["lat=90&lon=180", "lat=-90&lon=-180", "lat=0&lon=0"])
def test_rn_059_weather_accepts_coordinate_limits(api, fake_provider, coords):
    """Seção 6.1: latitude em [-90, 90] e longitude em [-180, 180], com os limites."""
    assert api.get(f"/api/weather?{coords}").status_code == 200
    lat, lon = (pair.split("=")[1] for pair in coords.split("&"))
    assert {(float(a), float(b)) for a, b in forwarded_coords(fake_provider)} == {
        (float(lat), float(lon))
    }


@pytest.mark.parametrize(
    "query",
    [
        "lat=90.01&lon=0",
        "lat=-91&lon=0",
        "lat=0&lon=180.5",
        "lat=0&lon=-181",
        "lat=abc&lon=0",
        "lat=nan&lon=0",
        "lat=0&lon=inf",
        "lon=0",
        "lat=0",
        "",
    ],
)
def test_rn_059_invalid_coordinates_return_400_without_calling_provider(api, fake_provider, query):
    """Seção 6.1: parâmetros inválidos dão 400 `invalid_request`, sem chamar o provedor."""
    for path in ("/api/weather", "/api/geo/reverse"):
        response = api.get(f"{path}?{query}")

        assert response.status_code == 400
        assert response.json() == INVALID
        assert_no_store(response)
    assert fake_provider.requests == []


# --- /api/geo/search -----------------------------------------------------------------------


def test_rn_004_search_returns_cities_with_labels(api):
    """RN-006 a RN-008: a busca devolve as cidades com os rótulos e a dica de corte."""
    response = api.get(SEARCH, params={"q": "Santa Maria"})

    assert response.status_code == 200
    assert_no_store(response)
    body = response.json()
    assert body["truncated"] is True
    assert body["results"][0]["header_label"] == "Santa Maria, BR"


def test_rn_004_search_without_results(api):
    """Seção 6.3: sem resultados, `results` vazio."""
    response = api.get(SEARCH, params={"q": "Xqzwvy"})

    assert response.json() == {"results": [], "truncated": False}


def test_rn_004_search_term_is_trimmed_before_calling_provider(api, fake_provider):
    """RN-004: os espaços das pontas são removidos antes da consulta."""
    api.get(SEARCH, params={"q": "   Santa Maria  "})

    assert fake_provider.requests[0].url.params["q"] == "Santa Maria"


@pytest.mark.parametrize("term", ["ab", "  ab  ", "a" * 100, " " + "a" * 100 + " ", "<b>Rio</b>"])
def test_rn_004_valid_terms_have_2_to_100_characters(api, fake_provider, term):
    """RN-004: de 2 a 100 caracteres sem os espaços das pontas, com qualquer caractere."""
    response = api.get(SEARCH, params={"q": term})

    assert response.status_code == 200
    assert fake_provider.requests[0].url.params["q"] == term.strip()


@pytest.mark.parametrize("params", [{"q": ""}, {"q": "a"}, {"q": "  a  "}, {"q": "a" * 101}, {}])
def test_rn_004_invalid_terms_return_400_without_calling_provider(api, fake_provider, params):
    """RN-004: termo vazio, de 1 caractere, acima de 100 ou ausente dá 400."""
    response = api.get(SEARCH, params=params)

    assert response.status_code == 400
    assert response.json() == INVALID
    assert_no_store(response)
    assert fake_provider.requests == []


def test_rn_004_search_ignores_items_that_are_not_cities(api, fake_provider):
    """Seção 6.2: item fora do formato na resposta da busca é ignorado, sem erro 500."""
    fake_provider.overrides["direct"] = httpx.Response(
        200, json=["x", {"name": "Uberlândia", "country": "BR", "lat": -18.9, "lon": -48.2}]
    )

    body = api.get(SEARCH, params={"q": "Uberlândia"}).json()

    assert [item["header_label"] for item in body["results"]] == ["Uberlândia, BR"]


# --- /api/geo/reverse ----------------------------------------------------------------------


def test_rn_009_reverse_returns_city(api, fake_provider):
    """RN-009: a geocodificação reversa devolve a cidade com os rótulos."""
    response = api.get(REVERSE)

    assert forwarded_coords(fake_provider) == {("-18.92", "-48.28")}

    assert response.status_code == 200
    assert_no_store(response)
    assert response.json()["result"]["header_label"] == "Uberlândia, BR"


def test_rn_009_reverse_without_city_returns_null(api, fake_provider):
    """RN-009: sem cidade para as coordenadas, `result` é `null` ("Sua localização")."""
    fake_provider.overrides["reverse"] = httpx.Response(200, json=[])

    assert api.get(REVERSE).json() == {"result": None}


# --- /api/tiles ----------------------------------------------------------------------------


@pytest.mark.parametrize("zxy", ["6/23/35", "0/0/0", "18/262143/262143"])
def test_adr_006_tile_is_passed_through_as_png(api, fake_provider, zxy):
    """Seção 6.1: a tile de chuva é repassada como PNG, com z/x/y na ordem pedida."""
    response = api.get(f"/api/tiles/precipitation/{zxy}.png")

    [request] = fake_provider.requests
    assert request.url.path == f"/map/precipitation_new/{zxy}.png"

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content == TRANSPARENT_PNG
    assert_no_store(response)


@pytest.mark.parametrize(
    "zxy", ["19/0/0", "-1/0/0", "6/64/0", "6/0/64", "6/-1/0", "a/0/0", "0/1/0"]
)
def test_adr_006_invalid_tile_returns_400_without_calling_provider(api, fake_provider, zxy):
    """Seção 6.1: `z` em [0, 18] e `x`, `y` em [0, 2^z − 1]; fora disso, 400."""
    response = api.get(f"/api/tiles/precipitation/{zxy}.png")

    assert response.status_code == 400
    assert response.json() == INVALID
    assert fake_provider.requests == []


# --- Erros do provedor (seção 6.4) ---------------------------------------------------------

PROVIDER_FAILURES = [
    (401, 502, "provider_unauthorized"),
    (429, 502, "provider_rate_limited"),
    (500, 502, "provider_unavailable"),
    (httpx.ReadTimeout("lento"), 504, "provider_timeout"),
    (httpx.ConnectError("sem rede"), 502, "network_unavailable"),
]


@pytest.mark.parametrize(("failure", "status", "code"), PROVIDER_FAILURES)
@pytest.mark.parametrize(
    ("endpoint", "path"),
    [("current", WEATHER), ("direct", f"{SEARCH}?q=Rio"), ("reverse", REVERSE), ("tile", TILE)],
)
def test_p_004_provider_errors_become_short_codes(
    api, fake_provider, endpoint, path, failure, status, code
):
    """P-004, seção 6.4: só `{"error": código}`, com 502 ou 504, sem o corpo do provedor."""
    fake_provider.overrides[endpoint] = failure

    response = api.get(path)

    assert response.status_code == status
    assert response.json() == {"error": code}
    assert "erro simulado" not in response.text
    assert_no_store(response)
