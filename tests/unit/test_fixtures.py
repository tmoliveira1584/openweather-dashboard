"""Guarda das fixtures reais: formato esperado e nenhuma chave gravada (P-001, ADR-013)."""

from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"

CITIES = ["uberlandia", "tokyo"]
ONECALL4_ENDPOINTS = ["current", "1min", "1h_p1", "1h_p2", "1day"]


@pytest.mark.parametrize("endpoint", ONECALL4_ENDPOINTS)
@pytest.mark.parametrize("city", CITIES)
def test_setup_onecall4_fixtures_have_expected_shape(load_json, city, endpoint):
    """As capturas da One Call 4.0 têm o fuso e a lista data, sem os links de paginação."""
    data = load_json(f"onecall4/{city}/{endpoint}.json")

    assert {"timezone_offset", "data"} <= data.keys()
    assert "next" not in data
    assert "prev" not in data


def test_setup_geo_fixtures_have_expected_shape(load_json):
    """As capturas de geocodificação são listas, com 0, 1 ou vários resultados."""
    assert len(load_json("geo_direct_santa_maria.json")) > 1
    assert load_json("geo_direct_empty.json") == []
    assert len(load_json("geo_reverse_uberlandia.json")) == 1


def test_p_001_fixtures_never_contain_appid():
    """P-001: nenhuma fixture guarda o parâmetro da chave."""
    files = sorted(FIXTURES_DIR.rglob("*.json"))

    assert files
    for path in files:
        assert "appid" not in path.read_text(encoding="utf-8").lower(), path.name


@pytest.mark.parametrize(
    ("name", "absent"),
    [
        ("onecall_no_minutely.json", {"minutely"}),
        ("onecall_partial.json", {"hourly", "daily"}),
        ("onecall_alerts.json", set()),
        ("onecall_minutely_bands.json", set()),
    ],
)
def test_setup_variant_bundles_have_expected_shape(load_json, name, absent):
    """Os pacotes variantes têm o formato da seção 6.2, sem os blocos retirados de propósito."""
    bundle = load_json(name)
    blocks = {"timezone_offset", "current", "minutely", "hourly", "daily", "alerts"}

    assert bundle.keys() == blocks - absent
