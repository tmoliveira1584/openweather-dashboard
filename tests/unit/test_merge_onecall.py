"""Testes do pacote da One Call 4.0 montado por `merge_onecall` (seção 6.2, ADR-013).

Usam as capturas reais de Uberlândia e de Tóquio (T-0.8).
"""

import json

import pytest

from app.clients.openweather import merge_onecall

ENDPOINTS = ("current", "1min", "1h_p1", "1h_p2", "1day")


@pytest.fixture
def captures(load_json):
    """Respostas reais de uma cidade, por endpoint, e os detalhes dos alertas de Uberlândia."""

    def load(city: str) -> dict:
        data = {name: load_json(f"onecall4/{city}/{name}.json") for name in ENDPOINTS}
        if city == "uberlandia":
            data["alerts"] = [load_json(f"onecall4/uberlandia/alert_{i}.json") for i in (1, 2, 3)]
        else:
            data["alerts"] = []
        return data

    return load


def merge(c: dict, **overrides) -> dict:
    args = {
        "current": c["current"],
        "minutely": c["1min"],
        "hourly_pages": [c["1h_p1"], c["1h_p2"]],
        "daily": c["1day"],
        "alerts": c["alerts"],
    }
    args.update(overrides)
    return merge_onecall(**args)


@pytest.mark.parametrize("city", ["uberlandia", "tokyo"])
def test_adr_013_merge_builds_bundle_from_real_captures(captures, city):
    """ADR-013: o pacote tem o fuso de `current`, o registro atual e as três previsões."""
    c = captures(city)

    bundle = merge(c)

    assert bundle["timezone_offset"] == c["current"]["timezone_offset"]
    assert bundle["current"] == c["current"]["data"][0]
    assert bundle["minutely"] == c["1min"]["data"]
    assert bundle["daily"] == c["1day"]["data"]
    assert len(bundle["hourly"]) == 40


def test_adr_013_merge_joins_hourly_pages_without_repeating_dt(captures):
    """ADR-013: as 2 páginas por hora viram uma lista em ordem, sem `dt` repetido."""
    c = captures("uberlandia")
    first, second = c["1h_p1"], c["1h_p2"]
    overlapping = {**second, "data": first["data"][-2:] + second["data"]}

    bundle = merge(c, hourly_pages=[first, overlapping])

    dts = [item["dt"] for item in bundle["hourly"]]
    assert dts == sorted(set(dts))
    assert len(dts) == 40


def test_adr_013_merge_drops_pagination_links(captures):
    """ADR-013, guardrail 13: os links `next`/`prev`, que trazem a chave, não entram no pacote."""
    c = captures("uberlandia")
    link = "https://api.openweathermap.org/data/4.0/onecall/timeline/1h?appid=segredo"
    with_links = {name: {**c[name], "next": link, "prev": link} for name in ENDPOINTS}
    with_links["alerts"] = c["alerts"]

    bundle = merge(with_links)

    assert "segredo" not in json.dumps(bundle)
    assert "next" not in bundle and "prev" not in bundle


@pytest.mark.parametrize(
    ("key", "override"),
    [
        ("minutely", {"minutely": None}),
        ("hourly", {"hourly_pages": [None, None]}),
        ("daily", {"daily": None}),
    ],
)
def test_adr_013_merge_leaves_block_out_on_404(captures, key, override):
    """ADR-013: um 404 numa previsão (`None`) deixa o bloco ausente do pacote."""
    bundle = merge(captures("uberlandia"), **override)

    assert key not in bundle


@pytest.mark.parametrize(
    ("key", "endpoint"), [("minutely", "1min"), ("daily", "1day"), ("hourly", "1h_p1")]
)
def test_adr_013_merge_leaves_block_out_when_data_is_empty(captures, key, endpoint):
    """ADR-013: `data` vazia é tratada como falta de cobertura, igual ao 404."""
    c = captures("uberlandia")
    empty = {**c[endpoint], "data": []}
    overrides = {
        "minutely": {"minutely": empty},
        "daily": {"daily": empty},
        "hourly": {"hourly_pages": [empty, empty]},
    }[key]

    bundle = merge(c, **overrides)

    assert key not in bundle


def test_adr_013_merge_keeps_hourly_when_only_one_page_answers(captures):
    """ADR-013: com uma página por hora sem dados, o pacote fica com as horas da outra."""
    c = captures("uberlandia")

    bundle = merge(c, hourly_pages=[c["1h_p1"], None])

    assert bundle["hourly"] == c["1h_p1"]["data"]


def test_adr_013_merge_keeps_only_id_and_validity_of_each_alert(captures):
    """ADR-013: do detalhe do alerta, o pacote guarda só `id`, `start` e `end`."""
    c = captures("uberlandia")

    bundle = merge(c)

    assert bundle["alerts"] == [
        {"id": a["id"], "start": a["start"], "end": a["end"]} for a in c["alerts"]
    ]


def test_adr_013_merge_keeps_alert_without_detail_with_id_only(captures):
    """ADR-013: um alerta cujo detalhe respondeu 404 entra só com o `id`, sem vigência."""
    c = captures("uberlandia")

    bundle = merge(c, alerts=[{"id": "urn:oid:sem-detalhe"}])

    assert bundle["alerts"] == [{"id": "urn:oid:sem-detalhe"}]


@pytest.mark.parametrize("alerts", [[], None])
def test_adr_013_merge_leaves_alerts_out_without_ids(captures, alerts):
    """Seção 6.2: sem alertas, o campo `alerts` fica ausente do pacote."""
    bundle = merge(captures("tokyo"), alerts=alerts)

    assert "alerts" not in bundle


def test_adr_013_merge_leaves_current_out_when_data_is_empty(captures):
    """Seção 6.2: `current` sem registros fica ausente; o fuso continua vindo dele."""
    c = captures("uberlandia")

    bundle = merge(c, current={**c["current"], "data": []})

    assert "current" not in bundle
    assert bundle["timezone_offset"] == -10800
