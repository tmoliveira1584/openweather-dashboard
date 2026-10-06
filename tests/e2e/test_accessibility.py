"""Acessibilidade e consistência da página inteira (fatia 12, T-12.5).

Os testes de cada feature já cobrem o teclado e os destaques de cada bloco. Aqui a página é
vista de uma vez: a ordem do Tab, uma jornada feita só pelo teclado, a cor nunca como único
meio, a unidade de cada valor, os textos em pt-BR e o mesmo formato para o mesmo tipo de
valor em todos os blocos.
"""

import re

from playwright.sync_api import Page, expect

from tests.e2e.clock import open_paused

# Paradas do Tab, na ordem da página, com a cidade padrão e o aviso de localização. As abas,
# a curva e o gráfico por minuto são uma parada cada: dentro deles, quem anda são as setas.
TAB_STOPS = [
    ".scale-option[data-scale='c']",
    ".scale-option[data-scale='f']",
    ".city",
    ".search-button",
    ".search-input",
    ".location-notice-close",
    ".day-tab[aria-selected='true']",
    ".hourly-point[tabindex='0']",
    "#map",
    ".leaflet-control-zoom-in",
    ".leaflet-control-zoom-out",
    ".map-attribution a >> nth=0",
    ".map-attribution a >> nth=1",
    ".map-attribution a >> nth=2",
    ".minutely-bars",
]

# Indicador de foco visível: o contorno do próprio elemento ou, nos pontos da curva, o da
# bolinha (seção 7.1).
FOCUS_RING_JS = """(node) => {
    const target = node.classList.contains('hourly-point')
        ? node.querySelector('.hourly-dot')
        : node;
    const style = getComputedStyle(target);
    return style.outlineStyle !== 'none' && parseFloat(style.outlineWidth) >= 2;
}"""

# Textos que não podem aparecer em inglês: os do Leaflet e os nomes comuns da interface.
ENGLISH = re.compile(
    r"\b(Loading|Error|Retry|Search|Zoom|Leaflet|Today|Tomorrow|Wind|Humidity|Pressure|"
    r"Visibility|Feels|Rain|Close|Next|Previous|the|and|of|in|out)\b"
)
TEXTS_JS = """() => {
    const clone = document.body.cloneNode(true);
    // A atribuição do mapa é o texto exigido pelos provedores (P-019, seção 7.2).
    clone.querySelectorAll('.map-attribution').forEach((node) => node.remove());
    const texts = [clone.textContent];
    for (const node of document.querySelectorAll('*')) {
        if (node.closest('.map-attribution')) continue;
        for (const name of ['aria-label', 'title', 'alt', 'placeholder', 'aria-valuetext']) {
            const value = node.getAttribute(name);
            if (value) texts.push(value);
        }
    }
    return texts.join(' | ');
}"""


def wait_ready(page: Page) -> None:
    expect(page.locator(".current")).to_have_attribute("data-block-state", "ready")


def open_page(page: Page) -> None:
    page.set_viewport_size({"width": 1280, "height": 900})
    page.goto("/")
    wait_ready(page)
    expect(page.locator(".map-attribution a")).to_have_count(3)


def focused_is(page: Page, selector: str) -> bool:
    return page.locator(selector).evaluate("(node) => node === document.activeElement")


def tab_to(page: Page, selector: str, key: str = "Tab") -> None:
    """Aperta Tab (ou `key`) até o foco chegar ao elemento, sem usar o mouse."""
    for _ in range(len(TAB_STOPS) + 2):
        page.keyboard.press(key)
        if focused_is(page, selector):
            return
    raise AssertionError(f"o Tab não chegou a {selector}")


def texts(page: Page, selector: str) -> list[str]:
    return page.locator(selector).all_text_contents()


def assert_all_match(values: list[str], pattern: str) -> None:
    assert values, f"nenhum valor para {pattern}"
    regex = re.compile(pattern)
    for value in values:
        assert regex.fullmatch(value), f"{value!r} fora do formato {pattern}"


# ---------- Teclado (P-023) ----------


def test_p_023_tab_reaches_every_control_in_order_with_a_visible_focus(page: Page, weather_api):
    """P-023, RNF-007, RNF-014, RNF-017, RNF-020, RF-049: o Tab passa por todos os controles da
    página, na ordem da tela, cada um com o indicador de foco visível; depois do último, o foco
    sai da página (sem armadilha) e o Shift+Tab faz o caminho de volta."""
    open_page(page)

    for selector in TAB_STOPS:
        page.keyboard.press("Tab")
        stop = page.locator(selector)
        assert focused_is(page, selector), f"esperava o foco em {selector}"
        assert stop.evaluate(FOCUS_RING_JS), f"foco sem indicador visível em {selector}"
        box = stop.bounding_box()
        assert box and box["width"] > 0 and box["height"] > 0
    page.keyboard.press("Tab")
    assert page.evaluate("document.activeElement === document.body")

    for selector in reversed(TAB_STOPS):
        page.keyboard.press("Shift+Tab")
        assert focused_is(page, selector), f"Shift+Tab: esperava o foco em {selector}"


