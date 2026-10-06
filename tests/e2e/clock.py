"""Relógio simulado dos testes de ponta a ponta (`page.clock`).

A fixture `page` já instala o relógio no momento das capturas (`CAPTURE_NOW`), andando
normalmente (D-22).
"""

from playwright.sync_api import Page

from tests.fakes import CAPTURE_NOW

# Um minuto depois da captura: sempre à frente do relógio instalado pela fixture `page`, que
# já andou um pouco até aqui (o `pause_at` não volta no tempo). Ainda é 16:42 de segunda em
# Uberlândia.
PAUSED_AT = CAPTURE_NOW + 60


def open_paused(page: Page) -> None:
    """Abre a página com o relógio simulado parado desde o início: o tempo da página (`Date`
    e `setTimeout`) só anda com `page.clock.run_for(ms)`.

    O `pause_at` vem antes do `goto`, para que o tempo de abrir a página não conte. No Python,
    o `pause_at` recebe um número em segundos.
    """
    page.clock.pause_at(PAUSED_AT)
    page.goto("/")
