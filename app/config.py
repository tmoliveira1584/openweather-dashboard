"""Configuração da aplicação, lida do ambiente (P-002).

A chave do OpenWeatherMap fica só no `.env`, carregado pelo `uvicorn --env-file .env`.
"""

import os
from collections.abc import Mapping
from dataclasses import dataclass, field

API_KEY_VAR = "OPENWEATHER_API_KEY"


class ConfigError(RuntimeError):
    """Configuração obrigatória ausente. A mensagem nunca contém valores secretos."""


@dataclass(frozen=True)
class Settings:
    # repr=False: a chave não aparece em logs nem em rastros de erro (P-001).
    openweather_api_key: str = field(repr=False)


def load_settings(environ: Mapping[str, str] | None = None) -> Settings:
    """Lê as configurações do ambiente e falha se a chave não existir (P-002)."""
    if environ is None:
        environ = os.environ
    api_key = environ.get(API_KEY_VAR, "").strip()
    if not api_key:
        raise ConfigError(
            f"A variável {API_KEY_VAR} não foi definida. "
            "Copie o .env.example para .env, preencha a chave e inicie com --env-file .env."
        )
    return Settings(openweather_api_key=api_key)
