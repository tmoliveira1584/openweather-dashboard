"""Estrutura da tela nas larguras de referência: 360, 599, 600 e 1280 px (fatia 5).

O breakpoint é 600 px (arquitetura, seção 7.1). Os testes usam o esqueleto estático do
index.html e continuam valendo quando os blocos passarem a ser montados pelo JavaScript.
"""

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


def open_at(page: Page, width: int) -> None:
    page.set_viewport_size({"width": width, "height": 900})
    page.goto("/")


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
