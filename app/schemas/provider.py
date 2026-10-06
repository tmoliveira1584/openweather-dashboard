"""Subconjunto das respostas do OpenWeatherMap (seção 6.2 da arquitetura).

Todos os campos são opcionais e os campos extras são ignorados. Um campo ausente ou fora do
formato (ex.: texto onde se espera número, NaN, objeto no lugar de lista) vira `None` e nunca
causa erro 500: as regras tratam a falta (cenários de categoria 5 do spec, P-013). Numa lista,
só o item inválido vira `None`.
"""

from typing import Annotated, Any

from pydantic import (
    AllowInfNan,
    BaseModel,
    ConfigDict,
    Field,
    Strict,
    ValidationError,
    ValidatorFunctionWrapHandler,
    WrapValidator,
)


def _none_if_invalid(value: Any, handler: ValidatorFunctionWrapHandler) -> Any:
    """Valor fora do formato vira `None` em vez de erro de validação."""
    try:
        return handler(value)
    except ValidationError:
        return None


_Lenient = WrapValidator(_none_if_invalid)

# Tipos estritos: "20" não vira 20 e True não vira 1. Inteiro vale onde se espera número.
Number = Annotated[float | None, Strict(), AllowInfNan(False), _Lenient]
Integer = Annotated[int | None, Strict(), _Lenient]
Text = Annotated[str | None, Strict(), _Lenient]

# Objeto ou lista fora do formato também vira `None`. Numa lista, só o item inválido.
type Maybe[T] = Annotated[T | None, _Lenient]
type Items[T] = Maybe[list[Maybe[T]]]


class ProviderModel(BaseModel):
    model_config = ConfigDict(extra="ignore")


class Weather(ProviderModel):
    """Condição do tempo (`weather[0]`): código, descrição em pt-BR e ícone (RN-016, RN-017)."""

    id: Integer = None
    description: Text = None
    icon: Text = None


class Current(ProviderModel):
    """Registro de `onecall/current` (RF-016 a RF-023)."""

    dt: Integer = None
    temp: Number = None
    feels_like: Number = None
    pressure: Number = None
    humidity: Number = None
    dew_point: Number = None
    uvi: Number = None
    visibility: Number = None
    wind_speed: Number = None
    wind_deg: Number = None
    weather: Items[Weather] = None
    alerts: Items[Text] = None


class Minute(ProviderModel):
    """Registro de `timeline/1min`, em mm/h (RN-041 a RN-047)."""

    dt: Integer = None
    precipitation: Number = None


class Rain(ProviderModel):
    """Volume de chuva da hora, em mm/h (RN-037)."""

    one_hour: Number = Field(None, alias="1h")


class Hour(ProviderModel):
    """Registro de `timeline/1h` (RN-034 a RN-040)."""

    dt: Integer = None
    temp: Number = None
    pop: Number = None
    rain: Maybe[Rain] = None
    weather: Items[Weather] = None


class DayTemp(ProviderModel):
    max: Number = None
    min: Number = None


class DayFeelsLike(ProviderModel):
    day: Number = None


class Day(ProviderModel):
    """Registro de `timeline/1day`. O `dt` é 00:00 UTC da data do dia (ADR-013)."""

    dt: Integer = None
    temp: Maybe[DayTemp] = None
    feels_like: Maybe[DayFeelsLike] = None
    humidity: Number = None
    visibility: Number = None
    pressure: Number = None
    dew_point: Number = None
    uvi: Number = None
    wind_speed: Number = None
    wind_deg: Number = None
    weather: Items[Weather] = None


class Alert(ProviderModel):
    """Detalhe de um alerta (`onecall/alert/{id}`): só o ID e a vigência (ADR-013)."""

    id: Text = None
    start: Integer = None
    end: Integer = None


class OneCallBundle(ProviderModel):
    """Pacote montado por `merge_onecall`: entrada do view model (seção 6.2, ADR-013)."""

    timezone_offset: Integer = None
    current: Maybe[Current] = None
    minutely: Items[Minute] = None
    hourly: Items[Hour] = None
    daily: Items[Day] = None
    alerts: Items[Alert] = None


class GeoResult(ProviderModel):
    """Item da geocodificação direta ou reversa."""

    name: Text = None
    local_names: Maybe[dict[str, Text]] = None
    state: Text = None
    country: Text = None
    lat: Number = None
    lon: Number = None
