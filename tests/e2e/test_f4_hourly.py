"""Feature 4, previsão hora a hora: cards, curva de temperatura, etiquetas de chuva, pontos
da curva pelo cursor e pelo teclado, indisponibilidade e troca de escala (fatia 9).

O relógio da página está no momento das capturas: segunda, 05/10/2026, 16:41 em Uberlândia
(ver a fixture `page`). Com a captura de Uberlândia, a janela vai das 16:00 de segunda às
15:00 de terça.
"""

import copy
import re
from itertools import pairwise

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.weather_api import bundle, view_of

# 08:18 de terça, 06/10/2026, em Uberlândia: o "Dado" dos CA-019 e CA-022.
AT_0818 = 1791255600 + 8 * 3600 + 18 * 60
# 13:00 de terça, 06/10/2026, em Uberlândia: a hora dos CA-023 e CA-024.
AT_1300 = 1791302400

LABELS_AT_CAPTURE = (
    [f"{h}:00" for h in range(16, 24)] + ["00:00 Ter"] + [f"{h:02d}:00" for h in range(1, 16)]
)
TEMPS_C = ["20°", "21°", "20°", "20°", "19°", "19°", "19°", "19°", "19°", "19°", "19°", "19°"]
TEMPS_C += ["19°", "19°", "18°", "19°", "20°", "22°", "24°", "24°", "25°", "27°", "29°", "28°"]
ALT_TEXT_C = "Nas próximas 24 horas, mínima de 18° às 06:00 e máxima de 29° às 14:00"
NUMBER = re.compile(r"-?\d+(?:\.\d+)?")


def hourly_view(change) -> dict:
    """`WeatherView` de Uberlândia com as horas da captura alteradas por `change(hours)`."""
    raw = copy.deepcopy(bundle("uberlandia"))
    change(raw["hourly"])
    return view_of(raw)


def hour_at(hours: list[dict], dt: int) -> dict:
    return next(hour for hour in hours if hour["dt"] == dt)


def open_with(page: Page, weather_api, view: dict | None = None, at: int | None = None):
    """Abre a página com a resposta `view` (ou a captura), com o relógio em `at` (ou no momento
    das capturas), e espera os dados."""
    if view is not None:
        weather_api.queue = [view]
    if at is not None:
        page.clock.set_system_time(at)
    page.goto("/")
    expect(page.locator(".hourly")).to_have_attribute("data-block-state", "ready")


def cards(page: Page):
    return page.locator(".hour-card")


def card(page: Page, label: str):
    return page.locator(".hour-card", has=page.locator(".hour-label", has_text=label))


def points(page: Page):
    return page.locator(".hourly-point")


def tooltip(page: Page):
    return page.locator(".hourly-tooltip")


def center_x(locator) -> float:
    box = locator.bounding_box()
    return box["x"] + box["width"] / 2


def boxes_of(locator) -> list[dict]:
    return [node.bounding_box() for node in locator.all()]


def curve_ys(page: Page) -> list[float]:
    """Coordenadas y do caminho da curva, inclusive as dos pontos de controle."""
    d = page.locator(".hourly-curve path").get_attribute("d")
    return [float(n) for n in NUMBER.findall(d)][1::2]


def choose_scale(page: Page, scale: str) -> None:
    group = page.get_by_role("group", name="Escala de temperatura")
    group.get_by_role("button", name=scale, exact=True).click()


def expect_no_page_scroll(page: Page) -> None:
    size = page.evaluate(
        "() => [document.documentElement.scrollWidth, document.documentElement.clientWidth]"
    )
    assert size[0] <= size[1]


# ---------- Cards (T-9.2) ----------


def test_ca_022_24_cards_from_the_hour_containing_now(page: Page, weather_api):
    """CA-022, RF-033, RN-034, RN-035: às 08:18, o primeiro card é "08:00", o último é "07:00"
    do dia seguinte e há 24 cards. A primeira hora do novo dia mostra o dia da semana."""
    open_with(page, weather_api, at=AT_0818)

    expect(cards(page)).to_have_count(24)
    labels = page.locator(".hour-label")
    expect(labels.first).to_have_text("08:00")
    expect(labels.last).to_have_text("07:00")
    expect(labels.nth(16)).to_have_text("00:00 Qua")


