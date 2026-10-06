"""Cliente do OpenWeatherMap: o único lugar que conhece as URLs e a chave (ADR-003, ADR-013).

A chave vai só no parâmetro `appid` das chamadas. Ela nunca aparece em erros nem em logs: os
erros carregam só o código da seção 6.4 e o status HTTP (P-001, seção 7.6).
"""

import asyncio
import logging
import time
from collections.abc import Callable
from typing import Any
from urllib.parse import quote

import httpx

Response = dict[str, Any]

ONECALL_URL = "https://api.openweathermap.org/data/4.0/onecall/"
GEO_URL = "https://api.openweathermap.org/geo/1.0/"
TILE_URL = "https://tile.openweathermap.org/map/precipitation_new/{z}/{x}/{y}.png"

PROVIDER_TIMEOUT_S = 15.0  # por chamada (RN-012)
HOUR_S = 3600
HOURLY_PAGE_S = 20 * HOUR_S  # cada página por hora traz 20 registros (ADR-013)
SEARCH_LIMIT = 5
REVERSE_LIMIT = 1
ALERT_FIELDS = ("id", "start", "end")  # do detalhe do alerta, só a vigência importa (ADR-013)

# Com várias falhas, prevalece a causa mais acionável para o usuário (seção 6.4).
ERROR_PRECEDENCE = (
    "provider_unauthorized",
    "provider_rate_limited",
    "provider_timeout",
    "network_unavailable",
    "provider_unavailable",
)
_STATUS_CODES = {
    401: "provider_unauthorized",
    403: "provider_unauthorized",
    429: "provider_rate_limited",
}

logger = logging.getLogger("app.provider")


class ProviderError(Exception):
    """Falha numa chamada ao provedor, com o código da seção 6.4 e o status HTTP, se houver."""

    def __init__(self, code: str, status: int | None = None) -> None:
        super().__init__(code)
        self.code = code
        self.status = status


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


def _alert_ids(*responses: Response | None) -> list[str]:
    """IDs distintos e não vazios das listas `alerts` dos registros, na ordem em que aparecem."""
    ids: dict[str, None] = {}
    for record in (item for response in responses for item in _records(response)):
        alerts = record.get("alerts") if isinstance(record, dict) else None
        for alert_id in alerts if isinstance(alerts, list) else []:
            if isinstance(alert_id, str) and alert_id.strip():
                ids[alert_id] = None
    return list(ids)


def _raise_first_error(results: list[Any]) -> None:
    """Levanta a falha mais acionável de uma rodada de chamadas em paralelo (seção 6.4)."""
    errors = [result for result in results if isinstance(result, BaseException)]
    for error in errors:
        if not isinstance(error, ProviderError):
            raise error
    if errors:
        raise min(errors, key=lambda error: ERROR_PRECEDENCE.index(error.code))


