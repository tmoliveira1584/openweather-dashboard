"""Estrutura da tela nas larguras de referência: 360, 599, 600 e 1280 px (fatia 5), e os
maiores textos possíveis em 360 px (fatia 12).

O breakpoint é 600 px (arquitetura, seção 7.1). Os testes usam o esqueleto do index.html com
o `/api/weather` simulado e continuam valendo quando os blocos passarem a ser montados pelo
JavaScript.
"""

import re

import pytest
from playwright.sync_api import Page

WIDTHS = [360, 599, 600, 1280]

# Indicadores na mesma linha do primeiro = número de colunas da grade.
COLUMNS_JS = """() => {
    const tiles = [...document.querySelectorAll('.indicators > .indicator')];
    const top = tiles[0].getBoundingClientRect().top;
    return tiles.filter((t) => Math.abs(t.getBoundingClientRect().top - top) < 1).length;
}"""

PAGE_SCROLL_JS = """() => ({
    scroll: document.documentElement.scrollWidth,
    client: document.documentElement.clientWidth,
})"""


@pytest.fixture(autouse=True)
def _weather_ready(weather_api):
    """O `/api/weather` responde, e os blocos mostram o conteúdo em vez do estado de erro."""


def open_at(page: Page, width: int) -> None:
    page.set_viewport_size({"width": width, "height": 900})
    page.goto("/")
    page.locator('.current[data-block-state="ready"]').wait_for(state="attached")


@pytest.mark.parametrize("width", WIDTHS)
def test_p_024_page_has_no_horizontal_scroll(page: Page, width: int):
    """P-024, RNF-015: a partir de 360 px, a página nunca rola na horizontal."""
    open_at(page, width)

    size = page.evaluate(PAGE_SCROLL_JS)
    assert size["scroll"] <= size["client"], f"rolagem horizontal da página em {width} px"


@pytest.mark.parametrize(("width", "columns"), [(360, 2), (599, 2), (600, 3), (1280, 3)])
def test_rnf_011_indicators_use_3_columns_from_600px(page: Page, width: int, columns: int):
    """RNF-011: os seis cards ficam em 3 colunas a partir de 600 px e em 2 abaixo disso."""
    open_at(page, width)

    assert page.locator(".indicators > .indicator").count() == 6
    assert page.evaluate(COLUMNS_JS) == columns


def test_rnf_015_day_tabs_scroll_inside_their_strip(page: Page):
    """RNF-015, RF-032: em 360 px, as 8 abas não cabem e rolam dentro da própria faixa."""
    open_at(page, 360)

    strip = page.locator(".day-tabs")
    overflow = strip.evaluate("(el) => getComputedStyle(el).overflowX")
    widths = strip.evaluate("(el) => ({scroll: el.scrollWidth, client: el.clientWidth})")

    assert overflow == "auto"
    assert widths["scroll"] > widths["client"]
    size = page.evaluate(PAGE_SCROLL_JS)
    assert size["scroll"] <= size["client"]


@pytest.mark.parametrize("width", [600, 1280])
def test_rnf_021_minute_panel_overlays_map_from_600px(page: Page, width: int):
    """RNF-021: a partir de 600 px, o painel fica sobre o canto inferior esquerdo do mapa."""
    open_at(page, width)

    map_box = page.locator("#map").bounding_box()
    panel = page.locator(".minutely").bounding_box()

    assert panel["x"] >= map_box["x"]
    assert panel["y"] >= map_box["y"]
    assert panel["y"] + panel["height"] <= map_box["y"] + map_box["height"]
    # Ancorado à esquerda (em 600 px ocupa a largura toda, com margens iguais) e embaixo.
    left_gap = panel["x"] - map_box["x"]
    right_gap = map_box["x"] + map_box["width"] - (panel["x"] + panel["width"])
    top_gap = panel["y"] - map_box["y"]
    bottom_gap = map_box["y"] + map_box["height"] - (panel["y"] + panel["height"])
    assert left_gap <= right_gap
    assert bottom_gap < top_gap


@pytest.mark.parametrize("width", [360, 599])
def test_rnf_021_minute_panel_below_map_under_600px(page: Page, width: int):
    """RNF-021, feature 6 (categoria 10): abaixo de 600 px, o mapa ocupa a largura disponível,
    com altura mínima de 300 px, e o painel fica abaixo dele."""
    open_at(page, width)

    map_box = page.locator("#map").bounding_box()
    panel = page.locator(".minutely").bounding_box()
    main = page.locator("main").bounding_box()

    assert map_box["height"] >= 300
    assert map_box["width"] == pytest.approx(main["width"], abs=1)
    assert panel["y"] >= map_box["y"] + map_box["height"]


