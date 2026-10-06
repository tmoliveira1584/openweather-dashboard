"""Feature 2, condições atuais: card principal, ilustração por grupo de condição, seis
indicadores e a escala ativa nesses valores (fatia 7).

A página abre com a cidade padrão (Uberlândia). Os cenários dos critérios de aceite partem do
pacote real de Uberlândia com os campos de `current` trocados e passam pelo view model do
próprio backend (`view_of`), para que os textos testados sejam os que o backend gera.
"""

import base64
import copy

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.weather_api import bundle, view_of

# 08:18 em Uberlândia (UTC-3), como no exemplo da seção 6.3 da arquitetura.
DT_08_18 = 1791112680

# Um código de condição de cada grupo (RN-017). `None` = sem condição: imagem neutra.
GROUP_CODES = {
    "thunderstorm": 211,
    "rain": 501,
    "snow": 601,
    "mist": 741,
    "clear": 800,
    "clouds": 804,
    "neutral": None,
}

INDICATOR_LABELS = ["Vento", "Umidade", "Visibilidade", "Pressão", "Índice UV", "Ponto de orvalho"]

# Menor contraste do texto branco com os pixels do card, sem o texto (WCAG 2.1). A borda de
# 12 px fica de fora: nos cantos arredondados aparece o fundo branco do painel.
MIN_CONTRAST_JS = """async (png) => {
    const image = new Image();
    image.src = 'data:image/png;base64,' + png;
    await image.decode();
    const canvas = document.createElement('canvas');
    canvas.width = image.width;
    canvas.height = image.height;
    const context = canvas.getContext('2d');
    context.drawImage(image, 0, 0);
    const inset = 12;
    const { data } = context.getImageData(
        inset, inset, image.width - 2 * inset, image.height - 2 * inset);
    const linear = (v) => {
        const c = v / 255;
        return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
    };
    let brightest = 0;
    for (let i = 0; i < data.length; i += 4) {
        const luminance = 0.2126 * linear(data[i]) + 0.7152 * linear(data[i + 1])
            + 0.0722 * linear(data[i + 2]);
        brightest = Math.max(brightest, luminance);
    }
    return 1.05 / (brightest + 0.05);
}"""


def current_view(**fields) -> dict:
    """`WeatherView` de Uberlândia com os campos de `current` trocados. `None` retira o campo.
    `code` e `description` trocam a condição (`weather[0]`); `code=None` retira a condição."""
    raw = copy.deepcopy(bundle("uberlandia"))
    current = raw["current"]
    condition = current["weather"][0]
    if "code" in fields:
        code = fields.pop("code")
        if code is None:
            current.pop("weather")
        else:
            condition["id"] = code
    if "description" in fields:
        condition["description"] = fields.pop("description")
    for name, value in fields.items():
        if value is None:
            current.pop(name, None)
        else:
            current[name] = value
    return view_of(raw)


# Cenário dos CA-009, CA-012, CA-039, CA-040 e CA-042: 20,4 °C, sensação de 20,6 °C, 08:18 e
# vento de 4,2 m/s vindo de 95°.
CA_VIEW = current_view(temp=20.4, feels_like=20.6, dt=DT_08_18, wind_speed=4.2, wind_deg=95)


def open_with(page: Page, weather_api, view: dict | None = None) -> None:
    """Abre a página com a resposta `view` (ou a captura de Uberlândia) e espera o card."""
    if view is not None:
        weather_api.queue = [view]
    page.goto("/")
    expect(page.locator(".current")).to_have_attribute("data-block-state", "ready")


def card(page: Page):
    return page.locator(".current-card")


def indicator(page: Page, label: str):
    return page.locator(".indicator", has_text=label).locator(".indicator-value")


def choose_scale(page: Page, scale: str) -> None:
    group = page.get_by_role("group", name="Escala de temperatura")
    group.get_by_role("button", name=scale, exact=True).click()


def min_text_contrast(page: Page) -> float:
    """Contraste do texto branco com o pixel mais claro do card, com o texto escondido."""
    page.add_style_tag(content=".current-card > * { visibility: hidden !important; }")
    png = card(page).screenshot(animations="disabled")
    return page.evaluate(MIN_CONTRAST_JS, base64.b64encode(png).decode())


