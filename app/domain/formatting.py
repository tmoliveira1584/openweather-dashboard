"""Números e indicadores no formato pt-BR do produto (RN-014, RN-020 a RN-025).

O arredondamento usa o texto decimal do valor (`repr`) e não o float binário, para que 2,675
vire "2,68". O empate em 0,5 vai para longe do zero ("20,5" → "21"), e não para o par como
no `round()` do Python.
"""

from decimal import ROUND_HALF_UP, Decimal

from app.domain.units import celsius_to_fahrenheit
from app.schemas.view import Scale

MISSING = "—"  # P-013

_UNIT_NAMES: dict[Scale, str] = {"c": "°C", "f": "°F"}


def _round(value: float | Decimal, decimals: int) -> Decimal:
    exact = value if isinstance(value, Decimal) else Decimal(repr(value))
    rounded = exact.quantize(Decimal(1).scaleb(-decimals), rounding=ROUND_HALF_UP)
    # Sem "-0": um valor que arredonda para zero perde o sinal (RN-025).
    return abs(rounded) if rounded.is_zero() else rounded


def format_number(value: float | Decimal, decimals: int = 0) -> str:
    """Vírgula decimal, sem separador de milhar e nunca "-0" (RN-025)."""
    return f"{_round(value, decimals):f}".replace(".", ",")


def format_temp(celsius: float | None, scale: Scale, with_unit: bool = False) -> str:
    """Temperatura inteira com "°" (RN-014) ou com a escala por extenso, como "19 °C" (RN-024).

    A conversão parte do valor original em °C (RN-055, P-014).
    """
    if celsius is None:
        return MISSING
    value = celsius_to_fahrenheit(celsius) if scale == "f" else celsius
    text = format_number(value)
    return f"{text} {_UNIT_NAMES[scale]}" if with_unit else f"{text}°"


def format_humidity(percent: float | None) -> str:
    """Umidade em percentual inteiro, como "94%" (RN-020)."""
    return MISSING if percent is None else f"{format_number(percent)}%"


def format_visibility(meters: float | None) -> str:
    """Metros ÷ 1.000, com até 1 casa: "10 km" e "2,5 km" (RN-021)."""
    if meters is None:
        return MISSING
    km = _round(Decimal(repr(meters)) / 1000, 1)
    decimals = 0 if km == km.to_integral_value() else 1
    return f"{format_number(km, decimals)} km"


def format_pressure(hpa: float | None) -> str:
    """Pressão em hPa, inteiro, como "1015 hPa" (RN-022)."""
    return MISSING if hpa is None else f"{format_number(hpa)} hPa"


def format_uvi(uvi: float | None) -> str:
    """Índice UV arredondado ao inteiro, como "2 UV" (RN-023)."""
    return MISSING if uvi is None else f"{format_number(uvi)} UV"
