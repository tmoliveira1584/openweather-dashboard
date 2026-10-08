"""Testes do `OpenWeatherClient` com o provedor simulado (seção 6.4, ADR-013, RN-012, RN-059)."""

import asyncio

import httpx
import pytest

from app.clients.openweather import (
    PROVIDER_TIMEOUT_S,
    OpenWeatherClient,
    ProviderError,
    merge_onecall,
)
from tests.fakes import CAPTURE_HOUR, CAPTURE_NOW, FAKE_KEY

UBERLANDIA = (-18.92, -48.28)
TOKYO = (35.68, 139.69)


def run(handler, method: str, *args):
    """Executa um método do cliente com o transporte simulado e devolve o resultado."""

    async def call():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
            client = OpenWeatherClient(http, FAKE_KEY, clock=lambda: CAPTURE_NOW)
            return await getattr(client, method)(*args)

    return asyncio.run(call())


def provider_error(handler, method: str = "weather", *args) -> ProviderError:
    with pytest.raises(ProviderError) as info:
        run(handler, method, *(args or UBERLANDIA))
    return info.value


@pytest.fixture
def uberlandia_bundle(load_json):
    u = "onecall4/uberlandia/"
    return merge_onecall(
        load_json(u + "current.json"),
        load_json(u + "1min.json"),
        [load_json(u + "1h_p1.json"), load_json(u + "1h_p2.json")],
        load_json(u + "1day.json"),
        [load_json(f"{u}alert_{i}.json") for i in (1, 2, 3)],
    )


# --- Consulta de clima ---------------------------------------------------------------------


def test_adr_013_weather_returns_bundle_from_5_calls_and_alert_details(
    fake_provider, uberlandia_bundle
):
    """ADR-013: 5 chamadas, mais o detalhe de cada alerta, combinadas em um pacote."""
    bundle = run(fake_provider, "weather", *UBERLANDIA)

    assert bundle == uberlandia_bundle
    endpoints = [fake_provider.endpoint(r) for r in fake_provider.requests]
    assert sorted(endpoints) == sorted(
        ["current", "1min", "1h_p1", "1h_p2", "1day", "alert", "alert", "alert"]
    )


def test_rn_059_weather_always_asks_metric_units_in_portuguese(fake_provider):
    """RN-059: toda chamada da One Call usa `units=metric`, `lang=pt_br`, as coordenadas e a chave."""
    run(fake_provider, "weather", *UBERLANDIA)

    onecall = [r for r in fake_provider.requests if fake_provider.endpoint(r) != "alert"]
    assert len(onecall) == 5
    for request in onecall:
        params = request.url.params
        assert request.url.host == "api.openweathermap.org"
        assert request.url.path.startswith("/data/4.0/onecall/")
        assert (params["units"], params["lang"], params["appid"]) == ("metric", "pt_br", FAKE_KEY)
        assert (params["lat"], params["lon"]) == ("-18.92", "-48.28")


def test_adr_013_hourly_pages_start_at_current_utc_hour_from_injected_clock(fake_provider):
    """ADR-013: a 1ª página por hora começa na hora UTC cheia do relógio e a 2ª, 20 h depois."""
    run(fake_provider, "weather", *UBERLANDIA)

    starts = sorted(
        int(r.url.params["start"]) for r in fake_provider.requests if "/timeline/1h" in r.url.path
    )
    assert starts == [CAPTURE_HOUR, CAPTURE_HOUR + 20 * 3600]


def test_adr_013_alert_detail_url_has_encoded_id_and_only_the_key(fake_provider):
    """ADR-013: o ID do alerta vai codificado na URL e a chamada leva só a chave."""
    run(fake_provider, "weather", *UBERLANDIA)

    alerts = [r for r in fake_provider.requests if fake_provider.endpoint(r) == "alert"]
    assert len(alerts) == 3
    for request in alerts:
        assert request.url.raw_path.startswith(b"/data/4.0/onecall/alert/urn%3Aoid%3A")
        assert dict(request.url.params) == {"appid": FAKE_KEY}


def test_adr_013_the_5_calls_run_in_parallel(load_json):
    """ADR-013, RNF-001: as 5 chamadas da One Call correm ao mesmo tempo."""
    in_flight = 0
    peak = 0

    async def slow_provider(request: httpx.Request) -> httpx.Response:
        nonlocal in_flight, peak
        in_flight += 1
        peak = max(peak, in_flight)
        await asyncio.sleep(0.05)
        in_flight -= 1
        return httpx.Response(200, json=load_json("onecall4/tokyo/current.json"))

    run(slow_provider, "weather", *TOKYO)

    assert peak == 5


def test_adr_013_city_without_alerts_makes_no_second_round(fake_provider):
    """ADR-013: sem IDs de alerta, não há segunda rodada e o pacote fica sem `alerts`."""
    bundle = run(fake_provider, "weather", *TOKYO)

    assert len(fake_provider.requests) == 5
    assert "alerts" not in bundle
    assert bundle["timezone_offset"] == 32400


