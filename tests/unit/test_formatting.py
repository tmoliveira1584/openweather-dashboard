"""Testes da formatação de números e indicadores (RN-014, RN-020 a RN-025)."""

import pytest

from app.domain.formatting import (
    MISSING,
    format_humidity,
    format_number,
    format_pressure,
    format_temp,
    format_uvi,
    format_visibility,
)


@pytest.mark.parametrize(
    ("value", "decimals", "expected"),
    [
        (20.4, 0, "20"),
        (2.5, 1, "2,5"),
        (0.21, 2, "0,21"),
        (0.3, 2, "0,30"),
        (1015, 0, "1015"),
        (12345.6, 1, "12345,6"),
        (-3.4, 0, "-3"),
    ],
)
def test_rn_025_decimal_comma_without_thousands_separator(value, decimals, expected):
    """RN-025: vírgula decimal, sem separador de milhar e "-" para negativos."""
    assert format_number(value, decimals) == expected


@pytest.mark.parametrize(
    ("value", "decimals", "expected"),
    [(-0.3, 0, "0"), (-0.04, 0, "0"), (-0.0, 0, "0"), (-0.004, 2, "0,00"), (-0.04, 1, "0,0")],
)
def test_rn_025_value_rounding_to_zero_never_shows_minus_zero(value, decimals, expected):
    """RN-025: um valor que arredonda para zero nunca aparece como "-0" e mantém as casas."""
    assert format_number(value, decimals) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [(20.5, "21"), (-20.5, "-21"), (0.5, "1"), (2.675, "3"), (20.49, "20")],
)
def test_rn_014_rounds_half_away_from_zero(value, expected):
    """RN-014, RN-025: o empate em 0,5 arredonda para longe do zero, não para o par."""
    assert format_number(value) == expected


def test_rn_025_rounds_by_decimal_text_not_binary_float():
    """RN-025: 2,675 com 2 casas vira "2,68", apesar de o float ser 2,67499…"""
    assert format_number(2.675, 2) == "2,68"


@pytest.mark.parametrize(
    ("celsius", "scale", "expected"),
    [(20.4, "c", "20°"), (20.54, "c", "21°"), (-3.4, "c", "-3°"), (-0.3, "c", "0°")],
)
def test_rn_014_temperature_rounded_with_degree_sign(celsius, scale, expected):
    """RN-014, RN-025 e caso de borda (6): inteiro mais próximo com "°", nunca "-0°"."""
    assert format_temp(celsius, scale) == expected


def test_ca_009_main_card_temperatures():
    """RN-014, CA-009: 20,4 °C mostra "20°" e a sensação de 20,6 °C mostra "21°"."""
    assert format_temp(20.4, "c") == "20°"
    assert format_temp(20.6, "c") == "21°"


@pytest.mark.parametrize(
    ("celsius", "scale", "expected"),
    [(19.54, "c", "20 °C"), (19.4, "c", "19 °C"), (19.4, "f", "67 °F")],
)
def test_rn_024_dew_point_with_full_scale(celsius, scale, expected):
    """RN-014, RN-024: ponto de orvalho inteiro, com a escala ativa por extenso."""
    assert format_temp(celsius, scale, with_unit=True) == expected


@pytest.mark.parametrize("with_unit", [False, True])
def test_rn_014_missing_temperature_shows_dash(with_unit):
    """RN-014, P-013: temperatura ausente mostra "—"."""
    assert format_temp(None, "c", with_unit=with_unit) == MISSING


@pytest.mark.parametrize(("value", "expected"), [(94, "94%"), (40, "40%"), (None, "—")])
def test_rn_020_humidity_as_integer_percent(value, expected):
    """RN-020: umidade em percentual inteiro."""
    assert format_humidity(value) == expected


@pytest.mark.parametrize(
    ("meters", "expected"),
    [
        (10000, "10 km"),
        (2500, "2,5 km"),
        (9950, "10 km"),
        (9940, "9,9 km"),
        (800, "0,8 km"),
        (0, "0 km"),
        (None, "—"),
    ],
)
def test_rn_021_visibility_in_km_with_up_to_one_decimal(meters, expected):
    """RN-021: metros ÷ 1.000, até 1 casa decimal e nenhuma quando o valor é inteiro."""
    assert format_visibility(meters) == expected


@pytest.mark.parametrize(("value", "expected"), [(1015, "1015 hPa"), (None, "—")])
def test_rn_022_pressure_in_hpa(value, expected):
    """RN-022: pressão em hPa, inteiro."""
    assert format_pressure(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"), [(2.4, "2 UV"), (0.12, "0 UV"), (9.5, "10 UV"), (None, "—")]
)
def test_rn_023_uv_index_rounded(value, expected):
    """RN-023: índice UV arredondado ao inteiro."""
    assert format_uvi(value) == expected