def test_p_023_every_function_is_operated_by_keyboard_only(page: Page, weather_api, geo_api, tiles):
    """P-023: só com o teclado, o usuário fecha o aviso, troca a escala, busca e escolhe uma
    cidade, troca de aba, percorre as horas e os minutos e aproxima o mapa."""
    open_page(page)

    tab_to(page, ".location-notice-close")
    page.keyboard.press("Enter")
    expect(page.locator(".location-notice")).to_be_hidden()

    tab_to(page, ".scale-option[data-scale='f']", "Shift+Tab")
    page.keyboard.press("Enter")
    expect(page.locator(".scale-option[data-scale='f']")).to_have_attribute("aria-pressed", "true")

    tab_to(page, ".search-input")
    page.keyboard.type("Curitiba")
    page.keyboard.press("Enter")
    expect(page.get_by_role("option")).to_have_count(2)
    page.keyboard.press("ArrowDown")
    page.keyboard.press("Enter")
    expect(page.locator(".city-name")).to_have_text("Curitiba, BR")
    wait_ready(page)

    tab_to(page, ".day-tab[aria-selected='true']")
    page.keyboard.press("ArrowRight")
    page.keyboard.press("Enter")
    expect(page.locator(".day-tab").nth(1)).to_have_attribute("aria-selected", "true")

    tab_to(page, ".hourly-point[tabindex='0']")
    first_hour = page.locator(".hourly-point[tabindex='0']").get_attribute("aria-label")
    page.keyboard.press("ArrowRight")
    expect(page.locator(".hourly-point[tabindex='0']")).not_to_have_attribute(
        "aria-label", first_hour
    )

    tab_to(page, "#map")
    page.keyboard.press("+")
    expect(page.locator("#map img.leaflet-tile[src*='/voyager/7/']").first).to_be_attached()

    tab_to(page, ".minutely-bars")
    slider = page.locator(".minutely-bars")
    first_minute = slider.get_attribute("aria-valuetext")
    page.keyboard.press("ArrowRight")
    expect(slider).not_to_have_attribute("aria-valuetext", first_minute)


def test_p_023_retry_is_reached_and_pressed_by_keyboard(page: Page, weather_api):
    """P-023, RF-013: com a consulta falhando, "Tentar novamente" recebe o foco pelo Tab e
    consulta de novo com Enter."""
    weather_api.queue = [(502, "provider_unavailable")]
    open_paused(page)
    expect(page.locator(".current")).to_have_attribute("data-block-state", "error")

    tab_to(page, ".current .block-state-retry")
    page.keyboard.press("Enter")

    wait_ready(page)
    assert len(weather_api.urls) == 2


# ---------- Cor (P-018) ----------


def test_p_018_selected_tab_and_active_hour_are_not_shown_only_by_color(page: Page, weather_api):
    """P-018, RNF-014, RNF-017: a aba selecionada tem borda visível e temperatura em negrito,
    e o card da hora ativa (com o foco na curva) tem borda visível; os demais não têm borda
    (transparente)."""
    open_page(page)
    tab_to(page, ".hourly-point[tabindex='0']")

    def look(selector: str) -> dict:
        return page.locator(selector).first.evaluate(
            """(node) => {
                const style = getComputedStyle(node);
                const temp = node.querySelector('.day-tab-temp');
                return {
                    border: style.borderTopColor !== 'rgba(0, 0, 0, 0)'
                        && parseFloat(style.borderTopWidth) > 0,
                    bold: temp ? Number(getComputedStyle(temp).fontWeight) >= 700 : null,
                };
            }"""
        )

    assert look(".day-tab[aria-selected='true']") == {"border": True, "bold": True}
    assert look(".day-tab[aria-selected='false']") == {"border": False, "bold": False}
    assert look(".hour-card.is-active") == {"border": True, "bold": None}
    assert look(".hour-card:not(.is-active)") == {"border": False, "bold": None}


def test_p_018_rain_bands_and_states_are_also_told_in_text(page: Page, weather_api):
    """P-018, RF-042, RF-043, RNF-020: as faixas de chuva têm legenda em texto, um resumo em
    frase e o valor de cada minuto em texto; o selo de alertas diz a quantidade em texto."""
    open_page(page)

    expect(page.locator(".legend-item")).to_have_count(5)
    for item in texts(page, ".legend-item"):
        assert "mm/h" in item
    expect(page.locator(".minutely-summary")).not_to_be_empty()
    assert re.fullmatch(
        r"\d{2}:\d{2} — \d+,\d{2} mm/h",
        page.locator(".minutely-bars").get_attribute("aria-valuetext") or "",
    )
    expect(page.locator(".current-alerts")).to_have_text("3 alertas")


