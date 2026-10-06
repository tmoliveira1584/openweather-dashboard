"""Ponto de entrada do backend: `uvicorn app.main:app`."""

from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import InvalidRequestError, router
from app.clients.openweather import PROVIDER_TIMEOUT_S, OpenWeatherClient, ProviderError
from app.config import load_settings
from app.logging_setup import AccessLogMiddleware, configure_logging

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

# Status HTTP de cada código de erro do provedor (seção 6.4). Os demais respondem 502.
GATEWAY_TIMEOUT_CODES = {"provider_timeout"}


def _error(status: int, code: str) -> JSONResponse:
    """Formato único de erro: `{"error": "<código>"}`, sem detalhes técnicos (P-004)."""
    return JSONResponse({"error": code}, status_code=status)


async def _invalid_request(request: Request, exc: Exception) -> JSONResponse:
    """Parâmetro inválido: 400 no lugar do 422 do FastAPI, sem repetir o valor recebido."""
    return _error(400, "invalid_request")


async def _provider_error(request: Request, exc: ProviderError) -> JSONResponse:
    """Falha do provedor: 504 por tempo esgotado, 502 nos demais casos (seção 6.4)."""
    return _error(504 if exc.code in GATEWAY_TIMEOUT_CODES else 502, exc.code)


async def _no_store(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Toda resposta de `/api` sai com `Cache-Control: no-store` (seção 6.1)."""
    response = await call_next(request)
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    return response


def create_app(client: OpenWeatherClient | None = None) -> FastAPI:
    """Monta a aplicação. Os testes injetam `client` para não usar a chave nem a rede."""
    configure_logging()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        if client is not None:
            app.state.client = client
            yield
            return

        # Sem a chave, a aplicação não inicia (P-002).
        app.state.settings = load_settings()
        async with httpx.AsyncClient(timeout=PROVIDER_TIMEOUT_S) as http:
            app.state.http = http
            app.state.client = OpenWeatherClient(http, app.state.settings.openweather_api_key)
            yield

    app = FastAPI(title="OpenWeather Dashboard", lifespan=lifespan)
    app.add_middleware(AccessLogMiddleware)
    app.middleware("http")(_no_store)
    app.add_exception_handler(RequestValidationError, _invalid_request)
    app.add_exception_handler(InvalidRequestError, _invalid_request)
    app.add_exception_handler(ProviderError, _provider_error)
    app.include_router(router)

    # Montado por último: as rotas /api registradas antes têm prioridade.
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
    return app


app = create_app()
