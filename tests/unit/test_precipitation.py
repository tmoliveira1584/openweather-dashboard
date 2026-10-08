"""Testes da chance de precipitação, do volume de chuva e da intensidade por minuto
(RN-036, RN-037, RN-041, RN-045, RN-047).
"""

import pytest

from app.domain.formatting import MISSING
from app.domain.precipitation import intensity_band, minute_tooltip, pop_label, rain_label

UBERLANDIA = -10800
AT_08_18 = 1791112680  # 08:18 em Uberlândia, o exemplo da seção 6.3 da arquitetura


@pytest.mark.parametrize(
    ("pop", "expected"),
    [(0.21, "21%"), (0, "0%"), (1, "100%"), (0.145, "15%"), (0.005, "1%"), (0.004, "0%")],
)
def test_rn_036_pop_is_fraction_times_100_rounded(pop, expected):
    """RN-036: fração × 100, arredondada ao inteiro, com "%" (0,21 → "21%")."""
    assert pop_label(pop) == expected


def test_rn_036_missing_pop_shows_dash():
    """RN-036, P-013: sem chance de precipitação, o card mostra "—"."""
    assert pop_label(None) == MISSING


@pytest.mark.parametrize(
    ("mm", "expected"),
    [(0.21, "0,21 mm/h"), (1.5, "1,50 mm/h"), (0.005, "0,01 mm/h"), (12.345, "12,35 mm/h")],
)
def test_rn_037_rain_label_has_two_decimals(mm, expected):
    """RN-037: volume de chuva em mm/h com 2 casas decimais."""
    assert rain_label(mm) == expected


@pytest.mark.parametrize("mm", [None, 0, 0.004, -0.2])
def test_rn_037_rain_label_is_none_when_rounded_value_is_not_positive(mm):
    """RN-037: a etiqueta só aparece com valor arredondado maior que zero; ausente = sem chuva."""
    assert rain_label(mm) is None


@pytest.mark.parametrize(
    ("p", "expected"),
    [
        (0, "none"),
        (0.0, "none"),
        (0.01, "light"),
        (0.3, "light"),
        (0.5, "light"),
        (0.51, "moderate"),
        (1.0, "moderate"),
        (2.5, "moderate"),
        (2.51, "heavy"),
        (5.0, "heavy"),
        (7.5, "heavy"),
        (7.51, "extreme"),
        (8.0, "extreme"),
        (12, "extreme"),
    ],
)
def test_rn_041_band_boundaries_are_inclusive_on_upper_limit(p, expected):
    """RN-041: faixas de intensidade com o limite superior incluído na faixa."""
    assert intensity_band(p) == expected


@pytest.mark.parametrize("p", [None, -1, -0.01, "0.3", float("nan"), True])
def test_rn_047_negative_or_non_numeric_intensity_has_no_band(p):
    """RN-047, RN-041: valor ausente, negativo ou não numérico não tem faixa."""
    assert intensity_band(p) is None


@pytest.mark.parametrize(
    ("p", "expected"),
    [(0.3, "08:18 — 0,30 mm/h"), (0, "08:18 — 0,00 mm/h"), (8, "08:18 — 8,00 mm/h")],
)
def test_rn_045_minute_tooltip_shows_local_time_and_intensity(p, expected):
    """RN-045: valor do cursor no formato "HH:MM — X,XX mm/h", na hora local da cidade."""
    assert minute_tooltip(AT_08_18, UBERLANDIA, p) == expected


@pytest.mark.parametrize("p", [None, -1, "abc"])
def test_rn_047_minute_tooltip_shows_dash_for_missing_intensity(p):
    """RN-047, RN-045: com intensidade ausente, negativa ou não numérica, o cursor mostra "—"."""
    assert minute_tooltip(AT_08_18, UBERLANDIA, p) == "08:18 — —"