# ---------- Unidades (P-017) ----------


def test_p_017_every_value_has_an_identifiable_unit(page: Page, weather_api):
    """P-017, RN-014, RNF-012: cada valor numérico traz a unidade no texto, ou é temperatura
    com "°" e a escala identificada no seletor (`aria-pressed`). Vale nas duas escalas."""
    open_page(page)

    for scale, wind, dew in [("c", "m/s", "°C"), ("f", "mph", "°F")]:
        page.locator(f".scale-option[data-scale='{scale}']").click()
        expect(page.locator(f".scale-option[data-scale='{scale}']")).to_have_attribute(
            "aria-pressed", "true"
        )
        wind_text, humidity, visibility, pressure, uvi, dew_point = texts(page, ".indicator-value")
        assert wind_text.split()[1] == wind
        assert humidity.endswith("%")
        assert re.fullmatch(r"\d+(,\d+)? k?m", visibility)
        assert pressure.endswith(" hPa")
        assert uvi.endswith(" UV")
        assert dew_point.endswith(f" {dew}")
        for selector in (".current-temp", ".day-tab-temp", ".hour-temp"):
            assert_all_match(texts(page, selector), r"-?\d+°")
        assert_all_match(texts(page, ".hour-pop"), r"\d+%")
        assert_all_match(texts(page, ".rain-label"), r"\d+,\d{2} mm/h")


# ---------- Idioma (P-016) ----------


def test_p_016_all_interface_texts_are_in_portuguese(page: Page, weather_api):
    """P-016: a página declara `pt-BR`, e nenhum texto visível ou para leitores de tela (nomes,
    títulos, textos alternativos) está em inglês, nem os do Leaflet, nos estados de dados e de
    erro. A atribuição do mapa é o texto exigido pelos provedores (P-019)."""
    weather_api.queue = ["ok", (502, "provider_timeout")]
    open_page(page)
    expect(page.locator("html")).to_have_attribute("lang", "pt-BR")

    ready_texts = page.evaluate(TEXTS_JS)
    page.evaluate(
        """async () => (await import('/js/actions.js')).selectCity(
            { lat: 1, lon: 2, headerLabel: 'X', markerLabel: 'X', source: 'search' })"""
    )
    expect(page.locator(".current")).to_have_attribute("data-block-state", "error")
    error_texts = page.evaluate(TEXTS_JS)

    for text in (ready_texts, error_texts):
        assert not ENGLISH.findall(text), ENGLISH.findall(text)
    assert "Aproximar" in ready_texts and "Afastar" in ready_texts


# ---------- Formato (RNF-012) ----------


def test_rnf_012_same_value_type_has_the_same_format_in_all_blocks(page: Page, weather_api):
    """RNF-012, RN-014 a RN-025: temperaturas, horas, percentuais e volumes de chuva têm o
    mesmo formato em todos os blocos, sempre com vírgula decimal, e a máxima de um dia é a
    mesma na aba e no card."""
    open_page(page)

    for selector in (".current-temp", ".day-tab-temp", ".hour-temp"):
        assert_all_match(texts(page, selector), r"-?\d+°")
    assert_all_match(texts(page, ".current-feels-like"), r"Sensação de -?\d+°")
    assert_all_match(texts(page, ".current-time"), r"\d{2}:\d{2}")
    assert_all_match(texts(page, ".hour-label"), r"\d{2}:\d{2}( (Dom|Seg|Ter|Qua|Qui|Sex|Sáb))?")
    assert_all_match(texts(page, ".mark-time"), r"\d{2}:\d{2}")
    assert_all_match([texts(page, ".indicator-value")[1], *texts(page, ".hour-pop")], r"\d+%")
    minute = page.locator(".minutely-bars").get_attribute("aria-valuetext")
    assert_all_match([*texts(page, ".rain-label"), minute.split(" — ")[1]], r"\d+,\d{2} mm/h")
    dashboard = page.locator(".dashboard").text_content()
    assert not re.search(r"\d\.\d", dashboard), "número com ponto decimal"

    thursday = page.locator(".day-tab", has_text="Qui")
    tab_max = thursday.locator(".day-tab-temp").text_content()
    thursday.click()
    expect(page.locator(".current-temp")).to_have_text(tab_max)
    assert_all_match(texts(page, ".current-min"), r"Mín\. -?\d+°")
