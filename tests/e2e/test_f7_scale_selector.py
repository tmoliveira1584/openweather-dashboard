"""Feature 7, seletor °C/°F do cabeçalho: escala inicial, destaque, teclado, consultas e
recarga da página.

Os blocos que mostram temperaturas e vento entram nas fatias 7 a 9. Aqui se verifica o
seletor e a escala ativa no estado, que é o que esses blocos vão ler.
"""

import pytest
from playwright.sync_api import Page, expect


@pytest.fixture
def api_requests(page: Page) -> list[str]:
    """URLs de todos os pedidos da página ao `/api`, também os que não chegam a ser simulados."""
    urls: list[str] = []
    page.on("request", lambda request: urls.append(request.url) if "/api/" in request.url else None)
    return urls


def option(page: Page, scale: str):
    group = page.get_by_role("group", name="Escala de temperatura")
    return group.get_by_role("button", name=scale, exact=True)


def scale_in_state(page: Page) -> str:
    return page.evaluate("async () => (await import('/js/state.js')).getState().scale")


def expect_active(page: Page, scale: str) -> None:
    other = "°F" if scale == "°C" else "°C"
    expect(option(page, scale)).to_have_attribute("aria-pressed", "true")
    expect(option(page, other)).to_have_attribute("aria-pressed", "false")


def test_rf_054_scale_starts_in_celsius(page: Page, weather_api):
    """RF-054, RF-053: o cabeçalho tem o seletor com °C e °F, e a página começa em °C."""
    page.goto("/")

    expect_active(page, "°C")
    assert scale_in_state(page) == "c"


def test_rf_053_active_scale_is_highlighted_beyond_color(page: Page, weather_api):
    """RF-053, RNF-028, P-018: a escala ativa é informada por `aria-pressed` e destacada por
    negrito e fundo, não só pela cor do texto."""
    page.goto("/")

    option(page, "°F").click()

    expect_active(page, "°F")
    styles = [
        option(page, scale).evaluate(
            "(n) => [getComputedStyle(n).fontWeight, getComputedStyle(n).backgroundColor]"
        )
        for scale in ("°F", "°C")
    ]
    (active_weight, active_bg), (inactive_weight, inactive_bg) = styles
    assert int(active_weight) >= 700 > int(inactive_weight)
    assert active_bg != inactive_bg


def test_rnf_027_switching_scale_changes_only_the_state(page: Page, weather_api, api_requests):
    """RNF-027, P-011, RF-055: alternar a escala muda só o estado, sem nenhuma consulta."""
    page.goto("/")
    expect(page.locator(".current")).to_have_attribute("data-block-state", "ready")
    assert len(api_requests) == 1

    for scale, expected in [("°F", "f"), ("°C", "c"), ("°F", "f")]:
        option(page, scale).click()
        assert scale_in_state(page) == expected

    page.wait_for_timeout(300)
    assert len(api_requests) == 1


def test_rnf_027_switching_during_loading_makes_no_extra_query(
    page: Page, weather_api, api_requests
):
    """RNF-027, feature 7 (categoria 7): alternar durante o carregamento muda a escala na
    hora, sem consulta adicional."""
    weather_api.hold = True
    page.goto("/")
    expect(page.locator(".current")).to_have_attribute("data-block-state", "loading")

    option(page, "°F").click()

    expect_active(page, "°F")
    weather_api.release()
    expect(page.locator(".current")).to_have_attribute("data-block-state", "ready")
    assert scale_in_state(page) == "f"
    assert len(api_requests) == 1


def test_rnf_028_click_on_active_scale_changes_nothing(page: Page, weather_api):
    """RNF-028, feature 7 (categoria 7): clicar na escala já ativa não muda nada, nem dispara
    um novo desenho."""
    page.goto("/")
    expect(page.locator(".current")).to_have_attribute("data-block-state", "ready")
    page.evaluate(
        """async () => {
            const { subscribe } = await import('/js/state.js');
            window.stateChanges = 0;
            subscribe(() => { window.stateChanges += 1; });
        }"""
    )

    option(page, "°C").click()

    expect_active(page, "°C")
    assert page.evaluate("window.stateChanges") == 0


def test_rnf_028_selector_is_operated_by_keyboard(page: Page, weather_api):
    """RNF-028, P-023: as opções recebem foco pelo Tab e são escolhidas com Enter ou
    Espaço."""
    page.goto("/")
    option(page, "°C").focus()

    page.keyboard.press("Tab")
    expect(option(page, "°F")).to_be_focused()
    page.keyboard.press("Enter")
    expect_active(page, "°F")

    page.keyboard.press("Shift+Tab")
    expect(option(page, "°C")).to_be_focused()
    page.keyboard.press("Space")
    expect_active(page, "°C")


def test_ca_044_reload_returns_to_celsius(page: Page, weather_api):
    """CA-044, RN-058, P-007: com °F ativo, recarregar a página volta para °C, e a escala não
    fica guardada no navegador."""
    page.goto("/")
    option(page, "°F").click()
    expect_active(page, "°F")
    stored = page.evaluate("() => [localStorage.length, sessionStorage.length, document.cookie]")
    assert stored == [0, 0, ""]

    page.reload()

    expect_active(page, "°C")
    assert scale_in_state(page) == "c"
