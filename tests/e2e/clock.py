"""Relógio simulado dos testes de ponta a ponta (`page.clock`)."""

import time

from playwright.sync_api import Page


def open_paused(page: Page) -> None:
    """Abre a página com o relógio simulado parado desde o início: o tempo da página (`Date`
    e `setTimeout`) só anda com `page.clock.run_for(ms)`.

    O `pause_at` vem antes do `goto`, para que o tempo de abrir a página não conte. No Python,
    o `pause_at` recebe um número em segundos.
    """
    now = time.time()
    page.clock.install(time=now)
    page.clock.pause_at(now)
    page.goto("/")
