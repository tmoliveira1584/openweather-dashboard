"""Chance de precipitação, volume de chuva e intensidade por minuto
(RN-036, RN-037, RN-041, RN-045, RN-047).
"""

import math
from decimal import Decimal

from app.domain.formatting import MISSING, format_number
from app.domain.time import time_label
from app.schemas.view import Band

# Limite superior de cada faixa, incluído nela, em mm/h (RN-041). Acima do último: `extreme`.
_BAND_LIMITS: tuple[tuple[float, Band], ...] = (
    (0, "none"),
    (0.5, "light"),
    (2.5, "moderate"),
    (7.5, "heavy"),
)


def _intensity(p: float | None) -> float | None:
    """Intensidade válida em mm/h; negativa ou não numérica conta como ausente (RN-047)."""
    if isinstance(p, bool) or not isinstance(p, int | float):
        return None
    if not math.isfinite(p) or p < 0:
        return None
    return p


def pop_label(pop: float | None) -> str:
    """Fração de 0 a 1 × 100, arredondada ao inteiro, com "%": 0,21 → "21%" (RN-036)."""
    if pop is None:
        return MISSING
    # Multiplica o texto decimal, para que 0,145 vire 14,5 e não 14,499…
    return f"{format_number(Decimal(repr(pop)) * 100)}%"


def rain_label(mm: float | None) -> str | None:
    """Volume em mm/h com 2 casas, como "0,21 mm/h" (RN-037).

    `None` quando o valor arredondado não é maior que zero ou quando falta o volume, que
    significa "sem chuva prevista".
    """
    if mm is None:
        return None
    text = format_number(mm, 2)
    if Decimal(text.replace(",", ".")) <= 0:
        return None
    return f"{text} mm/h"


def intensity_band(p: float | None) -> Band | None:
    """Faixa de intensidade com o limite superior incluído (RN-041).

    `None` para valor ausente, negativo ou não numérico (RN-047).
    """
    value = _intensity(p)
    if value is None:
        return None
    for limit, band in _BAND_LIMITS:
        if value <= limit:
            return band
    return "extreme"


def minute_tooltip(ts: int, offset: int, p: float | None) -> str:
    """Valor do cursor: "08:18 — 0,30 mm/h", ou "08:18 — —" sem intensidade (RN-045, RN-047)."""
    value = _intensity(p)
    amount = MISSING if value is None else f"{format_number(value, 2)} mm/h"
    return f"{time_label(ts, offset)} — {amount}"
