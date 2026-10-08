"""Testes do view model (seção 6.3): pacote da One Call → `WeatherView`, e busca de cidades."""

import pytest

from app.clients.openweather import merge_onecall
from app.domain.formatting import MISSING
from app.domain.view_model import build_search_result, build_weather_view
from app.schemas.provider import GeoResult, OneCallBundle

ALERT_IDS = ["urn:oid:a", "urn:oid:b", "urn:oid:c"]

# Pacote que deve gerar o exemplo de `WeatherView` da seção 6.3 (Uberlândia às 08:18).
EXAMPLE_BUNDLE = {
    "timezone_offset": -10800,
    "current": {
        "dt": 1791112680,
        "temp": 20.4,
        "feels_like": 20.6,
        "pressure": 1015,
        "humidity": 94,
        "dew_point": 19.0,
        "uvi": 2.1,
        "visibility": 10000,
        "wind_speed": 4.0,
        "wind_deg": 90,
        "weather": [{"id": 804, "description": "nublado", "icon": "04d"}],
        "alerts": ALERT_IDS,
    },
    "daily": [
        {
            "dt": 1791417600,  # 2026-10-08 00:00 UTC
            "temp": {"max": 35, "min": 21.4},
            "feels_like": {"day": 36},
            "humidity": 40,
            "pressure": 1012,
            "dew_point": 14,
            "uvi": 9,
            "wind_speed": 3,
            "wind_deg": 45,
            "weather": [{"id": 800, "description": "céu limpo", "icon": "01d"}],
        }
    ],
    "hourly": [
        {
            "dt": 1791111600,
            "temp": 20.4,
            "pop": 0.21,
            "rain": {"1h": 0.21},
            "weather": [{"id": 500, "description": "chuva leve", "icon": "10d"}],
        }
    ],
    "minutely": [{"dt": 1791112680, "precipitation": 0.3}],
    "alerts": [{"id": i, "start": 1791190500, "end": 1791255540} for i in ALERT_IDS],
}


def build(raw: dict) -> dict:
    return build_weather_view(OneCallBundle.model_validate(raw)).model_dump()


@pytest.fixture
def uberlandia(load_json) -> dict:
    """Pacote real de Uberlândia, montado a partir das capturas da T-0.8."""
    u = "onecall4/uberlandia/"
    return merge_onecall(
        load_json(u + "current.json"),
        load_json(u + "1min.json"),
        [load_json(u + "1h_p1.json"), load_json(u + "1h_p2.json")],
        load_json(u + "1day.json"),
        [load_json(f"{u}alert_{i}.json") for i in (1, 2, 3)],
    )


@pytest.fixture
def tokyo(load_json) -> dict:
    t = "onecall4/tokyo/"
    return merge_onecall(
        load_json(t + "current.json"),
        load_json(t + "1min.json"),
        [load_json(t + "1h_p1.json"), load_json(t + "1h_p2.json")],
        load_json(t + "1day.json"),
        None,
    )


# --- Contrato ------------------------------------------------------------------------------


def test_rn_016_view_matches_architecture_example(load_json):
    """RN-016, RN-035, P-013: o pacote de exemplo gera o `WeatherView` da seção 6.3."""
    expected = load_json("weather_view_example.json")

    view = build(EXAMPLE_BUNDLE)

    temp_value = view["hourly"][0].pop("temp_value")
    expected_value = expected["hourly"][0].pop("temp_value")
    assert temp_value == pytest.approx(expected_value)
    assert view == expected


@pytest.mark.parametrize(("city", "time"), [("uberlandia", "16:41"), ("tokyo", "04:41")])
def test_p_013_real_captures_build_complete_view(request, city, time):
    """As capturas reais geram os 4 blocos, com todos os dias, horas e minutos recebidos."""
    raw = request.getfixturevalue(city)

    view = build(raw)

    assert view["current"]["time_label"] == time
    assert len(view["daily"]) == len(raw["daily"]) == 10
    assert len(view["hourly"]) == 40
    assert len(view["minutely"]) == 60


# --- Card principal (RN-016) ---------------------------------------------------------------


def test_rn_016_description_gets_capital_first_letter_and_feels_like_prefix(uberlandia):
    """RN-016: "chuva leve" vira "Chuva leve", e a sensação aparece como "Sensação de 21°"."""
    current = build(uberlandia)["current"]

    assert current["description"] == "Chuva leve"
    assert current["feels_like"] == {"c": "Sensação de 21°", "f": "Sensação de 70°"}
    assert current["temp"] == {"c": "21°", "f": "69°"}
    assert current["time_label"] == "16:41"


