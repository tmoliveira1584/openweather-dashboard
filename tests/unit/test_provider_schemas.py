"""Testes dos modelos de entrada do provedor (seção 6.2, cenários de categoria 5 do spec).

Campo ausente ou fora do formato vira `None` e nunca causa erro de validação (P-013).
"""

import pytest

from app.clients.openweather import merge_onecall
from app.schemas.provider import Alert, GeoResult, OneCallBundle


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


def test_p_013_bundle_reads_real_capture(uberlandia_bundle):
    """O pacote real é lido com os campos usados pelo view model (seção 6.2)."""
    bundle = OneCallBundle.model_validate(uberlandia_bundle)

    assert bundle.timezone_offset == -10800
    assert bundle.current.temp == 20.54
    assert bundle.current.weather[0].description == "chuva leve"
    assert len(bundle.current.alerts) == 3
    assert len(bundle.minutely) == 60
    assert len(bundle.hourly) == 40
    assert bundle.hourly[0].rain.one_hour == 0.66
    assert bundle.daily[0].temp.max == 22.2
    assert bundle.daily[0].feels_like.day == 20.31
    assert bundle.daily[0].visibility is None
    assert [(alert.id, alert.start, alert.end) for alert in bundle.alerts] == [
        (raw["id"], raw["start"], raw["end"]) for raw in uberlandia_bundle["alerts"]
    ]


@pytest.mark.parametrize("name", ["onecall_no_minutely.json", "onecall_partial.json"])
def test_p_013_bundle_accepts_missing_blocks_and_fields(load_json, name):
    """Blocos e campos ausentes viram `None` (RF-023, RF-038, RF-045)."""
    bundle = OneCallBundle.model_validate(load_json(name))

    assert bundle.current is not None
    if name == "onecall_partial.json":
        assert bundle.hourly is None and bundle.daily is None
        assert bundle.current.visibility is None
        assert bundle.current.feels_like is None
    else:
        assert bundle.minutely is None


def test_p_013_empty_bundle_is_valid():
    """Um pacote vazio é válido: tudo fica `None`."""
    bundle = OneCallBundle.model_validate({})

    assert bundle.model_dump() == {
        "timezone_offset": None,
        "current": None,
        "minutely": None,
        "hourly": None,
        "daily": None,
        "alerts": None,
    }


@pytest.mark.parametrize("bad", ["20", True, float("nan"), float("inf"), [20], {"v": 20}])
def test_p_013_number_out_of_format_becomes_none(bad):
    """Número fora do formato (texto, booleano, NaN, infinito, lista) vira `None`."""
    bundle = OneCallBundle.model_validate(
        {"timezone_offset": bad, "current": {"dt": bad, "temp": bad, "humidity": 94}}
    )

    assert bundle.timezone_offset is None
    assert bundle.current.dt is None
    assert bundle.current.temp is None
    assert bundle.current.humidity == 94


def test_p_013_integer_accepted_where_decimal_is_expected():
    """Um inteiro onde se espera número com casas (ex.: pressão 1017) continua válido."""
    bundle = OneCallBundle.model_validate({"current": {"pressure": 1017, "wind_speed": 4}})

    assert bundle.current.pressure == 1017
    assert bundle.current.wind_speed == 4


def test_p_013_text_out_of_format_becomes_none():
    """Texto fora do formato vira `None` (ex.: descrição numérica)."""
    bundle = OneCallBundle.model_validate(
        {"current": {"weather": [{"id": "500", "description": 5, "icon": None}]}}
    )

    weather = bundle.current.weather[0]
    assert (weather.id, weather.description, weather.icon) == (None, None, None)


def test_p_013_nested_object_out_of_format_becomes_none():
    """Objeto aninhado fora do formato vira `None` sem derrubar o restante do registro."""
    bundle = OneCallBundle.model_validate(
        {
            "current": "x",
            "hourly": [{"dt": 1, "rain": 0.5, "weather": "chuva", "temp": 20}],
            "daily": [{"dt": 1, "temp": 30, "feels_like": [1]}],
        }
    )

    assert bundle.current is None
    assert bundle.hourly[0].rain is None
    assert bundle.hourly[0].weather is None
    assert bundle.hourly[0].temp == 20
    assert bundle.daily[0].temp is None
    assert bundle.daily[0].feels_like is None


def test_p_013_bad_list_item_becomes_none_and_keeps_the_others():
    """Um item inválido numa lista vira `None`; os demais itens são mantidos."""
    bundle = OneCallBundle.model_validate(
        {"minutely": [{"dt": 1, "precipitation": 0.3}, "x", 7], "current": {"alerts": ["a", 3]}}
    )

    assert bundle.minutely[0].precipitation == 0.3
    assert bundle.minutely[1:] == [None, None]
    assert bundle.current.alerts == ["a", None]


@pytest.mark.parametrize("bad", ["x", 5, {"a": 1}])
def test_p_013_list_out_of_format_becomes_none(bad):
    """Uma lista que chega em outro formato vira `None`, como um bloco ausente."""
    bundle = OneCallBundle.model_validate({"hourly": bad, "alerts": bad})

    assert bundle.hourly is None
    assert bundle.alerts is None


def test_p_013_alert_without_validity():
    """Alerta sem detalhe (404) só tem `id`; a vigência fica `None` (ADR-013)."""
    alert = Alert.model_validate({"id": "urn:oid:x", "start": "amanhã"})

    assert (alert.id, alert.start, alert.end) == ("urn:oid:x", None, None)


def test_p_013_geo_result_reads_capture_and_tolerates_bad_fields(load_json):
    """Geocodificação: lê a captura real e troca campos fora do formato por `None`."""
    real = GeoResult.model_validate(load_json("geo_reverse_uberlandia.json")[0])
    bad = GeoResult.model_validate({"name": "X", "lat": "-18", "local_names": {"pt": 1}})

    assert real.local_names["pt"] == "Uberlândia"
    assert isinstance(real.lat, float)
    assert bad.lat is None
    assert bad.local_names == {"pt": None}