@pytest.mark.parametrize(("endpoint", "block"), [("1min", "minutely"), ("1day", "daily")])
def test_adr_013_404_on_a_forecast_leaves_block_out(fake_provider, endpoint, block):
    """ADR-013, RF-038, RF-045: 404 numa previsão é falta de cobertura, não erro."""
    fake_provider.overrides[endpoint] = 404

    bundle = run(fake_provider, "weather", *UBERLANDIA)

    assert block not in bundle
    assert "current" in bundle


def test_adr_013_404_on_both_hourly_pages_leaves_hourly_out(fake_provider):
    """ADR-013: sem as 2 páginas por hora, o bloco por hora fica ausente."""
    fake_provider.overrides.update({"1h_p1": 404, "1h_p2": 404})

    assert "hourly" not in run(fake_provider, "weather", *UBERLANDIA)


def test_adr_013_404_on_current_is_provider_unavailable(fake_provider):
    """ADR-013, seção 6.4: 404 nos dados atuais derruba a consulta com `provider_unavailable`."""
    fake_provider.overrides["current"] = 404

    assert provider_error(fake_provider).code == "provider_unavailable"


def test_adr_013_404_on_alert_detail_keeps_alert_without_validity(fake_provider):
    """ADR-013: 404 no detalhe gera um alerta só com o `id`, que conta em todos os dias."""
    fake_provider.overrides["alert"] = 404

    bundle = run(fake_provider, "weather", *UBERLANDIA)

    assert len(bundle["alerts"]) == 3
    assert all(alert.keys() == {"id"} for alert in bundle["alerts"])


def test_adr_013_hourly_records_without_dt_are_kept_without_dedup():
    """ADR-013: só o `dt` repetido entre as páginas sai; registro sem `dt` passa adiante."""
    first = {"data": [{"dt": 1, "temp": 20}, {"temp": 21}]}
    second = {"data": [{"dt": 1, "temp": 22}, {"temp": 21}, {"dt": 2, "temp": 23}]}

    bundle = merge_onecall({"data": [{}]}, None, [first, second], None, None)

    assert bundle["hourly"] == [
        {"dt": 1, "temp": 20},
        {"temp": 21},
        {"temp": 21},
        {"dt": 2, "temp": 23},
    ]


def test_adr_013_current_without_timezone_offset_leaves_it_out_of_bundle():
    """ADR-013, seção 6.2: sem `timezone_offset` nos dados atuais, o pacote fica sem ele."""
    bundle = merge_onecall({"data": [{"dt": 1, "temp": 20}]}, None, [None, None], None, None)

    assert bundle == {"current": {"dt": 1, "temp": 20}}


def test_adr_013_blank_or_non_text_alert_ids_are_ignored(fake_provider, load_json):
    """ADR-013: só IDs de alerta em texto e não vazios geram a segunda rodada."""
    current = load_json("onecall4/uberlandia/current.json")
    valid_id = current["data"][0]["alerts"][0]
    current["data"][0]["alerts"] = ["", "   ", 7, None, valid_id]
    fake_provider.overrides["current"] = httpx.Response(200, json=current)

    bundle = run(fake_provider, "weather", *UBERLANDIA)

    requested = [
        r.url.path.rsplit("/", 1)[1]
        for r in fake_provider.requests
        if fake_provider.endpoint(r) == "alert"
    ]
    assert valid_id in requested
    assert all(alert_id.strip() and alert_id not in ("7", "None") for alert_id in requested)
    assert len(bundle["alerts"]) == len(requested)


def test_rn_012_unexpected_error_is_not_hidden_as_provider_error(fake_provider):
    """Seção 6.4: só falhas conhecidas do provedor viram código; um erro inesperado sobe."""
    fake_provider.overrides["1day"] = RuntimeError("defeito no código")

    with pytest.raises(RuntimeError, match="defeito no código"):
        run(fake_provider, "weather", *UBERLANDIA)


# --- Erros (seção 6.4) ---------------------------------------------------------------------

ERRORS = [
    (401, "provider_unauthorized"),
    (403, "provider_unauthorized"),
    (429, "provider_rate_limited"),
    (400, "provider_unavailable"),
    (500, "provider_unavailable"),
    (503, "provider_unavailable"),
    (httpx.ReadTimeout("lento"), "provider_timeout"),
    (httpx.ConnectTimeout("lento"), "provider_timeout"),
    (httpx.ConnectError("sem rede"), "network_unavailable"),
    (httpx.ReadError("conexão caiu"), "provider_unavailable"),
    (httpx.Response(200, content=b"<html>erro</html>"), "provider_unavailable"),
    (httpx.Response(200, json=[1, 2]), "provider_unavailable"),
]


