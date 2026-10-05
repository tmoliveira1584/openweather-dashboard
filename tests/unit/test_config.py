"""Testes da leitura de configuração (P-002), com chave falsa."""

import pytest

from app.config import ConfigError, Settings, load_settings

FAKE_KEY = "chave-falsa-de-teste"


def test_p_002_reads_api_key_from_environment():
    """P-002: a chave vem da configuração de ambiente."""
    settings = load_settings({"OPENWEATHER_API_KEY": f"  {FAKE_KEY}\n"})

    assert settings == Settings(openweather_api_key=FAKE_KEY)


@pytest.mark.parametrize(
    "environ",
    [{}, {"OPENWEATHER_API_KEY": ""}, {"OPENWEATHER_API_KEY": "  "}],
    ids=["ausente", "vazia", "so-espacos"],
)
def test_p_002_fails_when_api_key_is_missing(environ):
    """P-002: sem a chave no ambiente, a aplicação não inicia."""
    with pytest.raises(ConfigError, match="OPENWEATHER_API_KEY"):
        load_settings(environ)


def test_p_002_settings_repr_never_exposes_key():
    """P-002, P-001: o valor da chave não aparece no repr das configurações."""
    settings = load_settings({"OPENWEATHER_API_KEY": FAKE_KEY})

    assert FAKE_KEY not in repr(settings)
    assert FAKE_KEY not in str(settings)