def test_rf_033_each_card_has_hour_icon_pop_and_temperature(page: Page, weather_api):
    """RF-033, RN-035, RN-036, RN-040, RNF-010, P-015: cada card tem a hora no fuso da
    cidade, o ícone com a descrição como texto alternativo, a chance de precipitação e a
    temperatura arredondada na escala ativa."""
    open_with(page, weather_api)

    expect(page.locator(".hour-label")).to_have_text(LABELS_AT_CAPTURE)
    expect(page.locator(".hour-temp")).to_have_text(TEMPS_C)
    first = cards(page).first
    expect(first.locator(".hour-pop")).to_have_text("100%")
    expect(first.locator(".hour-icon")).to_have_attribute("alt", "Chuva leve")
    expect(first.locator(".hour-icon")).to_have_attribute("src", re.compile(r"/10d@2x\.png$"))
    expect(card(page, "22:00").locator(".hour-pop")).to_have_text("0%")


def test_rf_033_hours_follow_the_city_timezone(page: Page, weather_api):
    """RF-033, RN-034, P-015, feature 4 (categoria 8): em Tóquio são 04:41 de terça, e a
    janela começa às 04:00 de lá, com o dia da semana na meia-noite seguinte."""
    open_with(page, weather_api, weather_api.views["tokyo"])

    labels = page.locator(".hour-label")
    expect(labels.first).to_have_text("04:00")
    expect(labels.nth(20)).to_have_text("00:00 Qua")
    expect(cards(page)).to_have_count(24)


def test_ca_023_card_shows_pop_percent_and_rounded_temperature(page: Page, weather_api):
    """CA-023, RN-036, RN-040: às 13:00, chance de 0,2 e 24,6 °C viram "20%" e "25°"."""

    def change(hours):
        hour_at(hours, AT_1300).update(pop=0.2, temp=24.6)

    open_with(page, weather_api, hourly_view(change))

    expect(card(page, "13:00").locator(".hour-pop")).to_have_text("20%")
    expect(card(page, "13:00").locator(".hour-temp")).to_have_text("25°")


def test_rf_033_missing_pop_and_temperature_show_dash(page: Page, weather_api):
    """RF-033, P-013, feature 4 (categoria 5): sem chance de precipitação ou sem temperatura
    numa hora, o card mostra "—", e o ponto da curva daquela hora não aparece."""

    def change(hours):
        del hours[2]["pop"]
        del hours[3]["temp"]

    open_with(page, weather_api, hourly_view(change))

    expect(card(page, "18:00").locator(".hour-pop")).to_have_text("—")
    expect(card(page, "19:00").locator(".hour-temp")).to_have_text("—")
    expect(points(page).nth(3).locator(".hourly-dot")).to_be_hidden()
    expect(points(page).nth(3)).to_have_attribute("aria-label", "19:00 · —")
    assert page.locator(".hourly-curve path").get_attribute("d").count("M") == 2


def test_rnf_010_icon_failure_keeps_pop_and_temperature(page: Page, weather_api):
    """RNF-010, feature 4 (categoria 9): se o ícone não carrega, o card mantém o texto
    alternativo com a descrição, e o percentual e a temperatura continuam visíveis."""
    page.route("**/img/wn/**", lambda route: route.abort())
    open_with(page, weather_api)

    first = cards(page).first
    expect(first.locator(".hour-icon")).to_have_attribute("alt", "Chuva leve")
    expect(first.locator(".hour-pop")).to_be_visible()
    expect(first.locator(".hour-temp")).to_be_visible()