@pytest.mark.parametrize(
    ("description", "expected"),
    [("céu limpo", "Céu limpo"), ("Nublado", "Nublado"), ("é nublado", "É nublado")],
)
def test_rn_016_only_first_letter_changes(description, expected):
    """RN-016: só a primeira letra muda; o restante fica como o provedor mandou."""
    raw = {"timezone_offset": 0, "current": {"weather": [{"description": description}]}}

    assert build(raw)["current"]["description"] == expected


@pytest.mark.parametrize("weather", [None, [], [{"description": ""}], [{"description": "  "}]])
def test_p_013_missing_description_shows_dash(weather):
    """P-013: sem descrição, o card mostra "—" (caso de borda 5 da feature 2)."""
    raw = {"timezone_offset": 0, "current": {"weather": weather}}

    current = build(raw)["current"]

    assert current["description"] == MISSING
    assert current["condition_group"] == "neutral"
    assert current["icon"] is None


def test_p_013_partial_bundle_shows_dash_for_missing_current_values(load_json):
    """P-013, RF-023, CA-014: campo ausente mostra "—" e os demais aparecem normalmente."""
    view = build(load_json("onecall_partial.json"))

    current = view["current"]
    assert current["indicators"]["visibility"] == MISSING
    assert current["indicators"]["dew_point"] == {"c": MISSING, "f": MISSING}
    assert current["indicators"]["wind"] == {"c": "6 m/s", "f": "14 mph"}
    assert current["feels_like"] == {"c": "Sensação de —", "f": "Sensação de —"}
    assert current["indicators"]["humidity"] == "94%"
    assert current["temp"] == {"c": "21°", "f": "69°"}


def test_p_013_bundle_without_current_shows_dash_everywhere():
    """P-013: sem o registro atual, o card principal mostra "—" e o selo fica oculto."""
    current = build({"timezone_offset": 0})["current"]

    assert current["dt"] is None
    assert current["time_label"] == MISSING
    assert current["temp"] == {"c": MISSING, "f": MISSING}
    assert current["alerts_label"] is None
    indicators = current["indicators"]
    assert indicators["wind"] == indicators["dew_point"] == {"c": MISSING, "f": MISSING}
    assert {indicators[k] for k in ("humidity", "visibility", "pressure", "uvi")} == {MISSING}


def test_rn_018_today_badge_counts_distinct_ids_of_current(uberlandia, tokyo, load_json):
    """RN-018, CA-010: o selo de "Hoje" conta os IDs distintos de `current.alerts`."""
    assert build(uberlandia)["current"]["alerts_label"] == "3 alertas"
    assert build(load_json("onecall_alerts.json"))["current"]["alerts_label"] == "2 alertas"
    assert build(tokyo)["current"]["alerts_label"] is None


# --- Previsão diária -------------------------------------------------------------------------


def test_rn_026_day_date_is_utc_date_of_dt_without_offset(uberlandia):
    """RN-026, RN-028, RN-030, ADR-013: a data do dia é a data UTC do `dt`, sem somar o fuso."""
    first = build(uberlandia)["daily"][0]

    assert first["local_date"] == "2026-10-05"
    assert first["weekday_label"] == "Seg"
    assert first["date_label"] == "Seg, 05/10"


def test_rn_027_daily_keeps_every_day_received(tokyo):
    """RN-027, D-14: o view model não corta dias; o limite de 8 a partir de "Hoje" é do frontend.

    Em Tóquio, o primeiro dia (05/10) já é "ontem" no horário local da captura.
    """
    dates = [day["local_date"] for day in build(tokyo)["daily"]]

    assert dates[0] == "2026-10-05"
    assert len(dates) == 10


def test_rn_031_day_summary_uses_forecast_values(uberlandia):
    """RN-029, RN-031: máxima, mínima, sensação diurna e indicadores previstos para o dia."""
    first = build(uberlandia)["daily"][0]

    assert first["max"] == {"c": "22°", "f": "72°"}
    assert first["min_label"] == {"c": "Mín. 19°", "f": "Mín. 65°"}
    assert first["feels_like"] == {"c": "Sensação de 20°", "f": "Sensação de 69°"}
    assert first["description"] == "Chuva moderada"
    assert first["indicators"]["visibility"] == MISSING
    assert first["indicators"]["pressure"] == "1018 hPa"


