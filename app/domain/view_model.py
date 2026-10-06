"""Monta o view model a partir do pacote da One Call 4.0 e da busca de cidades (seção 6.3).

Toda formatação acontece aqui, nas duas escalas, para o frontend só exibir os textos
(guardrail 8). Texto ausente = "—" e número ausente = `None` (P-013).
"""

from app.domain.alerts import alerts_label, count_alert_ids, count_alerts_on_day
from app.domain.conditions import condition_group, wind_label
from app.domain.formatting import (
    MISSING,
    format_humidity,
    format_pressure,
    format_temp,
    format_uvi,
    format_visibility,
)
from app.domain.places import city_option
from app.domain.precipitation import intensity_band, minute_tooltip, pop_label, rain_label
from app.domain.time import (
    date_label,
    hour_label,
    local_date,
    local_datetime,
    time_label,
    weekday_label,
)
from app.domain.units import celsius_to_fahrenheit
from app.schemas.provider import (
    Alert,
    Current,
    Day,
    GeoResult,
    Hour,
    Minute,
    OneCallBundle,
    Weather,
)
from app.schemas.view import (
    CitySearchResult,
    CurrentView,
    DayView,
    HourView,
    Indicators,
    MinuteView,
    Scaled,
    ScaledValue,
    WeatherView,
)

UTC_OFFSET = 0  # o `dt` de cada dia já é 00:00 UTC da data do dia (ADR-013)
MAX_SEARCH_RESULTS = 5  # `limit` da geocodificação direta (seção 6.1)


def _weather(items: list[Weather | None] | None) -> Weather:
    """Primeira condição da lista (`weather[0]`), ou uma condição vazia."""
    first = items[0] if items else None
    return first or Weather()


def _description(weather: Weather) -> str:
    """Texto do provedor com a primeira letra maiúscula: "nublado" → "Nublado" (RN-016)."""
    text = (weather.description or "").strip()
    return text[:1].upper() + text[1:] if text else MISSING


def _temp(celsius: float | None, prefix: str = "") -> Scaled:
    """Temperatura com "°" nas duas escalas (RN-014). O prefixo fica mesmo sem valor (D-15)."""
    return Scaled(c=prefix + format_temp(celsius, "c"), f=prefix + format_temp(celsius, "f"))


def _indicators(
    wind_speed: float | None,
    wind_deg: float | None,
    humidity: float | None,
    visibility: float | None,
    pressure: float | None,
    uvi: float | None,
    dew_point: float | None,
) -> Indicators:
    """Os seis cards, nos formatos de RN-019 a RN-024."""
    return Indicators(
        wind=wind_label(wind_speed, wind_deg),
        humidity=format_humidity(humidity),
        visibility=format_visibility(visibility),
        pressure=format_pressure(pressure),
        uvi=format_uvi(uvi),
        dew_point=Scaled(
            c=format_temp(dew_point, "c", with_unit=True),
            f=format_temp(dew_point, "f", with_unit=True),
        ),
    )


def _current(raw: Current | None, offset: int | None) -> CurrentView:
    """Card principal da aba "Hoje" (RF-016 a RF-023, RN-016, RN-018)."""
    raw = raw or Current()
    weather = _weather(raw.weather)
    known_time = raw.dt is not None and offset is not None
    return CurrentView(
        dt=raw.dt,
        time_label=time_label(raw.dt, offset) if known_time else MISSING,
        temp=_temp(raw.temp),
        feels_like=_temp(raw.feels_like, "Sensação de "),
        description=_description(weather),
        condition_group=condition_group(weather.id),
        icon=weather.icon,
        alerts_label=alerts_label(count_alert_ids(raw.alerts)),
        indicators=_indicators(
            raw.wind_speed,
            raw.wind_deg,
            raw.humidity,
            raw.visibility,
            raw.pressure,
            raw.uvi,
            raw.dew_point,
        ),
    )


