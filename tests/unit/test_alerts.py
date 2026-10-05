"""Testes do selo de alertas e da contagem de alertas por dia (RN-018, RN-032).

As vigências reais vêm da captura de Uberlândia de 2026-10-05 (segunda-feira): dois alertas
terminam às 23:59 de segunda e o terceiro vai das 00:00 às 23:59 de terça, no fuso da cidade.
"""

from datetime import UTC, datetime

import pytest

from app.domain.alerts import alerts_label, count_alert_ids, count_alerts_on_day
from app.schemas.provider import Alert

UBERLANDIA = -10800
TOKYO = 32400


def local_ts(local: str, offset: int) -> int:
    """Instante UTC de uma data e hora locais da cidade, como "2026-10-07T18:00"."""
    return int(datetime.fromisoformat(local).replace(tzinfo=UTC).timestamp()) - offset


@pytest.fixture
def uberlandia_alerts(load_json):
    return [Alert(**load_json(f"onecall4/uberlandia/alert_{i}.json")) for i in (1, 2, 3)]


@pytest.mark.parametrize(
    ("count", "expected"),
    [(1, "1 alerta"), (2, "2 alertas"), (3, "3 alertas"), (99, "99 alertas")],
)
def test_rn_018_alerts_label_singular_and_plural(count, expected):
    """RN-018: "1 alerta" ou "N alertas"."""
    assert alerts_label(count) == expected


@pytest.mark.parametrize("count", [100, 250])
def test_rn_018_more_than_99_alerts_shows_99_plus(count):
    """RN-018: acima de 99, o selo mostra "99+ alertas"."""
    assert alerts_label(count) == "99+ alertas"


def test_rn_018_no_alerts_hides_the_badge():
    """RN-018, RF-019: sem alertas, não há selo."""
    assert alerts_label(0) is None


def test_rn_018_counts_distinct_ids_including_future_alerts(load_json):
    """RN-018: os 3 IDs de `current.alerts` contam, inclusive o que só começa amanhã."""
    current = load_json("onecall4/uberlandia/current.json")["data"][0]

    assert count_alert_ids(current["alerts"]) == 3


@pytest.mark.parametrize(
    ("ids", "expected"),
    [(["a", "a", "b"], 2), (["", "a", "  "], 1), ([], 0), (None, 0)],
)
def test_rn_018_counts_distinct_non_empty_ids_and_missing_list_is_zero(ids, expected):
    """RN-018: IDs repetidos contam uma vez, vazios não contam e lista ausente = 0."""
    assert count_alert_ids(ids) == expected


def test_ca_021_alert_counts_only_on_days_it_reaches():
    """CA-021, RN-032: alerta de quarta 18:00 a quinta 06:00 conta em "Qua" e não em "Sex"."""
    alert = Alert(
        id="a",
        start=local_ts("2026-10-07T18:00", UBERLANDIA),
        end=local_ts("2026-10-08T06:00", UBERLANDIA),
    )

    assert count_alerts_on_day([alert], "2026-10-07", UBERLANDIA) == 1  # Qua
    assert count_alerts_on_day([alert], "2026-10-08", UBERLANDIA) == 1  # Qui
    assert count_alerts_on_day([alert], "2026-10-09", UBERLANDIA) == 0  # Sex
    assert alerts_label(count_alerts_on_day([alert], "2026-10-09", UBERLANDIA)) is None


def test_rn_032_real_alerts_are_counted_by_validity(uberlandia_alerts):
    """RN-032: com as vigências reais, 2 alertas na segunda, 1 na terça e nenhum na quarta."""
    assert count_alerts_on_day(uberlandia_alerts, "2026-10-05", UBERLANDIA) == 2
    assert count_alerts_on_day(uberlandia_alerts, "2026-10-06", UBERLANDIA) == 1
    assert count_alerts_on_day(uberlandia_alerts, "2026-10-07", UBERLANDIA) == 0


def test_rn_032_alert_ending_at_midnight_counts_only_on_previous_day():
    """RN-032: fim às 00:00 não se sobrepõe ao dia seguinte por um tempo maior que zero."""
    alert = Alert(
        id="a",
        start=local_ts("2026-10-07T18:00", UBERLANDIA),
        end=local_ts("2026-10-08T00:00", UBERLANDIA),
    )

    assert count_alerts_on_day([alert], "2026-10-07", UBERLANDIA) == 1
    assert count_alerts_on_day([alert], "2026-10-08", UBERLANDIA) == 0


def test_rn_032_alert_starting_at_midnight_does_not_count_on_previous_day():
    """RN-032: início às 00:00 conta só a partir desse dia."""
    alert = Alert(
        id="a",
        start=local_ts("2026-10-08T00:00", UBERLANDIA),
        end=local_ts("2026-10-08T06:00", UBERLANDIA),
    )

    assert count_alerts_on_day([alert], "2026-10-07", UBERLANDIA) == 0
    assert count_alerts_on_day([alert], "2026-10-08", UBERLANDIA) == 1


def test_rn_032_zero_length_alert_does_not_reach_any_day():
    """RN-032: sem sobreposição maior que zero, o alerta não conta."""
    moment = local_ts("2026-10-07T12:00", UBERLANDIA)
    alert = Alert(id="a", start=moment, end=moment)

    assert count_alerts_on_day([alert], "2026-10-07", UBERLANDIA) == 0


@pytest.mark.parametrize(
    "alert",
    [
        Alert(id="sem-inicio", end=1791255540),
        Alert(id="sem-fim", start=1791255540),
        Alert(id="sem-vigencia"),
    ],
)
def test_rn_032_alert_without_start_or_end_counts_on_every_day(alert):
    """RN-032, ADR-013: alerta sem início ou sem fim (ex.: detalhe com 404) conta em todos os dias."""
    for day in ("2026-10-01", "2026-10-05", "2026-10-12"):
        assert count_alerts_on_day([alert], day, UBERLANDIA) == 1


def test_rn_032_day_period_uses_city_timezone():
    """RN-032: o dia vai de 00:00 a 24:00 no fuso da cidade, não em UTC nem no da máquina."""
    # 20:00 a 23:00 UTC de 05/10: ainda segunda em Uberlândia, já terça de manhã em Tóquio.
    alert = Alert(id="a", start=1791230400, end=1791241200)

    assert count_alerts_on_day([alert], "2026-10-05", UBERLANDIA) == 1
    assert count_alerts_on_day([alert], "2026-10-06", UBERLANDIA) == 0
    assert count_alerts_on_day([alert], "2026-10-05", TOKYO) == 0
    assert count_alerts_on_day([alert], "2026-10-06", TOKYO) == 1


def test_rn_032_no_alerts_counts_zero():
    """RN-032: sem alertas no pacote, nenhum dia tem selo."""
    assert count_alerts_on_day([], "2026-10-05", UBERLANDIA) == 0
