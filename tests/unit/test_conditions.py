"""Testes do grupo de condição e do vento (RN-017, RN-019)."""

import pytest

from app.domain.conditions import condition_group, wind_direction, wind_label
from app.domain.formatting import MISSING


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        (200, "thunderstorm"),
        (299, "thunderstorm"),
        (300, "rain"),
        (399, "rain"),
        (500, "rain"),
        (599, "rain"),
        (600, "snow"),
        (699, "snow"),
        (700, "mist"),
        (799, "mist"),
        (800, "clear"),
        (801, "clouds"),
        (804, "clouds"),
    ],
)
def test_rn_017_condition_code_ranges_map_to_groups(code, expected):
    """RN-017: cada faixa de código de condição leva ao seu grupo."""
    assert condition_group(code) == expected


def test_ca_015_code_501_is_rain_group():
    """CA-015, RN-017: o código 501 usa a imagem do grupo Chuva."""
    assert condition_group(501) == "rain"


@pytest.mark.parametrize("code", [None, 0, 199, 400, 499, 805, 900])
def test_rn_017_code_outside_ranges_is_neutral(code):
    """RN-017: código fora das faixas, ou ausente, usa a imagem neutra."""
    assert condition_group(code) == "neutral"


@pytest.mark.parametrize(
    ("deg", "expected"),
    [
        (0, "N"),
        (360, "N"),
        (22.49, "N"),
        (22.5, "NE"),
        (67.49, "NE"),
        (67.5, "L"),
        (95, "L"),
        (112.5, "SE"),
        (157.5, "S"),
        (202.5, "SO"),
        (247.5, "O"),
        (292.5, "NO"),
        (337.49, "NO"),
        (337.5, "N"),
        (359.9, "N"),
    ],
)
def test_rn_019_wind_direction_uses_8_point_rose_with_inclusive_lower_limit(deg, expected):
    """RN-019: setores de 45°, com o limite inferior incluído; 0° e 360° são "N"."""
    assert wind_direction(deg) == expected


@pytest.mark.parametrize("deg", [None, float("nan")])
def test_rn_019_missing_wind_direction_is_none(deg):
    """RN-019: sem direção válida, não há ponto cardeal."""
    assert wind_direction(deg) is None


def test_ca_012_wind_shows_speed_and_cardinal():
    """CA-012, RN-019: 4,2 m/s vindo de 95° mostra "4 m/s L" (e "9 mph L" em °F)."""
    label = wind_label(4.2, 95)

    assert label.c == "4 m/s L"
    assert label.f == "9 mph L"


def test_rn_019_mph_is_converted_from_original_speed():
    """RN-019, RN-054: a velocidade em mph parte do valor original em m/s, não do arredondado."""
    # 1,4 m/s arredonda para 1 m/s, mas 1,4 × 2,23694 = 3,13 mph → "3 mph", e não 1 × 2,24 → "2".
    assert wind_label(1.4, 0).f == "3 mph N"


@pytest.mark.parametrize("speed", [0, 0.2, 0.49])
def test_rn_019_speed_below_half_ms_is_calm_in_both_scales(speed):
    """RN-019, RF-022: abaixo de 0,5 m/s originais, "Calmo" nas duas escalas, sem direção."""
    label = wind_label(speed, 95)

    assert label.c == "Calmo"
    assert label.f == "Calmo"


def test_rn_019_half_ms_is_not_calm():
    """RN-019: 0,5 m/s já não é calmo; a velocidade arredondada aparece."""
    label = wind_label(0.5, 180)

    assert label.c == "1 m/s S"
    assert label.f == "1 mph S"


def test_rn_019_missing_direction_shows_only_speed():
    """RN-019: sem direção, só a velocidade aparece, como "4 m/s"."""
    label = wind_label(4.2, None)

    assert label.c == "4 m/s"
    assert label.f == "9 mph"


@pytest.mark.parametrize("speed", [None, float("nan")])
def test_rn_019_missing_speed_shows_dash(speed):
    """RN-019, P-013: sem velocidade, o vento mostra "—" nas duas escalas."""
    label = wind_label(speed, 95)

    assert label.c == MISSING
    assert label.f == MISSING