@pytest.mark.parametrize("width", [360, 1280])
def test_rf_037_cards_scroll_horizontally_inside_the_block(page: Page, weather_api, width):
    """RF-037, P-024, feature 4 (categoria 10): os 24 cards não cabem na largura do bloco e
    rolam na horizontal dentro dele, junto com a curva, sem rolagem horizontal da página."""
    page.set_viewport_size({"width": width, "height": 800})
    open_with(page, weather_api)

    scroll = page.locator(".hourly-scroll")
    sizes = scroll.evaluate("(n) => [n.scrollWidth, n.clientWidth]")
    assert sizes[0] > sizes[1]
    expect_no_page_scroll(page)

    scroll.evaluate("(n) => { n.scrollLeft = n.scrollWidth; }")
    box = scroll.bounding_box()
    last = cards(page).last.bounding_box()
    assert last["x"] + last["width"] <= box["x"] + box["width"] + 1
    chart = page.locator(".hourly-chart").bounding_box()
    assert chart["x"] + chart["width"] == pytest.approx(last["x"] + last["width"] + 4, abs=1)


# ---------- Curva, etiquetas e pontos (T-9.3) ----------


def test_rf_034_curve_covers_the_same_hours_as_the_cards(page: Page, weather_api):
    """RF-034: a curva tem um ponto por card, e cada ponto fica alinhado ao centro do card da
    mesma hora."""
    open_with(page, weather_api)

    expect(points(page)).to_have_count(24)
    d = page.locator(".hourly-curve path").get_attribute("d")
    assert d.count("M") == 1 and d.count("C") == 23
    for index in (0, 1, 12, 23):
        point = points(page).nth(index)
        point.scroll_into_view_if_needed()
        assert center_x(point.locator(".hourly-dot")) == pytest.approx(
            center_x(cards(page).nth(index)), abs=1
        )


def test_rnf_016_curve_has_a_text_alternative(page: Page, weather_api):
    """RNF-016: a curva tem um texto alternativo com a mínima e a máxima das 24 horas."""
    open_with(page, weather_api)

    curve = page.get_by_role("img", name=ALT_TEXT_C)
    expect(curve).to_have_count(1)
    expect(curve).to_have_class(re.compile(r"\bhourly-curve\b"))


def test_rn_039_curve_goes_from_min_to_max_temperature(page: Page, weather_api):
    """RN-039: a máxima da janela (14:00) fica no topo da faixa da curva e a mínima (06:00),
    na base. A curva fica entre as duas e deixa folga para as etiquetas embaixo."""
    open_with(page, weather_api)

    ys = curve_ys(page)
    assert min(ys) == pytest.approx(25, abs=0.01)
    assert max(ys) == pytest.approx(75, abs=0.01)
    chart = page.locator(".hourly-chart").bounding_box()
    top = points(page).nth(22).locator(".hourly-dot").bounding_box()
    bottom = points(page).nth(14).locator(".hourly-dot").bounding_box()
    assert top["y"] + top["height"] / 2 == pytest.approx(chart["y"] + chart["height"] / 4, abs=1)
    assert bottom["y"] + bottom["height"] / 2 == pytest.approx(
        chart["y"] + chart["height"] * 3 / 4, abs=1
    )


def test_ca_026_equal_temperatures_draw_a_straight_line_in_the_center(page: Page, weather_api):
    """CA-026, RN-039, RNF-016: com temperaturas iguais nas 24 horas, a curva é uma linha
    reta no centro do bloco, os 24 cards aparecem, e o texto alternativo diz que a
    temperatura está estável."""

    def change(hours):
        for hour in hours:
            hour["temp"] = 22.0

    open_with(page, weather_api, hourly_view(change))

    expect(cards(page)).to_have_count(24)
    assert set(curve_ys(page)) == {50}
    chart = page.locator(".hourly-chart").bounding_box()
    dot = points(page).nth(5).locator(".hourly-dot").bounding_box()
    assert dot["y"] + dot["height"] / 2 == pytest.approx(chart["y"] + chart["height"] / 2, abs=1)
    expect(page.get_by_role("img", name="Nas próximas 24 horas, temperatura estável em 22°"))


def test_ca_024_single_rain_label_at_its_hour(page: Page, weather_api):
    """CA-024, RF-035, RN-037: com chuva de 0,21 só às 13:00, há uma única etiqueta, "0,21
    mm/h", na posição das 13:00."""

    def change(hours):
        for hour in hours:
            hour.pop("rain", None)
        hour_at(hours, AT_1300)["rain"] = {"1h": 0.21}

    open_with(page, weather_api, hourly_view(change))

    labels = page.locator(".rain-label:visible")
    expect(labels).to_have_count(1)
    expect(labels).to_have_text("0,21 mm/h")
    labels.scroll_into_view_if_needed()
    assert center_x(labels) == pytest.approx(center_x(card(page, "13:00")), abs=1)


