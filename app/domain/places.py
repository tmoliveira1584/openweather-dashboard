"""Rótulos de cidade da busca e da geocodificação reversa (RN-006 a RN-008, RN-050)."""

from app.domain.formatting import MISSING
from app.schemas.provider import GeoResult
from app.schemas.view import CityOption


def _display_name(raw: GeoResult) -> str:
    """Nome em português do provedor ou, sem ele, o nome padrão (RN-006)."""
    portuguese = (raw.local_names or {}).get("pt")
    return portuguese or raw.name or MISSING


def _join(*parts: str | None) -> str:
    return ", ".join(part for part in parts if part)


def city_option(raw: GeoResult) -> CityOption:
    """Cidade com os rótulos do cabeçalho (RN-007), da lista (RN-008) e do marcador (RN-050).

    Sem país ou sem estado, a parte que falta é omitida. O item precisa ter coordenadas.
    """
    name = _display_name(raw)
    return CityOption(
        lat=raw.lat,
        lon=raw.lon,
        list_label=_join(name, raw.state, raw.country),
        header_label=_join(name, raw.country),
        marker_label=name,
    )