# ---------- Ilustrações (T-7.1) ----------


@pytest.mark.parametrize("group", GROUP_CODES)
def test_rf_017_each_condition_group_has_its_own_illustration(
    page: Page, weather_api, base_url, group: str
):
    """RF-017, RN-017, ADR-012: o card usa a ilustração SVG própria do grupo da condição, e o
    arquivo existe em /img/conditions/."""
    open_with(page, weather_api, current_view(code=GROUP_CODES[group]))

    expect(card(page)).to_have_attribute("data-condition", group)
    background = card(page).evaluate("(n) => getComputedStyle(n).backgroundImage")
    assert f"/img/conditions/{group}.svg" in background
    response = page.request.get(f"{base_url}/img/conditions/{group}.svg")
    assert response.status == 200
    assert response.headers["content-type"].startswith("image/svg+xml")


@pytest.mark.parametrize("group", GROUP_CODES)
def test_rnf_009_text_over_each_illustration_has_contrast_4_5(page: Page, weather_api, group: str):
    """RNF-009: com a camada escura sobre a ilustração, o texto branco tem contraste de pelo
    menos 4,5:1 com todos os pixels do card, em qualquer grupo."""
    open_with(page, weather_api, current_view(code=GROUP_CODES[group]))

    color = page.locator(".current-temp").evaluate("(n) => getComputedStyle(n).color")
    assert color == "rgb(255, 255, 255)"
    assert min_text_contrast(page) >= 4.5


def test_rnf_009_failed_illustration_leaves_neutral_background_with_readable_text(
    page: Page, weather_api
):
    """RNF-009, feature 2 (categoria 9): se a ilustração não carrega, o card fica com fundo de
    cor neutra e o texto continua legível."""
    page.route("**/img/conditions/*.svg", lambda route: route.abort())
    open_with(page, weather_api)

    expect(page.locator(".current-temp")).to_be_visible()
    background = card(page).evaluate("(n) => getComputedStyle(n).backgroundColor")
    assert background not in ("rgba(0, 0, 0, 0)", "transparent")
    assert min_text_contrast(page) >= 4.5


# ---------- Card principal (T-7.2) ----------


def test_ca_009_main_card_shows_temperature_feels_like_and_local_time(page: Page, weather_api):
    """CA-009, RF-016, RN-014, RN-015, RN-016: 20,4 °C, sensação de 20,6 °C e medição às
    08:18 locais aparecem como "20°", "Sensação de 21°" e "08:18", com a descrição."""
    open_with(page, weather_api, CA_VIEW)

    expect(page.locator(".current-temp")).to_have_text("20°")
    expect(page.locator(".current-feels-like")).to_have_text("Sensação de 21°")
    expect(page.locator(".current-time")).to_have_text("08:18")
    expect(page.locator(".current-description")).to_have_text("Chuva leve")


def test_rn_015_time_is_shown_in_the_city_timezone(page: Page, weather_api):
    """RN-015, P-015, feature 2 (categoria 8): Tóquio mostra a hora da medição no fuso de
    Tóquio (04:41), não no fuso do navegador."""
    weather_api.queue = [weather_api.views["tokyo"]]
    open_with(page, weather_api)

    expect(page.locator(".current-time")).to_have_text("04:41")


def test_ca_010_alerts_badge_shows_the_count_in_text(page: Page, weather_api):
    """CA-010, RF-018, RNF-010: com 3 alertas na resposta, o card mostra o selo "3 alertas",
    em texto e não só pela cor."""
    open_with(page, weather_api)

    badge = page.locator(".current-alerts")
    expect(badge).to_be_visible()
    expect(badge).to_have_text("3 alertas")


def test_ca_011_alerts_badge_is_hidden_without_alerts(page: Page, weather_api):
    """CA-011, RF-019: sem alertas na resposta (Tóquio), o selo não aparece."""
    weather_api.queue = [weather_api.views["tokyo"]]
    open_with(page, weather_api)

    expect(page.locator(".current-alerts")).to_be_hidden()