def test_rn_037_tiny_or_missing_rain_has_no_label(page: Page, weather_api):
    """RN-037, feature 4 (categorias 5 e 6): volume que arredonda para 0,00 (0,004) ou
    ausente não gera etiqueta."""

    def change(hours):
        for hour in hours:
            hour.pop("rain", None)
        hours[0]["rain"] = {"1h": 0.004}

    open_with(page, weather_api, hourly_view(change))

    expect(page.locator(".rain-label")).to_have_count(0)


# Chuva em 9 horas seguidas, das 18:00 às 02:00 (os volumes da noite de terça da captura).
RAIN_IN_A_ROW = [0.68, 1.95, 10.49, 7.92, 9.49, 2.28, 4.22, 2.13, 0.45]


def rain_in_a_row(hours):
    for hour in hours:
        hour.pop("rain", None)
    for hour, volume in zip(hours[2:11], RAIN_IN_A_ROW, strict=True):
        hour["rain"] = {"1h": volume}


def expect_no_overlap(labels) -> None:
    boxes = sorted((box["x"], box["x"] + box["width"]) for box in boxes_of(labels))
    for (_, end), (start, _) in pairwise(boxes):
        assert end <= start


def test_rn_038_labels_of_neighbor_hours_fit_their_columns(page: Page, weather_api):
    """RN-038, RF-035, feature 4 (categoria 6): no tamanho padrão, a etiqueta de cada hora cabe
    na coluna dela. Com chuva em 9 horas seguidas, as 9 etiquetas aparecem, sem sobreposição,
    como no print."""
    open_with(page, weather_api, hourly_view(rain_in_a_row))

    visible = page.locator(".rain-label:visible")
    expect(visible).to_have_count(9)
    expect_no_overlap(visible)


def test_rn_038_overlapping_labels_show_the_largest_of_each_group(page: Page, weather_api):
    """RN-038, RF-036, feature 4 (categoria 6): quando as etiquetas ficariam sobrepostas (aqui,
    com a fonte delas ampliada, como pelo ajuste de fonte do navegador), elas são agrupadas.
    Nenhuma etiqueta visível fica sobre outra, a de maior volume aparece, e o volume de uma
    oculta aparece ao passar o cursor no ponto da hora."""
    weather_api.hold = True
    page.goto("/")
    page.add_style_tag(content=".rain-label { font-size: 18px; }")
    weather_api.release(0, hourly_view(rain_in_a_row))
    expect(page.locator(".hourly")).to_have_attribute("data-block-state", "ready")

    expect(page.locator(".rain-label")).to_have_count(9)
    visible = page.locator(".rain-label:visible")
    texts = visible.all_inner_texts()
    assert "10,49 mm/h" in texts and 1 < len(texts) < 9
    assert "7,92 mm/h" not in texts
    expect_no_overlap(visible)
    points(page).nth(5).hover()  # 21:00, com 7,92 mm/h
    expect(tooltip(page)).to_have_text("21:00 · 19° · 7,92 mm/h")


def test_rf_036_hover_shows_hour_temperature_and_rain(page: Page, weather_api):
    """RF-036: o cursor sobre um ponto mostra a hora, a temperatura e, se houver, o volume de
    chuva. Sem chuva, só a hora e a temperatura."""
    open_with(page, weather_api)
    expect(tooltip(page)).to_be_hidden()

    points(page).nth(0).hover()
    expect(tooltip(page)).to_have_text("16:00 · 20° · 0,66 mm/h")
    expect(points(page).nth(0).locator(".hourly-dot")).to_be_visible()

    points(page).nth(2).hover()
    expect(tooltip(page)).to_have_text("18:00 · 20°")
    page.locator(".hourly .panel-title").hover()
    expect(tooltip(page)).to_be_hidden()


