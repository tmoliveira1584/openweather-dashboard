"""Saída e volta à página simuladas nos testes de ponta a ponta (RF-014).

O Playwright não troca a aba do navegador para segundo plano. Aqui, o `visibilityState` do
documento é trocado e o evento `visibilitychange` é disparado, como o navegador faria.
"""

from playwright.sync_api import Page

SET_VISIBILITY_JS = """(state) => {
    Object.defineProperty(document, 'visibilityState', { value: state, configurable: true });
    document.dispatchEvent(new Event('visibilitychange'));
}"""


def leave_page(page: Page) -> None:
    """A página vai para segundo plano (outra aba ou janela minimizada)."""
    page.evaluate(SET_VISIBILITY_JS, "hidden")


def return_to_page(page: Page) -> None:
    """A página volta a ficar visível."""
    page.evaluate(SET_VISIBILITY_JS, "visible")
