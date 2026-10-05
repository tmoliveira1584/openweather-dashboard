"""Testes da conversão de unidades (RN-053 a RN-055, P-014)."""

import pytest

from app.domain.formatting import format_temp
from app.domain.units import celsius_to_fahrenheit, ms_to_mph


@pytest.mark.parametrize(
    ("celsius", "fahrenheit"), [(0, 32), (100, 212), (-40, -40), (20.4, 68.72)]
)
def test_rn_053_celsius_to_fahrenheit(celsius, fahrenheit):
    """RN-053: °F = °C × 9/5 + 32."""
    assert celsius_to_fahrenheit(celsius) == pytest.approx(fahrenheit)


@pytest.mark.parametrize(("ms", "mph"), [(0, 0), (1, 2.23694), (4.12, 9.2161928)])
def test_rn_054_meters_per_second_to_mph(ms, mph):
    """RN-054: mph = m/s × 2,23694."""
    assert ms_to_mph(ms) == pytest.approx(mph)


def test_rn_055_converts_from_original_value():
    """RN-055, P-014, CA-039: 20,4 °C → 68,72 °F → "69°", e não 20 °C → 68 °F → "68°"."""
    assert format_temp(20.4, "c") == "20°"
    assert format_temp(20.4, "f") == "69°"


def test_rn_055_alternating_scale_has_no_accumulated_error():
    """RN-055, P-014, CA-042 e caso de borda (7): 10 alternâncias e a volta a °C mostram "20°"."""
    scale = "c"
    for _ in range(10):
        scale = "f" if scale == "c" else "c"
        assert format_temp(20.4, scale) == {"c": "20°", "f": "69°"}[scale]

    assert scale == "c"
    assert format_temp(20.4, scale) == "20°"


@pytest.mark.parametrize(
    ("celsius", "expected"), [(-40, "-40°"), (-17.8, "0°"), (-17.7, "0°"), (-18.1, "-1°")]
)
def test_rn_055_fahrenheit_near_zero_never_shows_minus_zero(celsius, expected):
    """RN-055, RN-025 e caso de borda (6): -17,8 °C = -0,04 °F mostra "0°", nunca "-0°"."""
    assert format_temp(celsius, "f") == expected