def test_rnf_017_points_and_cards_are_traversed_by_keyboard(page: Page, weather_api):
    """RNF-017, RF-036, P-023: os pontos da curva ocupam uma só parada do Tab; as setas, Home
    e End percorrem as horas, mostrando a hora, a temperatura e a chuva de cada uma e
    rolando o bloco para trazer o ponto e o card da hora à vista. Cada ponto tem o mesmo
    texto como nome acessível."""
    page.set_viewport_size({"width": 360, "height": 800})
    open_with(page, weather_api)
    tabindex = points(page).evaluate_all("(ps) => ps.map((p) => p.tabIndex)")
    assert tabindex == [0] + [-1] * 23

    points(page).first.focus()
    expect(tooltip(page)).to_have_text("16:00 · 20° · 0,66 mm/h")
    page.keyboard.press("ArrowRight")
    expect(points(page).nth(1)).to_be_focused()
    expect(tooltip(page)).to_have_text("17:00 · 21° · 0,42 mm/h")
    expect(points(page).nth(1)).to_have_attribute("aria-label", "17:00 · 21° · 0,42 mm/h")

    page.keyboard.press("End")
    expect(points(page).last).to_be_focused()
    expect(tooltip(page)).to_have_text("15:00 · 28°")
    box = page.locator(".hourly-scroll").bounding_box()
    last = cards(page).last.bounding_box()
    assert box["x"] - 1 <= last["x"] and last["x"] + last["width"] <= box["x"] + box["width"] + 1
    expect(cards(page).last).to_have_class(re.compile(r"\bis-active\b"))

    page.keyboard.press("ArrowRight")  # já na última hora: fica nela
    expect(points(page).last).to_be_focused()
    page.keyboard.press("Home")
    expect(points(page).first).to_be_focused()
    page.keyboard.press("ArrowLeft")
    expect(points(page).first).to_be_focused()
    page.keyboard.press("Tab")
    expect(tooltip(page)).to_be_hidden()
    expect_no_page_scroll(page)


def test_rf_036_keyboard_wins_over_the_resting_cursor(page: Page, weather_api):
    """RF-036, RNF-017: com o cursor parado sobre a curva, ir à última hora pelo teclado rola
    o bloco por baixo do cursor, e a dica fica com o ponto focado. Mover o cursor de novo
    volta a dica para o ponto sob ele."""
    open_with(page, weather_api)
    points(page).nth(1).hover()
    expect(tooltip(page)).to_have_text("17:00 · 21° · 0,42 mm/h")

    points(page).first.focus()
    page.keyboard.press("End")

    expect(points(page).last).to_be_focused()
    page.wait_for_timeout(200)
    expect(tooltip(page)).to_have_text("15:00 · 28°")
    points(page).nth(20).hover()
    expect(tooltip(page)).to_have_text("12:00 · 25°")


# ---------- Indisponibilidade (T-9.4) ----------


def test_ca_025_without_hourly_forecast_only_the_message_appears(
    page: Page, load_json, weather_api
):
    """CA-025, RF-038, P-021: sem a previsão hora a hora, o bloco mostra só "Previsão hora a
    hora indisponível para esta cidade.", e os demais blocos aparecem normalmente."""
    weather_api.queue = [view_of(load_json("onecall_partial.json"))]
    page.goto("/")

    block = page.locator(".hourly")
    expect(block).to_have_attribute("data-block-state", "unavailable")
    expect(block.locator(".block-state")).to_have_text(
        "Previsão hora a hora indisponível para esta cidade."
    )
    expect(page.locator(".hourly-scroll")).to_be_hidden()
    expect(block.locator(".panel-title")).to_have_text("Previsão hora a hora")
    expect(page.locator(".current")).to_have_attribute("data-block-state", "ready")
    expect(page.locator(".current-temp")).to_have_text("21°")


UPDATE_WEATHER_JS = """async () => {
    const { getState, setState } = await import('/js/state.js');
    setState({ weather: structuredClone(getState().weather) });
}"""


