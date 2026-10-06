"""Cliente do OpenWeatherMap (ADR-003, ADR-013).

Por enquanto traz só a função pura `merge_onecall`. O `OpenWeatherClient`, com as chamadas
HTTP e o `ProviderError`, entra na fatia 4.
"""

from typing import Any

Response = dict[str, Any]

ALERT_FIELDS = ("id", "start", "end")  # do detalhe do alerta, só a vigência importa (ADR-013)


def _records(response: Response | None) -> list[Any]:
    """Lista `data` de uma resposta. 404 (`None`) ou formato inesperado viram lista vazia."""
    if not isinstance(response, dict):
        return []
    data = response.get("data")
    return data if isinstance(data, list) else []


def _join_pages(pages: list[Response | None]) -> list[Any]:
    """Une as páginas por hora na ordem recebida, sem repetir `dt` (ADR-013)."""
    seen: set[Any] = set()
    joined = []
    for page in pages:
        for item in _records(page):
            dt = item.get("dt") if isinstance(item, dict) else None
            if dt is not None:
                if dt in seen:
                    continue
                seen.add(dt)
            joined.append(item)
    return joined


def _alert_validity(detail: Any) -> Any:
    """Só `id`, `start` e `end` do detalhe. Um alerta sem detalhe (404) chega só com `id`."""
    if not isinstance(detail, dict):
        return detail
    return {key: detail[key] for key in ALERT_FIELDS if key in detail}


def merge_onecall(
    current: Response | None,
    minutely: Response | None,
    hourly_pages: list[Response | None],
    daily: Response | None,
    alerts: list[Response] | None,
) -> Response:
    """Pacote da seção 6.2 a partir das respostas da One Call 4.0 (ADR-013).

    Cada argumento é a resposta do endpoint ou `None` (404). Uma previsão com 404 ou com
    `data` vazia fica ausente do pacote, e o view model a mostra como indisponível. Só a lista
    `data` de cada resposta é usada: os links `next`/`prev`, que trazem a chave, são
    descartados (guardrail 13). `alerts` é a lista de detalhes dos alertas.
    """
    bundle: Response = {}
    if isinstance(current, dict) and "timezone_offset" in current:
        bundle["timezone_offset"] = current["timezone_offset"]

    current_records = _records(current)
    if current_records:
        bundle["current"] = current_records[0]

    blocks = {
        "minutely": _records(minutely),
        "hourly": _join_pages(hourly_pages),
        "daily": _records(daily),
    }
    bundle.update({key: records for key, records in blocks.items() if records})

    if alerts:
        bundle["alerts"] = [_alert_validity(detail) for detail in alerts]
    return bundle
