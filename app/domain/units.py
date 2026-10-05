"""Conversão de unidades, sempre a partir do valor original do provedor (RN-053 a RN-055, P-014).

Nada aqui arredonda: o arredondamento acontece só na formatação.
"""

MPH_PER_MS = 2.23694


def celsius_to_fahrenheit(c: float) -> float:
    """°F = °C × 9/5 + 32 (RN-053)."""
    return c * 9 / 5 + 32


def ms_to_mph(v: float) -> float:
    """mph = m/s × 2,23694 (RN-054)."""
    return v * MPH_PER_MS