def test_rn_031_day_visibility_is_shown_when_forecast_has_it():
    """RN-031: com `visibility` no dia, o card mostra o valor no formato de RN-021."""
    raw = {"timezone_offset": 0, "daily": [{"dt": 1791417600, "visibility": 2500}]}

    day = build(raw)["daily"][0]

    assert day["indicators"]["visibility"] == "2,5 km"
    assert day["max"] == {"c": MISSING, "f": MISSING}
    assert day["min_label"] == {"c": "Mín. —", "f": "Mín. —"}


def test_rn_032_day_badge_counts_alerts_by_validity(load_json):
    """RN-032, CA-021: o selo de cada dia conta os alertas cuja vigência alcança o dia.

    `teste.a` vai de quarta 18:00 a quinta 06:00; `teste.b`, de terça 12:00 a quarta 00:00.
    """
    labels = {
        day["weekday_label"]: day["alerts_label"]
        for day in build(load_json("onecall_alerts.json"))["daily"][:5]
    }

    assert labels == {
        "Seg": None,
        "Ter": "1 alerta",
        "Qua": "1 alerta",
        "Qui": "1 alerta",
        "Sex": None,
    }


def test_rn_032_real_alerts_reach_monday_and_tuesday(uberlandia):
    """RN-032: as vigências reais (2 alertas na segunda e 1 na terça) aparecem nos dias certos."""
    labels = [day["alerts_label"] for day in build(uberlandia)["daily"][:3]]

    assert labels == ["2 alertas", "1 alerta", None]


# --- Hora a hora (RN-035) ------------------------------------------------------------------


def test_rn_035_weekday_only_at_local_midnight(uberlandia):
    """RN-035: a hora "00:00" local mostra o dia da semana; as demais, `null`."""
    hourly = build(uberlandia)["hourly"]

    midnights = [h for h in hourly if h["hour_label"] == "00:00"]
    assert [h["weekday_label"] for h in midnights] == ["Ter", "Qua"]
    assert all(h["weekday_label"] is None for h in hourly if h["hour_label"] != "00:00")
    assert hourly[0]["hour_label"] == "16:00"


def test_rn_035_hour_in_city_timezone(tokyo):
    """RN-035, RN-015: a hora segue o fuso da cidade, não o da máquina."""
    first = build(tokyo)["hourly"][0]

    assert first["hour_label"] == "04:00"


def test_rn_037_hour_rain_and_pop(uberlandia):
    """RN-036, RN-037: chance em % e volume com 2 casas; sem chuva, `rain_label` = `null`."""
    hourly = build(uberlandia)["hourly"]

    assert hourly[0]["pop"] == "100%"
    assert hourly[0]["rain_value"] == 0.66
    assert hourly[0]["rain_label"] == "0,66 mm/h"
    dry = next(h for h in hourly if h["rain_value"] is None)
    assert dry["rain_label"] is None


def test_p_013_hour_without_temperature():
    """P-013: hora sem temperatura mostra "—" e não tem posição na curva."""
    raw = {"timezone_offset": 0, "hourly": [{"dt": 1791111600}]}

    hour = build(raw)["hourly"][0]

    assert hour["temp"] == {"c": MISSING, "f": MISSING}
    assert hour["temp_value"] == {"c": None, "f": None}
    assert hour["pop"] == MISSING
    assert hour["description"] == MISSING


# --- Por minuto ----------------------------------------------------------------------------


def test_rn_041_minutes_get_band_and_tooltip(load_json):
    """RN-041, RN-045, RN-047, CA-027, CA-028: faixa e cursor de cada minuto da variante."""
    minutes = build(load_json("onecall_minutely_bands.json"))["minutely"][:11]

    assert [m["band"] for m in minutes] == [
        "none",
        "light",
        "light",
        "moderate",
        "moderate",
        "heavy",
        "heavy",
        "extreme",
        "extreme",
        None,
        None,
    ]
    # 0 mm/h continua 0, e não "sem dado" (RN-047); -1 é dado inválido.
    assert [m["intensity"] for m in minutes] == [
        0,
        0.3,
        0.5,
        1.0,
        2.5,
        5.0,
        7.5,
        8.0,
        12,
        None,
        None,
    ]
    # Horários esperados calculados à mão: dt da variante em UTC-3.
    assert minutes[0]["tooltip"] == "16:42 — 0,00 mm/h"
    assert minutes[1]["tooltip"] == "16:43 — 0,30 mm/h"
    assert minutes[-1]["tooltip"] == "16:52 — —"


