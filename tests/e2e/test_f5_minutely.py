"""Feature 5, previsão por minuto: barras por faixa, marcos, legenda, resumo, valor do minuto
pelo cursor e pelo teclado, indisponibilidade, escala e larguras (fatia 10).

O relógio da página está no momento das capturas: segunda, 05/10/2026, 16:41 em Uberlândia
(ver a fixture `page`). A previsão por minuto da captura vai das 16:42 às 17:41, com chuva
em todos os minutos; a de Tóquio, das 04:42 às 05:41, sem chuva.
"""

import copy
import re
from itertools import pairwise

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.weather_api import _load, bundle, view_of

TITLE = "Previsão por minuto — precipitação"
LEGEND = ["0 mm/h", "até 0,5 mm/h", "0,5 a 2,5 mm/h", "2,5 a 7,5 mm/h", "acima de 7,5 mm/h"]
BANDS = ["none", "light", "moderate", "heavy", "extreme"]
# Intensidades de borda dos 11 primeiros minutos (tests/fixtures/README.md), das 16:42 às
# 16:52: 0; 0,3; 0,5; 1,0; 2,5; 5,0; 7,5; 8,0; 12; -1 e ausente.
BANDS_VIEW = view_of(_load("onecall_minutely_bands.json"))
RGB = re.compile(r"rgba?\((\d+), (\d+), (\d+)")


def minutely_view(change) -> dict:
    """`WeatherView` de Uberlândia com os minutos da captura alterados por `change(minutes)`."""
    raw = copy.deepcopy(bundle("uberlandia"))
    change(raw["minutely"])
    return view_of(raw)


def open_with(page: Page, weather_api, view: dict | None = None, at: int | None = None):
    """Abre a página com a resposta `view` (ou a captura), com o relógio em `at` (ou no momento
    das capturas), e espera o painel sair do carregamento."""
    if view is not None:
        weather_api.queue = [view]
    if at is not None:
        page.clock.set_system_time(at)
    page.goto("/")
    expect(page.locator(".minutely")).to_have_attribute(
        "data-block-state", re.compile("ready|unavailable")
    )


def bars(page: Page):
    return page.locator(".minutely-bars .bar")


def chart(page: Page):
    return page.get_by_role("slider", name=TITLE)


def tooltip(page: Page):
    return page.locator(".minutely-tooltip")


def mark_texts(page: Page) -> list[str]:
    marks = page.locator(".mark")
    return [
        f"{mark.locator('.mark-label').text_content()} {mark.locator('.mark-time').text_content()}"
        for mark in marks.all()
    ]


def bar_classes(page: Page, indexes: list[int]) -> list[str]:
    return [bars(page).nth(i).get_attribute("class") for i in indexes]


def hover_minute(page: Page, index: int, count: int) -> None:
    """Põe o cursor no centro da coluna do minuto `index`, com o gráfico à vista."""
    page.locator(".minutely-bars").scroll_into_view_if_needed()
    box = page.locator(".minutely-bars").bounding_box()
    page.mouse.move(box["x"] + (index + 0.5) * box["width"] / count, box["y"] + box["height"] / 2)


def luminance(color: str) -> float:
    """Luminância relativa da WCAG 2.1 de uma cor `rgb(r, g, b)`."""
    channels = []
    for value in RGB.match(color).groups():
        c = int(value) / 255
        channels.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    r, g, b = channels
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    high, low = sorted([luminance(a), luminance(b)], reverse=True)
    return (high + 0.05) / (low + 0.05)


# ---------- Barras, legenda, marcos e resumo (T-10.2) ----------


def test_rf_039_one_bar_per_minute_of_the_next_hour(page: Page, weather_api, weather_views):
    """RF-039, RN-047: uma barra para cada minuto da próxima hora, a partir do primeiro que
    ainda não passou: 60 na captura, de 16:42 a 17:41."""
    open_with(page, weather_api)

    expect(bars(page)).to_have_count(60)
    expect(page.locator(".mark-time").first).to_have_text("16:42")


def test_rn_047_cached_data_starts_at_the_first_minute_not_gone(page: Page, weather_api):
    """RN-047, feature 5 (categoria 8): com dados de alguns minutos atrás, a janela começa no
    primeiro minuto que ainda não passou, com menos de 60 barras, e os marcos sem barras
    suficientes não aparecem. Às 16:47, sobram 55 barras e não há o marco de 60 min."""
    first = bundle("uberlandia")["minutely"][0]["dt"]

    open_with(page, weather_api, at=first + 5 * 60)

    expect(bars(page)).to_have_count(55)
    assert mark_texts(page) == ["Agora 16:47", "15 min 17:02", "30 min 17:17", "45 min 17:32"]