def test_rnf_010_condition_icon_has_the_description_as_alternative_text(page: Page, weather_api):
    """RNF-010: o ícone da condição é o do provedor e tem a descrição como texto alternativo."""
    open_with(page, weather_api)

    icon = page.locator(".current-icon")
    expect(icon).to_be_visible()
    expect(icon).to_have_attribute("alt", "Chuva leve")
    expect(icon).to_have_attribute("src", "https://openweathermap.org/img/wn/10d@2x.png")


def test_rf_023_missing_main_card_values_show_dash(page: Page, weather_api):
    """RF-023, P-013, feature 2 (categoria 5): sem temperatura, sensação e condição, o card
    mostra "—" no lugar dos valores, usa a imagem neutra e não mostra ícone."""
    open_with(page, weather_api, current_view(temp=None, feels_like=None, code=None))

    expect(page.locator(".current-temp")).to_have_text("—")
    expect(page.locator(".current-feels-like")).to_have_text("Sensação de —")
    expect(page.locator(".current-description")).to_have_text("—")
    expect(card(page)).to_have_attribute("data-condition", "neutral")
    expect(page.locator(".current-icon")).to_be_hidden()


def test_rf_016_long_description_wraps_without_being_cut(page: Page, weather_api):
    """RF-016, P-024, feature 2 (categoria 10): em 360 px, uma descrição longa quebra em até
    2 linhas, sem cortar o texto e sem rolagem horizontal da página."""
    page.set_viewport_size({"width": 360, "height": 740})
    open_with(page, weather_api, current_view(description="trovoada com chuva forte"))

    description = page.locator(".current-description")
    expect(description).to_have_text("Trovoada com chuva forte")
    size = description.evaluate(
        """(n) => ({
            lines: Math.round(n.getBoundingClientRect().height
                / parseFloat(getComputedStyle(n).lineHeight)),
            cut: n.scrollWidth > n.clientWidth || n.scrollHeight > n.clientHeight,
        })"""
    )
    assert not size["cut"]
    assert 1 <= size["lines"] <= 2
    page_size = page.evaluate(
        "() => [document.documentElement.scrollWidth, document.documentElement.clientWidth]"
    )
    assert page_size[0] <= page_size[1]


# ---------- Indicadores (T-7.3) ----------


def test_rf_020_six_indicators_with_labels_and_current_values(page: Page, weather_api):
    """RF-020, RN-020 a RN-024: seis cards, na ordem do spec, com os rótulos e os valores
    atuais da captura de Uberlândia."""
    open_with(page, weather_api)

    expect(page.locator(".indicator-label")).to_have_text(INDICATOR_LABELS)
    expect(page.locator(".indicator-value")).to_have_text(
        ["6 m/s L", "94%", "10 km", "1017 hPa", "0 UV", "20 °C"]
    )


def test_ca_012_wind_shows_speed_and_cardinal_point(page: Page, weather_api):
    """CA-012, RF-021, RN-019: vento de 4,2 m/s vindo de 95°, em °C, aparece como "4 m/s L"."""
    open_with(page, weather_api, CA_VIEW)

    expect(indicator(page, "Vento")).to_have_text("4 m/s L")


def test_rf_022_wind_below_half_meter_per_second_shows_calm(page: Page, weather_api):
    """RF-022, RN-019: vento de 0,3 m/s aparece como "Calmo", sem velocidade nem direção, nas
    duas escalas."""
    open_with(page, weather_api, current_view(wind_speed=0.3, wind_deg=95))

    expect(indicator(page, "Vento")).to_have_text("Calmo")
    choose_scale(page, "°F")
    expect(indicator(page, "Vento")).to_have_text("Calmo")


def test_ca_013_visibility_in_km_with_decimal_comma(page: Page, weather_api):
    """CA-013, RN-021, RN-025: visibilidade de 2.500 m aparece como "2,5 km"."""
    open_with(page, weather_api, current_view(visibility=2500))

    expect(indicator(page, "Visibilidade")).to_have_text("2,5 km")


def test_ca_014_missing_indicator_shows_dash_and_others_stay(page: Page, load_json, weather_api):
    """CA-014, RF-023, P-013: sem visibilidade, ponto de orvalho e direção do vento
    (`onecall_partial.json`), os cards mostram "—" e só a velocidade, e os demais aparecem
    normalmente."""
    open_with(page, weather_api, view_of(load_json("onecall_partial.json")))

    expect(page.locator(".indicator-value")).to_have_text(
        ["6 m/s", "94%", "—", "1017 hPa", "0 UV", "—"]
    )