# --- Blocos ausentes -----------------------------------------------------------------------


@pytest.mark.parametrize(
    ("name", "absent"),
    [("onecall_no_minutely.json", {"minutely"}), ("onecall_partial.json", {"hourly", "daily"})],
)
def test_p_013_missing_block_becomes_null(load_json, name, absent):
    """RF-038, RF-045, CA-025, CA-032: bloco ausente = `null`; os demais aparecem."""
    view = build(load_json(name))

    for block in ("daily", "hourly", "minutely"):
        assert (view[block] is None) == (block in absent), block


@pytest.mark.parametrize("value", [[], [None], [{"precipitation": 0.3}]])
def test_p_013_block_without_usable_records_becomes_null(value):
    """P-013, D-15: lista vazia, itens inválidos ou registros sem `dt` viram bloco `null`."""
    raw = {"timezone_offset": 0, "minutely": value, "hourly": value, "daily": value}

    view = build(raw)

    assert (view["minutely"], view["hourly"], view["daily"]) == (None, None, None)


def test_p_013_records_without_dt_are_dropped():
    """D-15: só o registro sem `dt` é descartado; os demais seguem."""
    raw = {"timezone_offset": 0, "minutely": [{"precipitation": 1}, {"dt": 60, "precipitation": 1}]}

    assert [m["dt"] for m in build(raw)["minutely"]] == [60]


def test_p_013_without_timezone_offset_time_blocks_are_null(uberlandia):
    """P-013, P-015, D-15: sem fuso, os blocos que dependem da hora local ficam indisponíveis."""
    del uberlandia["timezone_offset"]

    view = build(uberlandia)

    assert view["timezone_offset"] is None
    assert (view["daily"], view["hourly"], view["minutely"]) == (None, None, None)
    assert view["current"]["time_label"] == MISSING
    assert view["current"]["temp"] == {"c": "21°", "f": "69°"}


# --- Busca de cidades ------------------------------------------------------------------------


def geo(name: str, **fields) -> GeoResult:
    return GeoResult(**{"name": name, "country": "BR", "lat": -10.0, "lon": -50.0, **fields})


def test_rn_008_search_result_from_real_capture(load_json):
    """RN-006 a RN-008: cada cidade da captura vira um item com os 3 rótulos, na ordem."""
    raw = [GeoResult.model_validate(item) for item in load_json("geo_direct_santa_maria.json")]

    result = build_search_result(raw).model_dump()

    assert [item["list_label"] for item in result["results"]] == [
        "Santa Maria, Rio Grande do Sul, BR",
        "Santa Maria, California, US",
        "Santa-Maria-Siché, Corsica, FR",
        "Ilha de Santa Maria, PT",
        "Santa Maria, Piedmont, IT",
    ]
    assert result["results"][0]["header_label"] == "Santa Maria, BR"
    assert result["truncated"] is True


def test_rn_005_empty_search_result(load_json):
    """Sem resultados, `results` é uma lista vazia e não há dica de corte (seção 6.3)."""
    raw = [GeoResult.model_validate(item) for item in load_json("geo_direct_empty.json")]

    assert build_search_result(raw).model_dump() == {"results": [], "truncated": False}


@pytest.mark.parametrize(("count", "truncated"), [(1, False), (4, False), (5, True)])
def test_rn_005_truncated_only_with_exactly_five(count, truncated):
    """Seção 6.3: `truncated` é `true` quando o provedor devolve exatamente 5 cidades."""
    raw = [geo(f"Cidade {i}") for i in range(count)]

    result = build_search_result(raw)

    assert len(result.results) == count
    assert result.truncated is truncated


def test_rn_005_never_more_than_five_results():
    """Seção 6.3: a lista tem no máximo 5 itens, mesmo que cheguem mais."""
    raw = [geo(f"Cidade {i}") for i in range(7)]

    result = build_search_result(raw)

    assert [item.marker_label for item in result.results] == [f"Cidade {i}" for i in range(5)]
    assert result.truncated is True


def test_rn_005_city_without_coordinates_is_dropped():
    """D-13: uma cidade sem `lat` ou `lon` não pode ser selecionada e sai da lista."""
    raw = [geo("Sem lat", lat=None), geo("Boa"), GeoResult(name="Sem lon", lat=1.0)]

    result = build_search_result(raw)

    assert [item.marker_label for item in result.results] == ["Boa"]
