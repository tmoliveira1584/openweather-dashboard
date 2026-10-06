"""Teste de fumaça: a página abre no Chrome instalado, sem erros nem login, e os testes rodam
sem internet."""

import re

from playwright.sync_api import Page, expect

CARTO_TILE = "https://a.basemaps.cartocdn.com/rastertiles/voyager/6/23/36.png"
OWM_ICON = "https://openweathermap.org/img/wn/10d@2x.png"

# Devolve "status content-type", ou "falhou" se a requisição for abortada.
FETCH_JS = """async (url) => {
    try {
        const r = await fetch(url);
        return `${r.status} ${r.headers.get("content-type")}`;
    } catch {
        return "falhou";
    }
}"""


def test_setup_page_opens_in_chrome(page: Page, browser_channel):
    """A página mínima abre no Chrome instalado, em pt-BR, com o Leaflet local."""
    assert browser_channel == "chrome"

    page.goto("/")

    expect(page).to_have_title("OpenWeather Dashboard")
    expect(page.locator("html")).to_have_attribute("lang", "pt-BR")
    assert page.evaluate(FETCH_JS, "/vendor/leaflet-1.9.4/leaflet.js").startswith("200 ")


def test_setup_e2e_runs_offline(page: Page):
    """Tiles e ícones são simulados; /api sem simulação e outros domínios falham."""
    page.goto("/")

    assert page.evaluate(FETCH_JS, CARTO_TILE) == "200 image/png"
    assert page.evaluate(FETCH_JS, OWM_ICON) == "200 image/png"
    assert page.evaluate(FETCH_JS, "https://example.com/") == "falhou"
    assert page.evaluate(FETCH_JS, "/api/weather?lat=-18.91&lon=-48.27") == "falhou"


def test_rnf_006_page_works_in_the_installed_chrome_without_errors(
    page: Page, browser, browser_channel, weather_api, tiles
):
    """RNF-006, L-01: no Chrome instalado (o único navegador testado no MVP), a página abre e
    mostra todos os blocos sem nenhum erro de JavaScript nem mensagem de erro no console."""
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)

    page.goto("/")

    for block in (".day-tabs", ".current", ".hourly", ".minutely"):
        expect(page.locator(block)).to_have_attribute("data-block-state", "ready")
    expect(page.locator("#map .map-marker")).to_be_visible()
    assert browser_channel == "chrome"
    assert int(browser.version.split(".")[0]) >= 100
    assert errors == []


def test_p_025_page_has_no_sign_up_or_login(page: Page, weather_api):
    """P-025: a página não pede cadastro nem login: nenhum campo de senha nem texto de acesso
    à conta."""
    page.goto("/")
    expect(page.locator(".current")).to_have_attribute("data-block-state", "ready")

    expect(page.locator("input[type='password']")).to_have_count(0)
    text = page.locator("body").inner_text()
    assert not re.search(r"(?i)\b(entrar|login|senha|cadastr\w*|criar conta)\b", text)
