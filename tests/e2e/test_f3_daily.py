"""Feature 3, previsão diária: abas de dias, resumo do dia no card principal e nos
indicadores, selo de alertas por dia e volta para "Hoje" (fatia 8).

O relógio da página está no momento das capturas: segunda, 05/10/2026, 16:41 em Uberlândia
(ver a fixture `page`). Com a captura de Uberlândia, as abas são "Hoje" (segunda) e mais 7
dias, de terça a segunda, 12/10.
"""

import copy
import re

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.weather_api import bundle, view_of

LABELS = ["Hoje", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom", "Seg"]
MAX_C = ["22°", "28°", "31°", "34°", "35°", "36°", "32°", "32°"]
DESCRIPTIONS = [
    "Chuva moderada",
    "Chuva forte",
    "Chuva forte",
    "Céu limpo",
    "Céu limpo",
    "Algumas nuvens",
    "Nublado",
    "Chuva leve",
]
# Condições atuais da captura de Uberlândia, nos seis indicadores (aba "Hoje").
CURRENT_INDICATORS = ["6 m/s L", "94%", "10 km", "1017 hPa", "0 UV", "20 °C"]


def thursday_view(max_c: float, min_c: float) -> dict:
    """`WeatherView` de Uberlândia com a máxima e a mínima de quinta, 08/10, trocadas."""
    raw = copy.deepcopy(bundle("uberlandia"))
    thursday = raw["daily"][3]  # a captura começa na segunda, 05/10
    thursday["temp"] = {**thursday["temp"], "max": max_c, "min": min_c}
    return view_of(raw)


# CA-017: quinta, 08/10, com máxima de 35,2 °C e mínima de 21,4 °C.
CA_017_VIEW = thursday_view(35.2, 21.4)


def open_with(page: Page, weather_api, view: dict | None = None) -> None:
    """Abre a página com a resposta `view` (ou a captura de Uberlândia) e espera os dados."""
    if view is not None:
        weather_api.queue = [view]
    page.goto("/")
    expect(page.locator(".current")).to_have_attribute("data-block-state", "ready")


def tab(page: Page, label: str):
    return page.locator(".day-tab", has_text=label)


def expect_selected(page: Page, label: str) -> None:
    expect(page.locator('.day-tab[aria-selected="true"]')).to_have_count(1)
    expect(tab(page, label)).to_have_attribute("aria-selected", "true")


def indicator_values(page: Page):
    return page.locator(".indicator-value")


def choose_scale(page: Page, scale: str) -> None:
    group = page.get_by_role("group", name="Escala de temperatura")
    group.get_by_role("button", name=scale, exact=True).click()


def expect_current_conditions(page: Page) -> None:
    """Card principal e indicadores com as condições atuais da captura de Uberlândia."""
    expect(page.locator(".current-time")).to_have_text("16:41")
    expect(page.locator(".current-temp")).to_have_text("21°")
    expect(page.locator(".current-min")).to_be_hidden()
    expect(page.locator(".current-description")).to_have_text("Chuva leve")
    expect(page.locator(".current-feels-like")).to_have_text("Sensação de 21°")
    expect(page.locator(".current-alerts")).to_have_text("3 alertas")
    expect(page.locator(".current-card")).to_have_attribute("data-condition", "rain")
    expect(indicator_values(page)).to_have_text(CURRENT_INDICATORS)


# ---------- Abas (T-8.2) ----------


def test_ca_016_today_and_seven_tabs_with_weekday_max_and_icon(page: Page, weather_api):
    """CA-016, RF-024, RN-027, RN-028, RN-029, RNF-010: "Hoje" e mais 7 abas, com o dia da
    semana abreviado, a máxima arredondada e o ícone com a descrição como texto
    alternativo."""
    open_with(page, weather_api)

    tabs = page.get_by_role("tab")
    expect(tabs).to_have_count(8)
    expect(page.locator(".day-tab-label")).to_have_text(LABELS)
    expect(page.locator(".day-tab-temp")).to_have_text(MAX_C)
    icons = page.locator(".day-tab-icon")
    for index, description in enumerate(DESCRIPTIONS):
        expect(icons.nth(index)).to_have_attribute("alt", description)
        expect(icons.nth(index)).to_have_attribute("src", re.compile(r"/img/wn/\w+@2x\.png$"))


def test_rn_026_tabs_follow_the_city_timezone(page: Page, weather_api):
    """RN-026, RN-028, P-015, feature 3 (categoria 8): em Tóquio já é terça, 06/10. O dia
    05/10 da previsão é descartado, e "Hoje" é a terça, com mais 7 dias."""
    weather_api.queue = [weather_api.views["tokyo"]]
    open_with(page, weather_api)

    expect(page.locator(".day-tab-label")).to_have_text(
        ["Hoje", "Qua", "Qui", "Sex", "Sáb", "Dom", "Seg", "Ter"]
    )
    expect(page.locator(".day-tab-temp").first).to_have_text("28°")


def test_rf_025_today_starts_selected_and_highlighted_beyond_color(page: Page, weather_api):
    """RF-025, RNF-014, P-018: a página abre com "Hoje" selecionada, informada por
    `aria-selected` e destacada por borda e negrito, não só pela cor."""
    open_with(page, weather_api)

    expect_selected(page, "Hoje")
    styles = [
        tab(page, label).evaluate(
            "(n) => [getComputedStyle(n).fontWeight, getComputedStyle(n).borderTopColor]"
        )
        for label in ("Hoje", "Ter")
    ]
    (selected_weight, selected_border), (other_weight, other_border) = styles
    assert int(selected_weight) >= 700 > int(other_weight)
    assert selected_border != other_border


def test_rnf_014_tabs_are_operated_by_keyboard(page: Page, weather_api):
    """RNF-014, P-023: as setas movem o foco entre as abas (dando a volta nas pontas), Home e
    End vão para a primeira e a última, e o Enter seleciona. Só a aba selecionada entra na
    ordem do Tab."""
    open_with(page, weather_api)
    tab(page, "Hoje").focus()

    page.keyboard.press("ArrowRight")
    expect(tab(page, "Ter")).to_be_focused()
    expect_selected(page, "Hoje")  # a seta só move o foco
    page.keyboard.press("Enter")
    expect_selected(page, "Ter")
    expect(page.locator(".current-time")).to_have_text("Ter, 06/10")

    page.keyboard.press("ArrowLeft")
    page.keyboard.press("ArrowLeft")
    expect(tab(page, "Seg")).to_be_focused()
    page.keyboard.press("Home")
    expect(tab(page, "Hoje")).to_be_focused()
    page.keyboard.press("End")
    expect(tab(page, "Seg")).to_be_focused()

    tabindex = page.locator(".day-tab").evaluate_all("(tabs) => tabs.map((t) => t.tabIndex)")
    assert tabindex == [-1, 0, -1, -1, -1, -1, -1, -1]


def test_rf_032_selected_tab_is_scrolled_into_view_at_360px(page: Page, weather_api):
    """RF-032, RNF-015, P-024, feature 3 (categoria 10): em 360 px, as abas rolam na própria
    faixa, a aba selecionada pelo teclado é trazida para a área visível, e a página não rola
    na horizontal."""
    page.set_viewport_size({"width": 360, "height": 740})
    open_with(page, weather_api)
    tab(page, "Hoje").focus()

    page.keyboard.press("End")
    page.keyboard.press("Enter")

    expect_selected(page, "Seg")
    strip = page.locator(".day-tabs").bounding_box()
    last = tab(page, "Seg").bounding_box()
    assert last["x"] >= strip["x"] - 1
    assert last["x"] + last["width"] <= strip["x"] + strip["width"] + 1
    size = page.evaluate(
        "() => [document.documentElement.scrollWidth, document.documentElement.clientWidth]"
    )
    assert size[0] <= size[1]


def test_rf_024_tab_icon_failure_keeps_temperature(page: Page, weather_api):
    """RF-024, feature 3 (categoria 9): se o ícone de uma aba não carrega, a aba continua
    com a máxima visível e o ícone mantém o texto alternativo."""
    page.route("**/img/wn/**", lambda route: route.abort())
    open_with(page, weather_api)

    expect(tab(page, "Qui").locator(".day-tab-temp")).to_be_visible()
    expect(tab(page, "Qui").locator(".day-tab-icon")).to_have_attribute("alt", "Céu limpo")


def test_rf_024_without_daily_forecast_only_the_message_appears(page: Page, load_json, weather_api):
    """RF-024, P-021, feature 3 (categoria 5): sem previsão diária, a faixa mostra só
    "Previsão diária indisponível.", e o card continua com as condições atuais."""
    open_with(page, weather_api, view_of(load_json("onecall_partial.json")))

    strip = page.locator(".day-tabs")
    expect(strip).to_have_attribute("data-block-state", "unavailable")
    expect(strip.locator(".block-state")).to_have_text("Previsão diária indisponível.")
    expect(page.get_by_role("tab")).to_have_count(0)
    expect(page.locator(".current-temp")).to_have_text("21°")


# ---------- Resumo do dia (T-8.3) ----------


def test_ca_017_selected_day_summary_in_main_card_and_indicators(page: Page, weather_api):
    """CA-017, RF-026, RF-027, RN-030, RN-031, RN-033: em "Qui" (máxima de 35,2 °C e mínima
    de 21,4 °C), o card mostra "35°", "Mín. 21°", a descrição, a sensação diurna, a data no
    lugar da hora e a ilustração do dia; os indicadores mostram a previsão do dia, com "—"
    na visibilidade que a previsão não traz."""
    open_with(page, weather_api, CA_017_VIEW)

    tab(page, "Qui").click()

    expect_selected(page, "Qui")
    expect(page.locator(".current-temp")).to_have_text("35°")
    expect(page.locator(".current-min")).to_have_text("Mín. 21°")
    expect(page.locator(".current-description")).to_have_text("Céu limpo")
    expect(page.locator(".current-feels-like")).to_have_text("Sensação de 33°")
    expect(page.locator(".current-time")).to_have_text("Qui, 08/10")
    expect(page.locator(".current-card")).to_have_attribute("data-condition", "clear")
    expect(page.locator(".current-icon")).to_have_attribute("alt", "Céu limpo")
    expect(page.locator(".current-alerts")).to_be_hidden()
    expect(indicator_values(page)).to_have_text(
        ["5 m/s NE", "30%", "—", "1012 hPa", "14 UV", "13 °C"]
    )


def test_ca_018_today_brings_back_current_conditions(page: Page, weather_api):
    """CA-018, RF-028: com "Qui" selecionada, escolher "Hoje" volta a mostrar as condições
    atuais no card principal e nos indicadores."""
    open_with(page, weather_api)
    tab(page, "Qui").click()
    expect(page.locator(".current-time")).to_have_text("Qui, 08/10")

    tab(page, "Hoje").click()

    expect_selected(page, "Hoje")
    expect_current_conditions(page)


def test_ca_021_alerts_badge_counts_only_alerts_reaching_the_day(
    page: Page, load_json, weather_api
):
    """CA-021, RF-030, RN-032: com um alerta de quarta às 18:00 até quinta às 06:00
    (`onecall_alerts.json`), o selo mostra "1 alerta" em "Qua" e some em "Sex". Em "Hoje", o
    selo volta a contar os alertas atuais."""
    open_with(page, weather_api, view_of(load_json("onecall_alerts.json")))
    badge = page.locator(".current-alerts")

    tab(page, "Qua").click()
    expect(badge).to_have_text("1 alerta")
    tab(page, "Sex").click()
    expect(badge).to_be_hidden()
    tab(page, "Hoje").click()
    expect(badge).to_have_text("2 alertas")


def test_rnf_013_tab_switch_updates_within_100ms_without_query(page: Page, weather_api):
    """RNF-013, P-011, feature 3 (categoria 7): trocar de aba atualiza o card na hora (em até
    100 ms), sem consulta; na troca rápida entre várias abas, vale a última escolhida."""
    open_with(page, weather_api)

    elapsed = page.evaluate(
        """() => {
            const qui = [...document.querySelectorAll('.day-tab')]
                .find((t) => t.textContent.includes('Qui'));
            const start = performance.now();
            qui.click();
            const text = document.querySelector('.current-time').textContent;
            return [text, performance.now() - start];
        }"""
    )
    assert elapsed[0] == "Qui, 08/10"
    assert elapsed[1] < 100

    for label in ("Ter", "Sáb", "Qua", "Dom"):
        tab(page, label).click()
    expect_selected(page, "Dom")
    expect(page.locator(".current-time")).to_have_text("Dom, 11/10")
    page.wait_for_timeout(300)
    assert len(weather_api.urls) == 1


def test_rf_025_click_on_selected_tab_changes_nothing(page: Page, weather_api):
    """RF-025, feature 3 (categoria 7): clicar de novo na aba já selecionada não muda o
    estado nem faz consulta."""
    open_with(page, weather_api)
    tab(page, "Qui").click()
    page.evaluate(
        """async () => {
            const { subscribe } = await import('/js/state.js');
            window.stateChanges = 0;
            subscribe(() => { window.stateChanges += 1; });
        }"""
    )

    tab(page, "Qui").click()
    tab(page, "Qui").click()

    expect_selected(page, "Qui")
    assert page.evaluate("window.stateChanges") == 0
    assert len(weather_api.urls) == 1


# ---------- Troca de cidade, dados atualizados e escala (T-8.4) ----------


def test_ca_020_choosing_another_city_selects_today(page: Page, weather_api, geo_api):
    """CA-020, RF-031: com "Sex" selecionada, escolher outra cidade na busca volta para
    "Hoje", e o card mostra as condições atuais da nova cidade."""
    open_with(page, weather_api)
    tab(page, "Sex").click()
    expect_selected(page, "Sex")

    box = page.get_by_role("combobox", name="Buscar cidade")
    box.fill("Tóquio")
    box.press("Enter")

    expect(page.locator(".city-name")).to_have_text("Tóquio, JP")
    expect_selected(page, "Hoje")
    expect(page.locator(".current-time")).to_have_text("04:41")
    state = page.evaluate("async () => (await import('/js/state.js')).getState().selectedDay")
    assert state is None


def test_rn_026_selected_day_gone_by_midnight_returns_to_today(page: Page, weather_api):
    """RN-026, seção 7.4 (feature 3, categoria 8): com "Ter" selecionada, os dados em cache
    atravessam duas meias-noites da cidade. No tique seguinte do relógio, terça virou
    passado: "Hoje" passa a ser a quarta e a seleção volta para ela. Dos 10 dias da captura,
    ainda sobram 8, de quarta a quarta."""
    open_with(page, weather_api)
    tab(page, "Ter").click()

    page.clock.fast_forward("48:00:00")

    expect(page.locator(".day-tab-label")).to_have_text(
        ["Hoje", "Qui", "Sex", "Sáb", "Dom", "Seg", "Ter", "Qua"]
    )
    expect_selected(page, "Hoje")
    expect(page.locator(".current-time")).to_have_text("16:41")


def test_rf_057_selected_day_follows_the_active_scale(page: Page, weather_api):
    """RF-057, RF-055, RN-056: com °F ativo, o dia selecionado aparece em °F e mph, as abas
    mostram as máximas em °F, e trocar de aba mantém a escala."""
    open_with(page, weather_api, CA_017_VIEW)
    choose_scale(page, "°F")

    expect(page.locator(".day-tab-temp").first).to_have_text("72°")
    tab(page, "Qui").click()

    expect(page.locator(".current-temp")).to_have_text("95°")
    expect(page.locator(".current-min")).to_have_text("Mín. 71°")
    expect(page.locator(".current-feels-like")).to_have_text("Sensação de 91°")
    expect(indicator_values(page).first).to_have_text("12 mph NE")
    expect(indicator_values(page).last).to_have_text("56 °F")
    scale = page.evaluate("async () => (await import('/js/state.js')).getState().scale")
    assert scale == "f"


@pytest.mark.parametrize("label", ["Ter", "Dom"])
def test_rn_031_day_without_value_shows_dash(page: Page, weather_api, label: str):
    """RN-031, P-013: um valor que a previsão do dia não traz mostra "—" (a visibilidade em
    todos os dias da captura e o índice UV a partir de domingo)."""
    open_with(page, weather_api)

    tab(page, label).click()

    values = indicator_values(page)
    expect(values.nth(2)).to_have_text("—")  # Visibilidade
    expect(values.nth(4)).to_have_text("10 UV" if label == "Ter" else "—")  # Índice UV
