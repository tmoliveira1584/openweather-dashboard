"""Teste de fumaça: a página abre no Chrome instalado e os testes rodam sem internet."""

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