def test_ca_027_bars_take_the_band_color_and_legend_shows_5_bands(page: Page, weather_api):
    """CA-027, RF-040, RF-042, RN-041: intensidades 0; 0,3; 1,0; 5,0 e 8,0 dão barras cinza,
    verde, verde-escuro, amarelo e vermelho, e a legenda mostra as 5 faixas em texto."""
    open_with(page, weather_api, BANDS_VIEW)

    assert bar_classes(page, [0, 1, 3, 5, 7]) == [f"bar band-{band}" for band in BANDS]
    expect(page.locator(".legend-item")).to_have_text(LEGEND)
    swatches = page.locator(".legend-swatch")
    for index, band in enumerate(BANDS):
        expect(swatches.nth(index)).to_have_class(f"legend-swatch band-{band}")


def test_ca_028_upper_limit_belongs_to_the_band(page: Page, weather_api):
    """CA-028, RN-041, feature 5 (categoria 6): 0,5; 2,5 e 7,5 dão verde, verde-escuro e
    amarelo, porque o limite superior é incluído na faixa."""
    open_with(page, weather_api, BANDS_VIEW)

    assert bar_classes(page, [2, 4, 6]) == ["bar band-light", "bar band-moderate", "bar band-heavy"]


def test_rn_042_bar_height_has_ceiling_at_10_and_minimum_at_zero(page: Page, weather_api):
    """RN-042, feature 5 (categoria 6): a altura é proporcional à intensidade, com teto em
    10 mm/h. A barra de 12 mm/h tem a altura máxima, e o cursor mostra o valor real; a de
    0 mm/h tem a altura mínima visível."""
    open_with(page, weather_api, BANDS_VIEW)

    heights = [bars(page).nth(i).bounding_box()["height"] for i in (0, 5, 7, 8)]
    chart_height = page.locator(".minutely-bars").bounding_box()["height"]

    assert heights[3] == pytest.approx(chart_height, abs=0.5)
    assert heights[2] == pytest.approx(0.8 * chart_height, abs=0.5)
    assert heights[1] == pytest.approx(0.5 * chart_height, abs=0.5)
    assert 1 < heights[0] < 0.1 * chart_height
    hover_minute(page, 8, 60)
    expect(tooltip(page)).to_have_text("16:50 — 12,00 mm/h")


def test_rn_047_minute_without_value_leaves_an_empty_space(page: Page, weather_api):
    """RN-047, feature 5 (categoria 5): um valor negativo ou ausente não desenha barra, o lugar
    dela fica vazio e o cursor mostra "—"."""
    open_with(page, weather_api, BANDS_VIEW)

    for index in (9, 10):
        expect(bars(page).nth(index)).to_have_class("bar is-missing")
        expect(bars(page).nth(index)).to_have_attribute("height", "0")
    hover_minute(page, 9, 60)
    expect(tooltip(page)).to_have_text("16:51 — —")


def test_ca_029_marks_have_label_and_city_time(page: Page, weather_api):
    """CA-029, RF-041, RN-043: os marcos "Agora", "15 min", "30 min", "45 min" e "60 min" têm
    o horário local. Cada um fica no início do seu minuto, e o de 60 min, no fim da última
    barra; nenhum sai do gráfico."""
    open_with(page, weather_api)

    assert mark_texts(page) == [
        "Agora 16:42",
        "15 min 16:57",
        "30 min 17:12",
        "45 min 17:27",
        "60 min 17:42",
    ]
    box = page.locator(".minutely-bars").bounding_box()
    for mark, position in zip(page.locator(".mark").all(), [0, 0.25, 0.5, 0.75, 1], strict=True):
        tile = mark.bounding_box()
        anchor = tile["x"] + position * tile["width"]
        assert anchor == pytest.approx(box["x"] + position * box["width"], abs=1)
        assert box["x"] - 0.5 <= tile["x"]
        assert tile["x"] + tile["width"] <= box["x"] + box["width"] + 0.5


def test_p_015_marks_in_the_city_timezone(page: Page, weather_api, weather_views):
    """P-015, RN-043, feature 5 (categoria 8): com outra cidade, os marcos ficam no fuso dela
    (Tóquio, 12 horas à frente de Uberlândia)."""
    open_with(page, weather_api, weather_views["tokyo"])

    assert mark_texts(page)[0] == "Agora 04:42"
    assert mark_texts(page)[-1] == "60 min 05:42"