# ---------- Valores extremos em 360 px (fatia 12, T-12.6) ----------

LONG_CITY = {
    "lat": -15.0,
    "lon": -59.95,
    "headerLabel": "Vila Bela da Santíssima Trindade, BR",
    "markerLabel": "Vila Bela da Santíssima Trindade",
    "source": "search",
}
# Cada texto e a moldura que ele não pode ultrapassar.
FRAMES = [
    (".scale-toggle", ".app-header"),
    (".city", ".app-header"),
    (".search", ".app-header"),
    (".current-card", ".current"),
    (".indicators", ".current"),
    (".current-alerts", ".current-card"),
    (".current-time", ".current-card"),
    (".current-temp", ".current-card"),
    (".current-min", ".current-card"),
    (".current-description", ".current-card"),
    (".current-feels-like", ".current-card"),
    (".indicator-name", ".indicator"),
    (".indicator-value", ".indicator"),
    (".day-tab-label", ".day-tab"),
    (".day-tab-temp", ".day-tab"),
    (".hour-label", ".hour-card"),
    (".hour-pop", ".hour-card"),
    (".hour-temp", ".hour-card"),
    (".map-marker-label", "#map"),
]
OVERFLOW_JS = """(frames) => {
    const problems = [];
    for (const [selector, frameSelector] of frames) {
        const nodes = [...document.querySelectorAll(selector)];
        if (!nodes.length) problems.push(`${selector}: ausente`);
        for (const node of nodes) {
            if (node.hidden || !node.getClientRects().length) continue;
            const frame = node.closest(frameSelector) ?? document.querySelector(frameSelector);
            const box = node.getBoundingClientRect();
            const limit = frame.getBoundingClientRect();
            const text = node.textContent.trim().slice(0, 40);
            if (box.left < limit.left - 0.5 || box.right > limit.right + 0.5) {
                problems.push(`${selector} "${text}" sai de ${frameSelector}`);
            }
            if (node.clientWidth && node.scrollWidth > node.clientWidth + 1) {
                problems.push(`${selector} "${text}" cortado (${node.scrollWidth} > ${node.clientWidth})`);
            }
        }
    }
    return problems;
}"""


def extreme_view(view: dict) -> dict:
    """`WeatherView` com os maiores textos possíveis: temperaturas de 3 dígitos e negativas
    em °F (-100 °C = -148 °F), vento de 3 dígitos, umidade de 100%, pressão de 4 dígitos e
    índice UV de 2 dígitos."""

    def change(value):
        if isinstance(value, dict) and set(value) == {"c", "f"}:
            if all(isinstance(text, str) for text in value.values()):
                if "°" in value["c"]:
                    return {
                        scale: re.sub(r"-?\d+", n, value[scale], count=1)
                        for scale, n in (("c", "-100"), ("f", "-148"))
                    }
                if "/s" in value["c"]:
                    return {"c": "69 m/s NNO", "f": "155 mph NNO"}
            return value
        if isinstance(value, dict):
            changed = {key: change(item) for key, item in value.items()}
            if "humidity" in changed:
                changed |= {"humidity": "100%", "pressure": "1085 hPa", "uvi": "11 UV"}
            return changed
        if isinstance(value, list):
            return [change(item) for item in value]
        return value

    return change(view)


@pytest.mark.parametrize("scale", ["°C", "°F"])
def test_p_024_extreme_values_and_long_city_fit_at_360px(
    page: Page, weather_api, weather_views, scale: str
):
    """P-024, RNF-015, feature 1 (categoria 10): em 360 px, com temperaturas de 3 dígitos e
    negativas, vento de 3 dígitos e um nome de cidade longo, nenhum texto sai do seu card ou
    é cortado, e a página não rola na horizontal. O nome da cidade pode ser cortado com "…"
    no cabeçalho (completo ao focar)."""
    extreme = extreme_view(weather_views["uberlandia"])
    weather_api.views = {"uberlandia": extreme, "tokyo": extreme}
    open_at(page, 360)
    page.evaluate("async (city) => (await import('/js/actions.js')).selectCity(city)", LONG_CITY)
    page.get_by_role("button", name=scale, exact=True).click()
    expected = "-148°" if scale == "°F" else "-100°"
    for selector in (".current-temp", ".day-tab-temp >> nth=0", ".hour-temp >> nth=0"):
        assert page.locator(selector).text_content() == expected

    for tab in (None, "Qui"):
        if tab:
            page.locator(".day-tab", has_text=tab).click()
        assert page.evaluate(OVERFLOW_JS, FRAMES) == []
        size = page.evaluate(PAGE_SCROLL_JS)
        assert size["scroll"] <= size["client"], "rolagem horizontal da página"
