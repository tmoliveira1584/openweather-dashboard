"""Log próprio da aplicação, sem dados de localização nem a chave (P-001, P-006).

O log de acesso do Uvicorn fica desligado (`--no-access-log`), porque registra a query string.
Este middleware registra `método rota status duração`.
"""

import logging
import time

from starlette.routing import Route
from starlette.types import ASGIApp, Message, Receive, Scope, Send

ACCESS_LOGGER = "app.access"

logger = logging.getLogger(ACCESS_LOGGER)


def configure_logging() -> None:
    """Ajusta os níveis dos loggers. Pode ser chamada mais de uma vez."""
    # Em INFO, httpx e httpcore registram a URL completa, com o appid (P-001).
    for name in ("httpx", "httpcore"):
        logging.getLogger(name).setLevel(logging.WARNING)

    app_logger = logging.getLogger("app")
    app_logger.setLevel(logging.INFO)
    if not app_logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        app_logger.addHandler(handler)


def _route_label(scope: Scope) -> str:
    """Modelo da rota encontrada, ou o caminho sem a query string se não houver rota.

    O modelo evita registrar valores do caminho, como os z/x/y das tiles, que revelam
    a área vista no mapa (P-006).
    """
    route = scope.get("route")
    if isinstance(route, Route):
        return route.path
    return scope["path"]


class AccessLogMiddleware:
    """Middleware ASGI que registra uma linha por requisição HTTP."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start = time.perf_counter()
        status = 500  # mantido se a rota levantar exceção antes de responder

        async def send_with_status(message: Message) -> None:
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_with_status)
        finally:
            duration_ms = round((time.perf_counter() - start) * 1000)
            logger.info("%s %s %d %dms", scope["method"], _route_label(scope), status, duration_ms)