def test_ca_030_no_rain_all_gray_and_summary(page: Page, weather_api, weather_views):
    """CA-030, RN-041, RN-042, feature 5 (categoria 6): com todas as intensidades 0, as barras
    ficam cinza, com a altura mínima, e o resumo é "Sem chuva prevista na próxima hora."."""
    open_with(page, weather_api, weather_views["tokyo"])

    classes = page.locator(".minutely-bars .bar").evaluate_all(
        "(nodes) => nodes.map((node) => node.getAttribute('class'))"
    )
    heights = {bar.get_attribute("height") for bar in bars(page).all()}
    assert classes == ["bar band-none"] * 60
    assert len(heights) == 1 and float(heights.pop()) > 0
    expect(page.locator(".minutely-summary")).to_have_text("Sem chuva prevista na próxima hora.")


def test_ca_031_rain_only_from_a_future_minute(page: Page, weather_api):
    """CA-031, RN-044: com chuva só a partir de um minuto futuro, o resumo dá o horário em que
    ela começa."""

    def dry_first_20(minutes):
        for minute in minutes[:20]:
            minute["precipitation"] = 0

    open_with(page, weather_api, minutely_view(dry_first_20))

    expect(page.locator(".minutely-summary")).to_have_text("Chuva prevista a partir de 17:02.")


def test_rf_043_summary_of_the_next_hour(page: Page, weather_api):
    """RF-043, RN-044: com chuva em todos os minutos (a captura), o resumo é "Chuva durante
    toda a próxima hora."; com chuva agora que para, dá o horário em que ela para."""
    open_with(page, weather_api)
    expect(page.locator(".minutely-summary")).to_have_text("Chuva durante toda a próxima hora.")

    def stops_at_1712(minutes):
        for minute in minutes[30:]:
            minute["precipitation"] = 0

    open_with(page, weather_api, minutely_view(stops_at_1712))
    expect(page.locator(".minutely-summary")).to_have_text(
        "Chuva agora, parando por volta de 17:12."
    )


# ---------- Cursor e teclado (T-10.3) ----------


def test_rf_044_cursor_shows_time_and_intensity(page: Page, weather_api, weather_views):
    """RF-044, RN-045: o cursor sobre uma barra mostra "HH:MM — X,XX mm/h" daquele minuto, e a
    dica some quando o cursor sai do gráfico."""
    minutes = weather_views["uberlandia"]["minutely"]
    open_with(page, weather_api)

    hover_minute(page, 20, 60)
    expect(tooltip(page)).to_be_visible()
    expect(tooltip(page)).to_have_text(minutes[20]["tooltip"])
    assert minutes[20]["tooltip"] == "17:02 — 0,38 mm/h"

    page.mouse.move(0, 0)
    expect(tooltip(page)).to_be_hidden()


def test_rnf_020_chart_is_one_tab_stop_and_arrows_announce_each_minute(
    page: Page, weather_api, weather_views
):
    """RNF-020, RF-044, P-023: o gráfico é um único elemento focável. As setas percorrem os
    minutos, e o valor de cada um é anunciado (`aria-valuetext`) e aparece na dica. Home e End
    vão para o primeiro e o último, sem dar a volta nas pontas."""
    minutes = weather_views["uberlandia"]["minutely"]
    open_with(page, weather_api)
    slider = chart(page)

    assert page.locator(".minutely [tabindex]").count() == 1
    slider.focus()
    expect(slider).to_have_attribute("aria-valuetext", minutes[0]["tooltip"])
    expect(tooltip(page)).to_have_text(minutes[0]["tooltip"])

    for key, index in [
        ("ArrowLeft", 0),
        ("ArrowRight", 1),
        ("ArrowRight", 2),
        ("ArrowLeft", 1),
        ("End", 59),
        ("ArrowRight", 59),
        ("Home", 0),
    ]:
        page.keyboard.press(key)
        expect(slider).to_have_attribute("aria-valuetext", minutes[index]["tooltip"])
        expect(slider).to_have_attribute("aria-valuenow", str(index))
        expect(tooltip(page)).to_have_text(minutes[index]["tooltip"])

    page.keyboard.press("Shift+Tab")
    expect(tooltip(page)).to_be_hidden()


def test_rnf_020_tab_reaches_the_chart(page: Page, weather_api):
    """RNF-020, P-023: o gráfico entra na ordem do Tab depois do bloco hora a hora e do mapa,
    na ordem do documento: o mapa, os botões de zoom e os links das atribuições (fatia 11)."""
    open_with(page, weather_api)
    page.locator(".hourly-point").first.focus()

    stops = []
    for _ in range(7):
        page.keyboard.press("Tab")
        stops.append(
            page.evaluate(
                "() => document.activeElement.getAttribute('aria-label') "
                "|| document.activeElement.textContent.trim()"
            )
        )

    assert stops[:-1] == [
        "Mapa de precipitação centrado em Uberlândia",
        "Aproximar",
        "Afastar",
        "OpenStreetMap",
        "CARTO",
        "OpenWeather",
    ]
    expect(chart(page)).to_be_focused()


