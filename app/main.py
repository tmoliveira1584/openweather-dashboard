"""Ponto de entrada do backend: `uvicorn app.main:app`."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import load_settings
from app.logging_setup import AccessLogMiddleware, configure_logging

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

# Tempo limite de cada chamada ao provedor (RN-012).
PROVIDER_TIMEOUT_S = 15.0


def create_app(client=None) -> FastAPI:
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
            yield

    app = FastAPI(title="OpenWeather Dashboard", lifespan=lifespan)
    app.add_middleware(AccessLogMiddleware)

    # Montado por último: as rotas /api registradas antes têm prioridade.
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
    return app


app = create_app()
