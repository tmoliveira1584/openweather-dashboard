"""Testes dos modelos de saída: contrato do backend com o frontend (seção 6.3)."""

import pytest
from pydantic import ValidationError

from app.schemas.view import CitySearchResult, ReverseResult, WeatherView

UBERLANDIA = {
    "lat": -18.9186,
    "lon": -48.2772,
    "list_label": "Uberlândia, Minas Gerais, BR",
    "header_label": "Uberlândia, BR",
    "marker_label": "Uberlândia",
}


def test_p_013_weather_view_matches_architecture_example(load_json):
    """O exemplo da seção 6.3 é lido e devolvido igual, com as chaves em `snake_case`."""
    example = load_json("weather_view_example.json")

    assert WeatherView.model_validate(example).model_dump() == example


def test_p_013_weather_view_accepts_missing_blocks_and_values(load_json):
    """Bloco ausente = `null`; número ausente = `null`; texto ausente = "—" (P-013)."""
    example = load_json("weather_view_example.json")
    example.update(daily=None, hourly=None, minutely=None, timezone_offset=None)
    example["current"].update(dt=None, icon=None, alerts_label=None)
    example["minutely"] = [
        {"dt": 1, "time_label": "08:18", "intensity": None, "band": None, "tooltip": "08:18 — —"}
    ]

    view = WeatherView.model_validate(example)

    assert view.model_dump() == example


@pytest.mark.parametrize(
    ("path", "value"),
    [(("current", "condition_group"), "fog"), (("minutely", 0, "band"), "strong")],
)
def test_p_013_weather_view_rejects_values_outside_the_contract(load_json, path, value):
    """Os `Literal` do contrato recusam valores fora da lista (seção 6.6)."""
    example = load_json("weather_view_example.json")
    target = example
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value

    with pytest.raises(ValidationError):
        WeatherView.model_validate(example)


def test_p_013_city_search_and_reverse_results_match_architecture_example():
    """`CitySearchResult` e `ReverseResult` seguem o formato da seção 6.3."""
    search = {"results": [UBERLANDIA], "truncated": False}

    assert CitySearchResult.model_validate(search).model_dump() == search
    assert ReverseResult(result=None).model_dump() == {"result": None}
    assert ReverseResult.model_validate({"result": UBERLANDIA}).model_dump() == {
        "result": UBERLANDIA
    }