# ---------- Indisponibilidade, escala e posição (T-10.4) ----------


def test_rf_045_unavailable_message_replaces_bars_legend_and_summary(page: Page, weather_api):
    """RF-045, CA-032, P-021: sem a previsão por minuto, o painel mostra só a mensagem, no lugar
    das barras, da legenda e do resumo, e os demais blocos continuam."""
    open_with(page, weather_api, view_of(_load("onecall_no_minutely.json")))

    panel = page.locator(".minutely")
    expect(panel).to_have_attribute("data-block-state", "unavailable")
    expect(panel.locator(".block-state")).to_have_text(
        "Previsão por minuto indisponível para esta localidade."
    )
    expect(panel.locator(".panel-title")).to_have_text(TITLE)
    for part in (".minutely-chart", ".minutely-summary", ".minutely-legend"):
        expect(panel.locator(part)).to_be_hidden()
    expect(page.locator("#map")).to_be_visible()
    expect(page.locator(".hourly")).to_have_attribute("data-block-state", "ready")


def test_rf_045_all_minutes_gone_is_unavailable(page: Page, weather_api):
    """RF-045, RN-047: se todos os minutos recebidos já passaram (dados em cache), o painel
    fica indisponível, em vez de vazio."""
    last = bundle("uberlandia")["minutely"][-1]["dt"]

    open_with(page, weather_api, at=last + 60)

    expect(page.locator(".minutely")).to_have_attribute("data-block-state", "unavailable")


def test_rn_046_panel_does_not_change_with_the_scale(page: Page, weather_api):
    """RN-046, RN-057, feature 5 (categoria 7): a intensidade é sempre em mm/h, e trocar a
    escala não muda nada no painel."""
    open_with(page, weather_api)

    def snapshot():
        drawn = bars(page).evaluate_all(
            "(nodes) => nodes.map((n) => `${n.getAttribute('class')} ${n.getAttribute('height')}`)"
        )
        text = page.locator(".minutely").inner_text()
        return text, chart(page).get_attribute("aria-valuetext"), drawn

    before = snapshot()
    group = page.get_by_role("group", name="Escala de temperatura")
    group.get_by_role("button", name="°F", exact=True).click()
    expect(group.get_by_role("button", name="°F", exact=True)).to_have_attribute(
        "aria-pressed", "true"
    )

    assert snapshot() == before
    assert before[1] == "16:42 — 0,56 mm/h"


@pytest.mark.parametrize("width", [360, 1280])
def test_p_024_minute_bars_fit_the_panel_without_scroll(page: Page, weather_api, width: int):
    """RNF-021, P-024, feature 5 (categoria 10): em qualquer largura, as 60 barras cabem no
    painel, mais finas na tela estreita, sem rolagem horizontal, e os marcos não se
    sobrepõem."""
    page.set_viewport_size({"width": width, "height": 900})
    open_with(page, weather_api)

    panel = page.locator(".minutely").bounding_box()
    box = page.locator(".minutely-bars").bounding_box()
    tiles = [mark.bounding_box() for mark in page.locator(".mark").all()]
    size = page.evaluate(
        "() => [document.documentElement.scrollWidth, document.documentElement.clientWidth]"
    )

    assert panel["x"] <= box["x"] and box["x"] + box["width"] <= panel["x"] + panel["width"]
    for left, right in pairwise(tiles):
        assert left["x"] + left["width"] <= right["x"]
    assert size[0] <= size[1]


# ---------- Contraste e leitura sem cor (T-10.5) ----------


def test_rnf_019_bar_colors_contrast_3_to_1_with_the_panel(page: Page, weather_api):
    """RNF-019, P-018: cada cor de faixa tem contraste de pelo menos 3:1 com o fundo do painel
    (WCAG 2.1, critério 1.4.11), e a legenda e o resumo dizem em texto o que as cores
    mostram."""
    open_with(page, weather_api, BANDS_VIEW)

    background = page.locator(".minutely").evaluate("(el) => getComputedStyle(el).backgroundColor")
    for index in (0, 1, 3, 5, 7):
        fill = bars(page).nth(index).evaluate("(el) => getComputedStyle(el).fill")
        assert contrast(fill, background) >= 3, (index, fill)
    expect(page.locator(".legend-item")).to_have_text(LEGEND)
    expect(page.locator(".minutely-summary")).to_have_text("Chuva prevista a partir de 16:43.")
