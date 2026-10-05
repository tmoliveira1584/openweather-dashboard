"""Testes dos rótulos de cidade da busca e da geocodificação reversa (RN-006 a RN-008)."""

import pytest

from app.domain.places import city_option
from app.schemas.provider import GeoResult

TOKYO = GeoResult(
    name="Tokyo",
    local_names={"en": "Tokyo", "pt": "Tóquio"},
    state="Tokyo",
    country="JP",
    lat=35.6828,
    lon=139.759,
)


@pytest.fixture
def santa_maria(load_json):
    """Os 5 resultados reais da busca por "Santa Maria"."""
    return [GeoResult(**item) for item in load_json("geo_direct_santa_maria.json")]


def test_rn_006_uses_portuguese_name_when_available():
    """RN-006: o nome exibido é o nome em português do provedor."""
    option = city_option(TOKYO)

    assert option.header_label == "Tóquio, JP"
    assert option.marker_label == "Tóquio"


def test_rn_006_falls_back_to_default_name_without_portuguese(santa_maria):
    """RN-006: sem nome em português, usa o nome padrão do provedor."""
    assert city_option(santa_maria[2]).marker_label == "Santa-Maria-Siché"


def test_rn_006_empty_portuguese_name_falls_back_to_default_name():
    """RN-006: um nome em português vazio conta como inexistente."""
    raw = GeoResult(name="Santa Maria", local_names={"pt": ""}, country="IT", lat=45, lon=8.3)

    assert city_option(raw).marker_label == "Santa Maria"


def test_rn_007_header_label_is_name_and_country_code(load_json):
    """RN-007: cabeçalho no formato "<nome>, <código do país>", como "Uberlândia, BR"."""
    raw = GeoResult(**load_json("geo_reverse_uberlandia.json")[0])

    assert city_option(raw).header_label == "Uberlândia, BR"


def test_rn_008_list_label_has_name_state_and_country(load_json):
    """RN-008: item da lista no formato "Uberlândia, Minas Gerais, BR"."""
    raw = GeoResult(**load_json("geo_reverse_uberlandia.json")[0])

    assert city_option(raw).list_label == "Uberlândia, Minas Gerais, BR"


def test_rn_008_list_label_without_state_has_name_and_country(santa_maria):
    """RN-008: sem estado, o item fica "<nome>, <país>"."""
    assert city_option(santa_maria[3]).list_label == "Ilha de Santa Maria, PT"


def test_rn_008_homonyms_are_told_apart_by_state_and_country(santa_maria):
    """RN-008: cidades de mesmo nome se distinguem pelo estado e pelo país."""
    labels = [city_option(raw).list_label for raw in santa_maria]

    assert labels == [
        "Santa Maria, Rio Grande do Sul, BR",
        "Santa Maria, California, US",
        "Santa-Maria-Siché, Corsica, FR",
        "Ilha de Santa Maria, PT",
        "Santa Maria, Piedmont, IT",
    ]


def test_city_option_keeps_coordinates(santa_maria):
    """As coordenadas do provedor seguem sem alteração para a consulta de clima."""
    option = city_option(santa_maria[0])

    assert (option.lat, option.lon) == (-29.6860512, -53.8069214)