def test_rn_034_new_hour_drops_the_hour_gone_from_cached_data(page: Page, weather_api):
    """RN-034, feature 4 (categoria 8): com os dados em cache, depois que uma nova hora
    começou, a janela começa na hora atual, e a hora que passou sai."""
    open_with(page, weather_api)

    page.clock.fast_forward("01:00:00")
    page.evaluate(UPDATE_WEATHER_JS)

    expect(page.locator(".hour-label").first).to_have_text("17:00")
    expect(cards(page)).to_have_count(24)
    assert len(weather_api.urls) == 1


def test_rf_038_all_hours_gone_shows_the_unavailable_message(page: Page, weather_api):
    """RF-038, RN-034: se todas as horas recebidas já passaram, o bloco mostra a mensagem de
    indisponibilidade, como sem a previsão hora a hora."""
    open_with(page, weather_api)

    page.clock.fast_forward("40:00:00")
    page.evaluate(UPDATE_WEATHER_JS)

    block = page.locator(".hourly")
    expect(block).to_have_attribute("data-block-state", "unavailable")
    expect(block.locator(".block-state")).to_have_text(
        "Previsão hora a hora indisponível para esta cidade."
    )


# ---------- Aba de dia, escala e consultas (T-9.5) ----------


def test_ca_019_another_day_tab_keeps_the_current_window(page: Page, weather_api):
    """CA-019, RF-029: com a aba "Qui" selecionada às 08:18, a previsão hora a hora continua
    começando em "08:00", sem nova consulta."""
    open_with(page, weather_api, at=AT_0818)

    page.locator(".day-tab", has_text="Qui").click()

    expect(page.locator(".current-time")).to_have_text("Qui, 08/10")
    expect(page.locator(".hour-label").first).to_have_text("08:00")
    expect(cards(page)).to_have_count(24)
    assert len(weather_api.urls) == 1


def test_rf_055_scale_change_converts_every_temperature_on_screen(page: Page, weather_api):
    """RF-055, RN-056, RN-057, RNF-018, P-011, P-014: ao escolher °F, as temperaturas dos
    cards, dos pontos da curva e do texto alternativo mudam junto com o card principal e as
    abas, e a curva mantém o desenho. Chance de precipitação e volume de chuva não mudam.
    Nenhuma consulta é feita, e voltar a °C devolve os valores iniciais."""
    open_with(page, weather_api)
    d_before = page.locator(".hourly-curve path").get_attribute("d")

    choose_scale(page, "°F")

    expect(page.locator(".hour-temp").first).to_have_text("69°")
    expect(page.locator(".hour-temp").nth(22)).to_have_text("83°")
    expect(page.locator(".current-temp")).to_have_text("69°")
    expect(page.locator(".day-tab-temp").first).to_have_text("72°")
    expect(page.get_by_role("img", name=re.compile("mínima de 65° às 06:00 e máxima de 83°")))
    expect(points(page).first).to_have_attribute("aria-label", "16:00 · 69° · 0,66 mm/h")
    expect(page.locator(".hour-pop").first).to_have_text("100%")
    expect(page.locator(".rain-label").first).to_have_text("0,66 mm/h")
    assert page.locator(".hourly-curve path").get_attribute("d") == d_before

    choose_scale(page, "°C")
    expect(page.locator(".hour-temp")).to_have_text(TEMPS_C)
    expect(page.get_by_role("img", name=ALT_TEXT_C)).to_have_count(1)
    page.wait_for_timeout(300)
    assert len(weather_api.urls) == 1


def test_rnf_018_hourly_appears_with_the_other_blocks_without_extra_query(page: Page, weather_api):
    """RNF-018: a curva e os cards aparecem junto com os demais blocos, com a mesma consulta
    de clima, sem outra consulta."""
    weather_api.hold = True
    page.goto("/")
    weather_api.release()

    expect(page.locator(".current")).to_have_attribute("data-block-state", "ready")
    states = page.evaluate(
        """() => ['.current', '.hourly'].map(
            (s) => document.querySelector(s).dataset.blockState)"""
    )
    assert states == ["ready", "ready"]
    expect(cards(page)).to_have_count(24)
    expect(points(page)).to_have_count(24)
    page.wait_for_timeout(300)
    assert len(weather_api.urls) == 1