def _day(raw: Day, alerts: list[Alert], offset: int) -> DayView:
    """Aba e resumo do dia (RN-028 a RN-033). A data é a data UTC do `dt` (ADR-013)."""
    weather = _weather(raw.weather)
    temp = raw.temp
    date = local_date(raw.dt, UTC_OFFSET)
    return DayView(
        local_date=date,
        weekday_label=weekday_label(raw.dt, UTC_OFFSET),
        date_label=date_label(raw.dt, UTC_OFFSET),
        max=_temp(temp.max if temp else None),
        min_label=_temp(temp.min if temp else None, "Mín. "),
        feels_like=_temp(raw.feels_like.day if raw.feels_like else None, "Sensação de "),
        description=_description(weather),
        condition_group=condition_group(weather.id),
        icon=weather.icon,
        alerts_label=alerts_label(count_alerts_on_day(alerts, date, offset)),
        indicators=_indicators(
            raw.wind_speed,
            raw.wind_deg,
            raw.humidity,
            raw.visibility,
            raw.pressure,
            raw.uvi,
            raw.dew_point,
        ),
    )


def _hour(raw: Hour, offset: int) -> HourView:
    """Card e ponto da curva hora a hora (RN-034 a RN-040)."""
    weather = _weather(raw.weather)
    rain = raw.rain.one_hour if raw.rain else None
    at_midnight = local_datetime(raw.dt, offset).hour == 0
    return HourView(
        dt=raw.dt,
        hour_label=hour_label(raw.dt, offset),
        weekday_label=weekday_label(raw.dt, offset) if at_midnight else None,
        temp=_temp(raw.temp),
        temp_value=ScaledValue(
            c=raw.temp,
            f=None if raw.temp is None else celsius_to_fahrenheit(raw.temp),
        ),
        pop=pop_label(raw.pop),
        rain_value=rain,
        rain_label=rain_label(rain),
        icon=weather.icon,
        description=_description(weather),
    )


def _minute(raw: Minute, offset: int) -> MinuteView:
    """Barra da previsão por minuto (RN-041, RN-045, RN-047)."""
    band = intensity_band(raw.precipitation)
    return MinuteView(
        dt=raw.dt,
        time_label=time_label(raw.dt, offset),
        intensity=None if band is None else raw.precipitation,
        band=band,
        tooltip=minute_tooltip(raw.dt, offset, raw.precipitation),
    )


def _timed[T: (Minute, Hour, Day)](records: list[T | None] | None) -> list[T]:
    """Registros que podem ser posicionados no tempo: sem `dt`, são descartados (D-15)."""
    return [record for record in records or [] if record is not None and record.dt is not None]


def build_weather_view(raw: OneCallBundle) -> WeatherView:
    """`WeatherView` da seção 6.3 a partir do pacote de `merge_onecall` (RN-016, RN-035, P-013).

    Bloco ausente ou sem registros = `None`, e o frontend mostra "indisponível". `daily` traz
    todos os dias recebidos: o recorte de "Hoje" e o limite de 8 ficam no frontend (D-14).
    Sem `timezone_offset`, os blocos que dependem da hora local também ficam `None` (D-15).
    """
    offset = raw.timezone_offset
    view = WeatherView(
        timezone_offset=offset,
        current=_current(raw.current, offset),
        daily=None,
        hourly=None,
        minutely=None,
    )
    if offset is None:
        return view

    alerts = [alert for alert in raw.alerts or [] if alert is not None]
    view.daily = [_day(day, alerts, offset) for day in _timed(raw.daily)] or None
    view.hourly = [_hour(hour, offset) for hour in _timed(raw.hourly)] or None
    view.minutely = [_minute(minute, offset) for minute in _timed(raw.minutely)] or None
    return view


def build_search_result(raw: list[GeoResult]) -> CitySearchResult:
    """Até 5 cidades com os rótulos prontos (RN-005 a RN-008).

    `truncated` é `True` quando o provedor devolve 5 cidades, o limite pedido: pode haver mais
    (dica "Mostrando as 5 primeiras…"). Uma cidade sem coordenadas sai da lista, porque não
    pode ser selecionada (D-13).
    """
    return CitySearchResult(
        results=[
            city_option(city)
            for city in raw[:MAX_SEARCH_RESULTS]
            if city.lat is not None and city.lon is not None
        ],
        truncated=len(raw) >= MAX_SEARCH_RESULTS,
    )
