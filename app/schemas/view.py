"""View model: contrato do backend com o frontend (seção 6.3 da arquitetura).

As chaves JSON são os nomes dos atributos, em `snake_case`. Texto ausente = "—" e número
ausente = `null` (P-013). Bloco sem dados = `null`, e o frontend mostra "indisponível".
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


class ScaledValue(BaseModel):
    """Número sem arredondar nas duas escalas. Serve só para posicionar a curva (guardrail 8)."""

    c: float | None
    f: float | None


class Indicators(BaseModel):
    """Os seis cards: vento, umidade, visibilidade, pressão, índice UV e ponto de orvalho."""

    wind: Scaled
    humidity: str
    visibility: str
    pressure: str
    uvi: str
    dew_point: Scaled


class CurrentView(BaseModel):
    """Card principal e indicadores da aba "Hoje" (RF-016 a RF-023)."""

    dt: int | None
    time_label: str
    temp: Scaled
    feels_like: Scaled
    description: str
    condition_group: ConditionGroup
    icon: str | None
    alerts_label: str | None
    indicators: Indicators


class DayView(BaseModel):
    """Aba e resumo de um dia da previsão diária (RF-024 a RF-032)."""

    local_date: str
    weekday_label: str
    date_label: str
    max: Scaled
    min_label: Scaled
    feels_like: Scaled
    description: str
    condition_group: ConditionGroup
    icon: str | None
    alerts_label: str | None
    indicators: Indicators


class HourView(BaseModel):
    """Card e ponto da curva da previsão hora a hora (RF-033 a RF-038)."""

    dt: int
    hour_label: str
    weekday_label: str | None
    temp: Scaled
    temp_value: ScaledValue
    pop: str
    rain_value: float | None
    rain_label: str | None
    icon: str | None
    description: str


class MinuteView(BaseModel):
    """Barra da previsão por minuto (RF-039 a RF-045)."""

    dt: int
    time_label: str
    intensity: float | None
    band: Band | None
    tooltip: str


class WeatherView(BaseModel):
    """Resposta de `GET /api/weather`."""

    timezone_offset: int | None
    current: CurrentView
    daily: list[DayView] | None
    hourly: list[HourView] | None
    minutely: list[MinuteView] | None


class CityOption(BaseModel):
    """Cidade da busca ou da geocodificação reversa, com os rótulos prontos (RN-006 a RN-008)."""

    lat: float
    lon: float
    list_label: str
    header_label: str
    marker_label: str


class CitySearchResult(BaseModel):
    """Resposta de `GET /api/geo/search`. `truncated` com exatamente 5 cidades (seção 6.3)."""

    results: list[CityOption]
    truncated: bool


class ReverseResult(BaseModel):
    """Resposta de `GET /api/geo/reverse`. Com `null`, o frontend usa "Sua localização" (RN-009)."""

    result: CityOption | None
