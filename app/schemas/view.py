"""View model: contrato do backend com o frontend (seção 6.3 da arquitetura).

Por enquanto traz só os tipos usados pelas regras do domínio (D-12, D-13). `WeatherView`,
`CitySearchResult` e `ReverseResult` entram na fatia 3.
"""

from typing import Literal

from pydantic import BaseModel

Scale = Literal["c", "f"]
ConditionGroup = Literal["thunderstorm", "rain", "snow", "mist", "clear", "clouds", "neutral"]
Band = Literal["none", "light", "moderate", "heavy", "extreme"]


class Scaled(BaseModel):
    """Texto pronto nas duas escalas, como `{"c": "4 m/s L", "f": "9 mph L"}`."""

    c: str
    f: str


class CityOption(BaseModel):
    """Cidade da busca ou da geocodificação reversa, com os rótulos prontos (RN-006 a RN-008)."""

    lat: float
    lon: float
    list_label: str
    header_label: str
    marker_label: str
