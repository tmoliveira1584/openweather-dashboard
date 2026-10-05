"""Grupo de condição do tempo e vento (RN-017, RN-019)."""

import math

from app.domain.formatting import MISSING, format_number
from app.domain.units import ms_to_mph
from app.schemas.view import ConditionGroup, Scaled

CALM = "Calmo"
CALM_BELOW_MS = 0.5  # velocidade original, em m/s (RN-019)

# Rosa de 8 pontos, a partir do norte, em setores de 45° (RN-019).
CARDINALS = ("N", "NE", "L", "SE", "S", "SO", "O", "NO")

# Faixas de código de condição do provedor, com os dois limites incluídos (RN-017).
_GROUP_RANGES: tuple[tuple[int, int, ConditionGroup], ...] = (
    (200, 299, "thunderstorm"),
    (300, 399, "rain"),
    (500, 599, "rain"),
    (600, 699, "snow"),
    (700, 799, "mist"),
    (800, 800, "clear"),
    (801, 804, "clouds"),
)


def _is_number(value: float | None) -> bool:
    return value is not None and math.isfinite(value)


def condition_group(code: int | None) -> ConditionGroup:
    """Grupo de condição pela faixa do código; fora das faixas, `neutral` (RN-017)."""
    if code is not None:
        for low, high, group in _GROUP_RANGES:
            if low <= code <= high:
                return group
    return "neutral"


def wind_direction(deg: float | None) -> str | None:
    """Ponto cardeal na rosa de 8 pontos, com o limite inferior do setor incluído (RN-019).

    O setor N vai de 337,5° a 22,5°, por isso 0° e 360° são "N".
    """
    if not _is_number(deg):
        return None
    return CARDINALS[math.floor((deg % 360 + 22.5) / 45) % 8]


def wind_label(speed_ms: float | None, deg: float | None) -> Scaled:
    """Vento como "4 m/s L" e "9 mph L" (RN-019).

    "Calmo" nas duas escalas abaixo de 0,5 m/s originais (RF-022). Sem direção, só a
    velocidade; sem velocidade, "—" (P-013).
    """
    if not _is_number(speed_ms):
        return Scaled(c=MISSING, f=MISSING)
    if speed_ms < CALM_BELOW_MS:
        return Scaled(c=CALM, f=CALM)
    cardinal = wind_direction(deg)
    suffix = f" {cardinal}" if cardinal else ""
    return Scaled(
        c=f"{format_number(speed_ms)} m/s{suffix}",
        f=f"{format_number(ms_to_mph(speed_ms))} mph{suffix}",
    )