@pytest.mark.parametrize(("failure", "code"), ERRORS)
@pytest.mark.parametrize("endpoint", ["current", "1min", "1h_p2", "1day", "alert"])
def test_rn_012_weather_errors_follow_section_6_4(fake_provider, endpoint, failure, code):
    """RN-012, seção 6.4: cada falha de qualquer chamada vira o código da tabela."""
    fake_provider.overrides[endpoint] = failure

    error = provider_error(fake_provider)

    assert error.code == code
    assert FAKE_KEY not in str(error)
    assert error.__cause__ is None
    assert error.__context__ is None or error.__suppress_context__


@pytest.mark.parametrize(
    ("failures", "code"),
    [
        ({"current": 500, "1min": 429, "1day": 401}, "provider_unauthorized"),
        ({"current": 500, "1min": 429, "1day": httpx.ReadTimeout("x")}, "provider_rate_limited"),
        ({"current": httpx.ConnectError("x"), "1day": httpx.ReadTimeout("x")}, "provider_timeout"),
        ({"current": 500, "1h_p1": httpx.ConnectError("x")}, "network_unavailable"),
        ({"current": 404, "1min": httpx.ConnectError("x")}, "network_unavailable"),
    ],
)
def test_rn_012_most_actionable_error_wins(fake_provider, failures, code):
    """Seção 6.4: com várias falhas, prevalece o código mais acionável."""
    fake_provider.overrides.update(failures)

    assert provider_error(fake_provider).code == code


def test_rn_012_every_call_has_15_second_timeout(fake_provider):
    """RN-012: cada chamada ao provedor tem tempo limite de 15 s."""
    run(fake_provider, "weather", *UBERLANDIA)
    run(fake_provider, "geocode", "Santa Maria")
    run(fake_provider, "reverse", *UBERLANDIA)
    run(fake_provider, "tile", 6, 23, 35)

    assert PROVIDER_TIMEOUT_S == 15
    for request in fake_provider.requests:
        timeout = request.extensions["timeout"]
        assert timeout == dict.fromkeys(("connect", "read", "write", "pool"), 15)


# --- Geocodificação e tiles ----------------------------------------------------------------


def test_rn_004_geocode_asks_up_to_5_cities(fake_provider, load_json):
    """Seção 6.1: a busca pede até 5 cidades à geocodificação direta, com o termo e a chave."""
    cities = run(fake_provider, "geocode", "Santa Maria")

    request = fake_provider.requests[0]
    assert cities == load_json("geo_direct_santa_maria.json")
    assert str(request.url).startswith("https://api.openweathermap.org/geo/1.0/direct?")
    assert dict(request.url.params) == {"q": "Santa Maria", "limit": "5", "appid": FAKE_KEY}


def test_rn_009_reverse_asks_one_city(fake_provider, load_json):
    """Seção 6.1: a geocodificação reversa pede 1 cidade para as coordenadas."""
    cities = run(fake_provider, "reverse", *UBERLANDIA)

    request = fake_provider.requests[0]
    assert cities == load_json("geo_reverse_uberlandia.json")
    assert request.url.path == "/geo/1.0/reverse"
    assert dict(request.url.params) == {
        "lat": "-18.92",
        "lon": "-48.28",
        "limit": "1",
        "appid": FAKE_KEY,
    }


@pytest.mark.parametrize(
    ("endpoint", "method", "args"),
    [
        ("direct", "geocode", ("Santa Maria",)),
        ("reverse", "reverse", UBERLANDIA),
        ("tile", "tile", (6, 23, 35)),
    ],
)
@pytest.mark.parametrize(("failure", "code"), ERRORS[:10])
def test_rn_012_geo_and_tile_errors_follow_section_6_4(
    fake_provider, endpoint, method, args, failure, code
):
    """Seção 6.4: a geocodificação e as tiles usam os mesmos códigos de erro."""
    fake_provider.overrides[endpoint] = failure

    assert provider_error(fake_provider, method, *args).code == code


@pytest.mark.parametrize("body", [{"cidades": []}, "Santa Maria"])
def test_rn_012_geocode_with_unexpected_format_is_provider_unavailable(fake_provider, body):
    """Seção 6.4: a geocodificação deve devolver uma lista; outro formato é falha do provedor."""
    fake_provider.overrides["direct"] = httpx.Response(200, json=body)

    assert provider_error(fake_provider, "geocode", "Santa Maria").code == "provider_unavailable"


def test_adr_006_tile_returns_png_bytes(fake_provider):
    """Seção 6.1: a tile de chuva vem da camada `precipitation_new`, com os bytes repassados."""
    content = run(fake_provider, "tile", 6, 23, 35)

    request = fake_provider.requests[0]
    assert content.startswith(b"\x89PNG")
    assert str(request.url) == (
        f"https://tile.openweathermap.org/map/precipitation_new/6/23/35.png?appid={FAKE_KEY}"
    )