class OpenWeatherClient:
    """Chamadas ao OpenWeatherMap com tempo limite e os erros da seção 6.4 (ADR-003, ADR-013).

    `clock` dá o "agora" em segundos Unix, usado só no `start` da previsão por hora. Os testes
    injetam um relógio parado.
    """

    def __init__(
        self, http: httpx.AsyncClient, api_key: str, clock: Callable[[], float] = time.time
    ) -> None:
        self._http = http
        self._api_key = api_key
        self._clock = clock

    def _error(self, label: str, code: str, status: int | None = None) -> ProviderError:
        """Registra a falha só com o endpoint, o código e o status, nunca a URL (seção 7.6)."""
        logger.warning("Falha no provedor: %s %s HTTP %s", label, code, status or "-")
        return ProviderError(code, status)

    async def _get(
        self, label: str, url: str, params: dict[str, Any], *, missing_ok: bool = False
    ) -> httpx.Response | None:
        """GET com a chave e tempo limite de 15 s. Com `missing_ok`, um 404 devolve `None`.

        A exceção original do httpx é descartada (`from None`), porque pode trazer a URL.
        """
        try:
            response = await self._http.get(
                url, params={**params, "appid": self._api_key}, timeout=PROVIDER_TIMEOUT_S
            )
        except httpx.TimeoutException:
            raise self._error(label, "provider_timeout") from None
        except httpx.ConnectError:
            raise self._error(label, "network_unavailable") from None
        except httpx.TransportError:
            raise self._error(label, "provider_unavailable") from None

        status = response.status_code
        if status == 404 and missing_ok:
            return None
        if not response.is_success:
            raise self._error(label, _STATUS_CODES.get(status, "provider_unavailable"), status)
        return response

    async def _json[T: (dict, list)](
        self,
        label: str,
        url: str,
        params: dict[str, Any],
        expected: type[T],
        *,
        missing_ok: bool = False,
    ) -> T | None:
        """Corpo JSON no formato esperado (objeto ou lista). Outro formato é falha do provedor."""
        response = await self._get(label, url, params, missing_ok=missing_ok)
        if response is None:
            return None
        try:
            data = response.json()
        except ValueError:
            raise self._error(label, "provider_unavailable", response.status_code) from None
        if not isinstance(data, expected):
            raise self._error(label, "provider_unavailable", response.status_code)
        return data

    async def weather(self, lat: float, lon: float) -> Response:
        """Pacote da seção 6.2: 5 chamadas em paralelo e, se houver alertas, o detalhe de cada um.

        Sempre em unidades métricas e em português (RN-059). Um 404 numa previsão vira bloco
        ausente; qualquer outra falha derruba a consulta inteira (ADR-013).
        """
        params = {"lat": lat, "lon": lon, "units": "metric", "lang": "pt_br"}
        start = int(self._clock()) // HOUR_S * HOUR_S
        timeline = ONECALL_URL + "timeline/"
        hourly_pages = (
            self._json(
                "onecall/timeline/1h",
                timeline + "1h",
                {**params, "start": page_start},
                dict,
                missing_ok=True,
            )
            for page_start in (start, start + HOURLY_PAGE_S)
        )
        results = await asyncio.gather(
            self._json("onecall/current", ONECALL_URL + "current", params, dict),
            self._json("onecall/timeline/1min", timeline + "1min", params, dict, missing_ok=True),
            *hourly_pages,
            self._json("onecall/timeline/1day", timeline + "1day", params, dict, missing_ok=True),
            return_exceptions=True,
        )
        _raise_first_error(results)
        current, minutely, first_hours, next_hours, daily = results

        alerts = await self._alerts(_alert_ids(current, minutely, first_hours, next_hours))
        return merge_onecall(current, minutely, [first_hours, next_hours], daily, alerts)

    async def _alerts(self, ids: list[str]) -> list[Response]:
        """Segunda rodada: o detalhe de cada alerta, em paralelo (ADR-013)."""
        results = await asyncio.gather(*(self._alert(i) for i in ids), return_exceptions=True)
        _raise_first_error(results)
        return results

    async def _alert(self, alert_id: str) -> Response:
        """Detalhe de um alerta, com o ID codificado na URL. Com 404, fica só com o `id`."""
        url = ONECALL_URL + "alert/" + quote(alert_id, safe="")
        detail = await self._json("onecall/alert/{id}", url, {}, dict, missing_ok=True)
        return {"id": alert_id} if detail is None else detail

    async def geocode(self, q: str) -> list[Any]:
        """Geocodificação direta: até 5 cidades para o termo (seção 6.1)."""
        params = {"q": q, "limit": SEARCH_LIMIT}
        return await self._json("geo/direct", GEO_URL + "direct", params, list)

    async def reverse(self, lat: float, lon: float) -> list[Any]:
        """Geocodificação reversa: a cidade das coordenadas (seção 6.1)."""
        params = {"lat": lat, "lon": lon, "limit": REVERSE_LIMIT}
        return await self._json("geo/reverse", GEO_URL + "reverse", params, list)

    async def tile(self, z: int, x: int, y: int) -> bytes:
        """Tile PNG da camada de chuva, com os bytes repassados (ADR-006)."""
        url = TILE_URL.format(z=z, x=x, y=y)
        response = await self._get("tile/precipitation/{z}/{x}/{y}", url, {})
        return response.content
