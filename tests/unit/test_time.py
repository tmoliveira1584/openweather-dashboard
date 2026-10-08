"""Testes da hora local e dos rótulos de hora, dia e data (RN-015, RN-028, RN-030, RN-035).

Os horários vêm das capturas reais de 2026-10-05: o mesmo instante é 16:41 de segunda em
Uberlândia (UTC-3) e 04:41 de terça em Tóquio (UTC+9).
"""

from datetime import UTC

import pytest

from app.domain.time import (
    date_label,
    hour_label,
    local_date,
    local_datetime,
    time_label,
    weekday_label,
)

CAPTURE_DT = 1791229263  # 2026-10-05 19:41:03 UTC
UBERLANDIA = -10800
TOKYO = 32400


def test_rn_015_local_datetime_is_utc_plus_city_offset():
    """RN-015, P-015: hora local = UTC da medição + fuso da cidade, sem o fuso da máquina."""
    moment = local_datetime(CAPTURE_DT, UBERLANDIA)

    assert (moment.hour, moment.minute, moment.second) == (16, 41, 3)
    assert moment.tzinfo is UTC


@pytest.mark.parametrize(("offset", "expected"), [(UBERLANDIA, "16:41"), (TOKYO, "04:41")])
def test_rn_015_time_label_in_city_timezone(load_json, offset, expected):
    """RN-015 e caso de borda (8): HH:MM em 24 horas no fuso de cada cidade."""
    city = "uberlandia" if offset == UBERLANDIA else "tokyo"
    current = load_json(f"onecall4/{city}/current.json")

    assert current["timezone_offset"] == offset
    assert time_label(current["data"][0]["dt"], current["timezone_offset"]) == expected


def test_rn_015_time_label_pads_with_zeros():
    """RN-015: "08:18", com zero à esquerda."""
    assert time_label(1791112680, UBERLANDIA) == "08:18"


@pytest.mark.parametrize(("offset", "expected"), [(UBERLANDIA, "16:00"), (TOKYO, "04:00")])
def test_rn_035_hour_label(offset, expected):
    """RN-035: a hora aparece como "HH:00" no fuso da cidade."""
    assert hour_label(CAPTURE_DT - 41 * 60 - 3, offset) == expected


def test_rn_035_midnight_of_new_day_has_weekday():
    """RN-035: a primeira hora do novo dia em Uberlândia é "00:00" de terça; uma hora antes,
    ainda é segunda no fuso da cidade, embora já seja terça em UTC."""
    midnight = 1791255600  # 2026-10-06 03:00 UTC

    assert hour_label(midnight, UBERLANDIA) == "00:00"
    assert weekday_label(midnight, UBERLANDIA) == "Ter"
    assert hour_label(midnight - 3600, UBERLANDIA) == "23:00"
    assert weekday_label(midnight - 3600, UBERLANDIA) == "Seg"


@pytest.mark.parametrize(
    ("day", "expected"),
    [(4, "Dom"), (5, "Seg"), (6, "Ter"), (7, "Qua"), (8, "Qui"), (9, "Sex"), (10, "Sáb")],
)
def test_rn_028_weekday_abbreviations_in_portuguese(day, expected):
    """RN-028, P-016: dias da semana abreviados em português, de domingo (04/10) a sábado."""
    midnight_utc = 1791072000 + (day - 4) * 86400  # 2026-10-04 00:00 UTC

    assert weekday_label(midnight_utc, 0) == expected


@pytest.mark.parametrize(
    ("offset", "weekday", "date", "iso"),
    [(UBERLANDIA, "Seg", "Seg, 05/10", "2026-10-05"), (TOKYO, "Ter", "Ter, 06/10", "2026-10-06")],
)
def test_rn_030_same_instant_falls_on_city_date(offset, weekday, date, iso):
    """RN-015, RN-028, RN-030: o mesmo instante cai em dias diferentes conforme o fuso."""
    assert weekday_label(CAPTURE_DT, offset) == weekday
    assert date_label(CAPTURE_DT, offset) == date
    assert local_date(CAPTURE_DT, offset) == iso


@pytest.mark.parametrize("city", ["uberlandia", "tokyo"])
def test_rn_030_daily_date_uses_utc_date_of_dt(load_json, city):
    """RN-030, ADR-013: o dia da 4.0 vem às 00:00 UTC da sua data, lida com offset 0."""
    first_day = load_json(f"onecall4/{city}/1day.json")["data"][0]["dt"]

    assert local_date(first_day, 0) == "2026-10-05"
    assert date_label(first_day, 0) == "Seg, 05/10"


def test_rn_030_date_label_pads_day_and_month():
    """RN-030: dia e mês com dois dígitos, como em "Seg, 05/10"."""
    assert date_label(1767225600, 0) == "Qui, 01/01"  # 2026-01-01 00:00 UTC