# ---------- Escala ativa (T-7.4) ----------


def test_ca_039_fahrenheit_converts_main_card_without_querying(page: Page, weather_api):
    """CA-039, RF-055, RN-053, RN-055, P-011: 20,4 °C em °F aparece como "69°", com a
    sensação e o ponto de orvalho também em °F, e nenhuma consulta é feita."""
    open_with(page, weather_api, CA_VIEW)

    choose_scale(page, "°F")

    expect(page.locator(".current-temp")).to_have_text("69°")
    expect(page.locator(".current-feels-like")).to_have_text("Sensação de 69°")
    expect(indicator(page, "Ponto de orvalho")).to_have_text("67 °F")
    page.wait_for_timeout(300)
    assert len(weather_api.urls) == 1


def test_ca_040_wind_in_mph_with_fahrenheit(page: Page, weather_api):
    """CA-040, RF-056: vento de 4,2 m/s em °F aparece como "9 mph" (com a direção), e volta a
    m/s em °C."""
    open_with(page, weather_api, CA_VIEW)

    choose_scale(page, "°F")
    expect(indicator(page, "Vento")).to_have_text("9 mph L")
    choose_scale(page, "°C")
    expect(indicator(page, "Vento")).to_have_text("4 m/s L")


def test_ca_041_new_city_appears_in_fahrenheit_and_mph(page: Page, weather_api, geo_api):
    """CA-041, RF-058, RF-057: com °F ativo, a cidade escolhida na busca (Tóquio) aparece já
    em °F e mph."""
    open_with(page, weather_api)
    choose_scale(page, "°F")

    box = page.get_by_role("combobox", name="Buscar cidade")
    box.fill("Tóquio")
    box.press("Enter")  # um único resultado: a cidade é escolhida sem abrir a lista

    expect(page.locator(".city-name")).to_have_text("Tóquio, JP")
    expect(page.locator(".current-time")).to_have_text("04:41")
    expect(page.locator(".current-temp")).to_have_text("68°")
    expect(page.locator(".current-feels-like")).to_have_text("Sensação de 69°")
    expect(indicator(page, "Vento")).to_have_text("10 mph N")
    expect(indicator(page, "Ponto de orvalho")).to_have_text("66 °F")


def test_rf_058_scale_chosen_while_loading_applies_to_arriving_data(page: Page, weather_api):
    """RF-058, feature 7 (categoria 7): escolher °F durante o carregamento faz os dados
    chegarem já em °F, sem consulta adicional."""
    weather_api.hold = True
    page.goto("/")
    expect(page.locator(".current")).to_have_attribute("data-block-state", "loading")

    choose_scale(page, "°F")
    weather_api.release(0, CA_VIEW)

    expect(page.locator(".current-temp")).to_have_text("69°")
    expect(indicator(page, "Vento")).to_have_text("9 mph L")
    assert len(weather_api.urls) == 1


def test_ca_042_toggling_ten_times_returns_to_the_original_value(page: Page, weather_api):
    """CA-042, RN-055, P-014: alternar a escala 10 vezes e terminar em °C mostra "20°" de
    novo, sem erro acumulado."""
    open_with(page, weather_api, CA_VIEW)

    for scale in ["°F", "°C"] * 5:
        choose_scale(page, scale)

    expect(page.locator(".current-temp")).to_have_text("20°")
    expect(page.locator(".current-feels-like")).to_have_text("Sensação de 21°")


def test_ca_043_values_without_temperature_do_not_change(page: Page, weather_api):
    """CA-043, RN-057: umidade de 94%, pressão de 1015 hPa e visibilidade de 10 km não mudam
    em °F, assim como o índice UV."""
    open_with(page, weather_api, current_view(pressure=1015))
    unchanged = ["Umidade", "Visibilidade", "Pressão", "Índice UV"]
    expected = ["94%", "10 km", "1015 hPa", "0 UV"]

    choose_scale(page, "°F")

    for label, value in zip(unchanged, expected, strict=True):
        expect(indicator(page, label)).to_have_text(value)
