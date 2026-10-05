"""Subconjunto das respostas do OpenWeatherMap (seção 6.2 da arquitetura).

Todos os campos são opcionais e os campos extras são ignorados. Por enquanto traz só os
modelos usados pelas regras do domínio (D-13). O pacote da One Call (`OneCallBundle`) e o
tratamento de valores fora do formato entram na fatia 3.
"""

from pydantic import BaseModel, ConfigDict


class ProviderModel(BaseModel):
    model_config = ConfigDict(extra="ignore")


class Alert(ProviderModel):
    """Detalhe de um alerta (`onecall/alert/{id}`): só o ID e a vigência (ADR-013)."""

    id: str | None = None
    start: int | None = None
    end: int | None = None


class GeoResult(ProviderModel):
    """Item da geocodificação direta ou reversa."""

    name: str | None = None
    local_names: dict[str, str] | None = None
    state: str | None = None
    country: str | None = None
    lat: float | None = None
    lon: float | None = None
