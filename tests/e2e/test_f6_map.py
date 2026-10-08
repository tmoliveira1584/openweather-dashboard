"""Feature 6, mapa de precipitação: centro, marcador, zoom, camada de chuva, atribuições,
troca de cidade, falhas, teclado, toque e tiles da área visível (fatia 11).

As tiles do CARTO e da rota `/api/tiles/precipitation` são simuladas (`Tiles`), sem internet.
O zoom é lido das tiles do nível ativo, e o centro, pela posição do marcador: com o mapa
centrado na cidade, o marcador fica no centro do mapa.
"""

import math
import re

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.location import allow_location
from tests.e2e.tiles import CARTO_TILE, TILES_DONE_JS
from tests.e2e.weather_api import _load, view_of

UBERLANDIA = (-18.9186, -48.2772)
ATTRIBUTION = "© OpenStreetMap contributors © CARTO · Dados de precipitação © OpenWeather"
TILE_SIZE = 256

# Zoom do nível de tiles ativo: o Leaflet dá ao nível do zoom atual o maior z-index.
ZOOM_JS = """() => {
    const levels = [...document.querySelectorAll('#map .leaflet-tile-container')]
        .filter((level) => level.querySelector('img'));
    const top = levels.reduce((a, b) => (+b.style.zIndex > +a.style.zIndex ? b : a));
    return Number(top.querySelector('img').src.match(/\\/(\\d+)\\/\\d+\\/\\d+\\.png/)[1]);
}"""


def the_map(page: Page):
    return page.locator("#map")


def marker(page: Page):
    return page.locator("#map .map-marker")


def marker_label(page: Page):
    return page.locator("#map .map-marker-label")


def open_map(page: Page, width: int = 1280, height: int = 900) -> None:
    """Abre a página e espera o mapa terminar de carregar as tiles da vista inicial."""
    page.set_viewport_size({"width": width, "height": height})
    page.goto("/")
    expect(marker(page)).to_be_visible()
    wait_tiles(page)


def wait_tiles(page: Page) -> None:
    page.wait_for_function(TILES_DONE_JS)


def map_zoom(page: Page) -> int:
    return page.evaluate(ZOOM_JS)


def wait_zoom(page: Page, zoom: int) -> None:
    """Espera o zoom chegar a `zoom` e a animação terminar: durante ela, o Leaflet ignora um
    novo pedido de zoom. O estado precisa se manter por 3 leituras seguidas."""
    steady = 0
    for _ in range(100):
        animating = page.locator("#map .leaflet-zoom-anim").count()
        steady = steady + 1 if not animating and map_zoom(page) == zoom else 0
        if steady == 3:
            return
        page.wait_for_timeout(30)
    raise AssertionError(f"esperava o zoom {zoom}, ficou {map_zoom(page)}")


def wait_map_still(page: Page, moved_from: tuple[float, float] | None = None):
    """Espera o mapa parar: sem animação e com o marcador no mesmo lugar por 3 leituras.
    Com `moved_from`, espera antes o marcador sair dessa posição. Devolve a posição final."""
    last, steady = None, 0
    for _ in range(150):
        animating = page.locator("#map .leaflet-zoom-anim, #map .leaflet-pan-anim").count()
        offset = marker_offset(page)
        moved = moved_from is None or offset != pytest.approx(moved_from, abs=0.5)
        steady = steady + 1 if moved and not animating and offset == last else 0
        last = offset
        if steady == 3:
            return offset
        page.wait_for_timeout(30)
    raise AssertionError(f"o mapa não parou: marcador em {last}")


def marker_offset(page: Page) -> tuple[float, float]:
    """Distância do centro do marcador ao centro do mapa, em px."""
    box = the_map(page).bounding_box()
    dot = marker(page).bounding_box()
    return (
        dot["x"] + dot["width"] / 2 - (box["x"] + box["width"] / 2),
        dot["y"] + dot["height"] / 2 - (box["y"] + box["height"] / 2),
    )


def assert_centered(page: Page) -> None:
    dx, dy = marker_offset(page)
    assert abs(dx) <= 1.5 and abs(dy) <= 1.5, f"marcador fora do centro: {dx:.1f}, {dy:.1f}"


def drag_map(page: Page, dx: int, dy: int) -> None:
    """Arrasta o mapa com o mouse a partir de um ponto do alto, longe do painel por minuto."""
    box = the_map(page).bounding_box()
    x, y = box["x"] + box["width"] * 0.75, box["y"] + 80
    page.mouse.move(x, y)
    page.mouse.down()
    for step in range(1, 11):
        page.mouse.move(x + dx * step / 10, y + dy * step / 10)
    # A pausa antes de soltar evita a inércia do Leaflet, que levaria o mapa além do arrasto.
    page.wait_for_timeout(150)
    page.mouse.up()


def zoom_button(page: Page, name: str):
    return page.get_by_role("button", name=name, exact=True)


def boxes_overlap(a: dict, b: dict) -> bool:
    return (
        a["x"] < b["x"] + b["width"]
        and b["x"] < a["x"] + a["width"]
        and a["y"] < b["y"] + b["height"]
        and b["y"] < a["y"] + a["height"]
    )


def choose_curitiba(page: Page) -> None:
    box = page.get_by_role("combobox", name="Buscar cidade")
    box.fill("Curitiba")
    box.press("Enter")
    page.get_by_role("option", name="Curitiba, Paraná, BR").click()


def world_pixel(lat: float, lon: float, zoom: int) -> tuple[float, float]:
    """Posição do ponto no mundo em px, na projeção Web Mercator das tiles (EPSG:3857)."""
    scale = TILE_SIZE * 2**zoom
    sin_lat = math.sin(math.radians(lat))
    x = (lon + 180) / 360 * scale
    y = (0.5 - math.log((1 + sin_lat) / (1 - sin_lat)) / (4 * math.pi)) * scale
    return x, y


def tile_range(lat: float, lon: float, zoom: int, size: dict, margin: float, shift=(0, 0)) -> set:
    """Tiles que cobrem a área visível do mapa centrado em (lat, lon) e deslocado `shift` px,
    com `margin` px a mais (positivo) ou a menos (negativo) em cada borda."""
    cx, cy = world_pixel(lat, lon, zoom)
    cx, cy = cx + shift[0], cy + shift[1]
    left = cx - size["width"] / 2 - margin
    right = cx + size["width"] / 2 + margin
    top = cy - size["height"] / 2 - margin
    bottom = cy + size["height"] / 2 + margin
    xs = range(math.floor(left / TILE_SIZE), math.ceil(right / TILE_SIZE))
    ys = range(math.floor(top / TILE_SIZE), math.ceil(bottom / TILE_SIZE))
    return {(zoom, x, y) for x in xs for y in ys}


@pytest.fixture(autouse=True)
def _weather_ready(weather_api):
    """O `/api/weather` responde com a captura de Uberlândia (ou de Tóquio)."""


# ---------- Centro, marcador, camada de chuva e zoom (T-11.1) ----------


def test_ca_033_map_centered_on_uberlandia_with_marker_and_zoom_6(page: Page, tiles):
    """CA-033, RF-046, RN-048, RNF-024: com Uberlândia selecionada, o mapa fica centrado nela,
    com o marcador "Uberlândia", zoom 6 e a descrição em texto."""
    open_map(page)

    expect(marker_label(page)).to_have_text("Uberlândia")
    assert_centered(page)
    assert map_zoom(page) == 6
    assert {tile[0] for tile in tiles.base} == {6}
    expect(the_map(page)).to_have_attribute(
        "aria-label", "Mapa de precipitação centrado em Uberlândia"
    )
    expect(
        page.get_by_role("region", name="Mapa de precipitação centrado em Uberlândia")
    ).to_be_visible()


def test_rf_047_rain_layer_over_base_map_with_opacity_0_6(page: Page, tiles):
    """RF-047, RN-049: a camada de precipitação atual vem do proxy do backend e fica sobre o
    mapa base, semitransparente (opacidade 0,6)."""
    open_map(page)

    layers = page.locator("#map .leaflet-tile-pane > .leaflet-layer")
    expect(layers).to_have_count(2)
    base, rain = layers.nth(0), layers.nth(1)
    assert CARTO_TILE.search(base.locator("img").first.get_attribute("src"))
    assert rain.locator("img").first.get_attribute("src").startswith("/api/tiles/precipitation/6/")
    assert rain.evaluate("(layer) => getComputedStyle(layer).opacity") == "0.6"
    assert base.evaluate("(layer) => getComputedStyle(layer).opacity") == "1"
    assert set(tiles.rain) == set(tiles.base)


def test_rn_048_zoom_stops_at_3_and_10(page: Page, tiles):
    """RN-048, feature 6 (categoria 6): o zoom vai de 3 a 10. No limite, o botão fica
    desativado e mais cliques não mudam o zoom."""
    open_map(page)
    zoom_out, zoom_in = zoom_button(page, "Afastar"), zoom_button(page, "Aproximar")

    for zoom in (5, 4, 3):
        zoom_out.click()
        wait_zoom(page, zoom)
    expect(zoom_out).to_have_attribute("aria-disabled", "true")
    zoom_out.click(force=True)
    page.keyboard.press("Minus")
    page.wait_for_timeout(400)
    assert map_zoom(page) == 3

    for zoom in range(4, 11):
        zoom_in.click()
        wait_zoom(page, zoom)
    expect(zoom_in).to_have_attribute("aria-disabled", "true")
    zoom_in.click(force=True)
    page.wait_for_timeout(400)
    assert map_zoom(page) == 10
    assert min(tile[0] for tile in tiles.base) == 3
    assert max(tile[0] for tile in tiles.base) == 10


def test_rn_050_location_without_name_shows_sua_localizacao(page: Page, tiles, geo_api):
    """RN-050, feature 6 (categoria 8): sem nome na geocodificação reversa, o marcador mostra
    "Sua localização", nas coordenadas informadas pelo navegador."""
    geo_api.reverse_answer = []
    allow_location(page, -22.9035, -43.2096)

    open_map(page)

    expect(marker_label(page)).to_have_text("Sua localização")
    expect(the_map(page)).to_have_attribute(
        "aria-label", "Mapa de precipitação centrado em Sua localização"
    )
    assert_centered(page)
    assert tile_range(-22.9035, -43.2096, 6, the_map(page).bounding_box(), -2) <= set(tiles.base)


def test_p_003_marker_label_is_text_not_markup(page: Page, tiles, geo_api):
    """P-003, RN-050: o nome da cidade entra no rótulo do marcador como texto, nunca como
    marcação."""
    geo_api.answers["Ataque"] = [
        {"name": "<img src=x onerror=alert(1)>", "lat": -10.0, "lon": -50.0, "country": "BR"}
    ]
    open_map(page)

    box = page.get_by_role("combobox", name="Buscar cidade")
    box.fill("Ataque")
    box.press("Enter")

    expect(marker_label(page)).to_have_text("<img src=x onerror=alert(1)>")
    expect(marker_label(page).locator("img")).to_have_count(0)


# ---------- Atribuições (T-11.2) ----------


@pytest.mark.parametrize("width", [360, 599, 600, 1280])
def test_ca_038_attributions_visible_and_not_covered_by_minute_panel(page: Page, tiles, width):
    """CA-038, RF-050, RNF-025, P-019: as atribuições do mapa base e da camada de chuva ficam
    visíveis no canto inferior direito do mapa, sem o painel por minuto por cima."""
    open_map(page, width)

    attribution = page.locator("#map .map-attribution")
    expect(attribution).to_have_text(ATTRIBUTION)
    expect(attribution).to_be_visible()
    box = attribution.bounding_box()
    area = the_map(page).bounding_box()
    panel = page.locator(".minutely").bounding_box()

    assert box["x"] >= area["x"] and box["y"] >= area["y"]
    assert box["x"] + box["width"] <= area["x"] + area["width"] + 0.5
    assert box["y"] + box["height"] <= area["y"] + area["height"] + 0.5
    assert not boxes_overlap(box, panel), f"painel sobre a atribuição em {width} px"
    # Nada cobre a atribuição: o ponto do meio dela, já à vista, é dela mesma.
    attribution.scroll_into_view_if_needed()
    covered = attribution.evaluate(
        """(node) => {
            const box = node.getBoundingClientRect();
            const hit = document.elementFromPoint(box.x + box.width / 2, box.y + box.height / 2);
            return !node.contains(hit);
        }"""
    )
    assert not covered


def test_rf_050_attribution_links_to_each_provider(page: Page, tiles):
    """RF-050, P-019: cada provedor tem o link da sua atribuição, aberto em outra aba."""
    open_map(page)

    links = page.locator("#map .map-attribution a")
    expect(links).to_have_text(["OpenStreetMap", "CARTO", "OpenWeather"])
    hrefs = links.evaluate_all("(nodes) => nodes.map((node) => node.href)")
    assert hrefs == [
        "https://www.openstreetmap.org/copyright",
        "https://carto.com/attributions",
        "https://openweathermap.org/",
    ]
    for link in links.all():
        expect(link).to_have_attribute("target", "_blank")
        expect(link).to_have_attribute("rel", "noopener noreferrer")


# ---------- Troca de cidade e interação (T-11.3) ----------


def test_ca_034_selecting_curitiba_recenters_map_and_moves_marker(page: Page, tiles, geo_api):
    """CA-034, RF-048, feature 6 (categoria 7): depois de arrastar e aproximar o mapa, escolher
    Curitiba recentraliza o mapa nela, move o marcador e volta ao zoom inicial."""
    open_map(page)
    drag_map(page, -300, 120)
    zoom_button(page, "Aproximar").click()
    wait_zoom(page, 7)
    assert abs(marker_offset(page)[0]) > 100

    choose_curitiba(page)

    expect(marker_label(page)).to_have_text("Curitiba")
    expect(the_map(page)).to_have_attribute(
        "aria-label", "Mapa de precipitação centrado em Curitiba"
    )
    wait_zoom(page, 6)
    wait_tiles(page)
    assert_centered(page)
    curitiba = tile_range(-25.4295963, -49.2712724, 6, the_map(page).bounding_box(), -2)
    assert curitiba <= set(tiles.base)
    expect(marker(page)).to_have_count(1)


def test_ca_037_dragging_and_zooming_neither_queries_weather_nor_changes_city(
    page: Page, tiles, weather_api
):
    """CA-037, RN-051, feature 6 (categoria 7): arrastar e aproximar o mapa várias vezes, com
    o mouse, a roda e o teclado, não consulta o clima nem muda a cidade."""
    open_map(page)
    assert len(weather_api.urls) == 1

    drag_map(page, -200, 50)
    drag_map(page, 150, -100)
    zoom_button(page, "Aproximar").click()
    wait_zoom(page, 7)
    box = the_map(page).bounding_box()
    page.mouse.move(box["x"] + box["width"] * 0.75, box["y"] + 100)
    page.mouse.wheel(0, 300)
    the_map(page).focus()
    page.keyboard.press("ArrowLeft")
    page.keyboard.press("Equal")
    page.wait_for_timeout(500)

    assert len(weather_api.urls) == 1
    expect(page.locator(".city-name")).to_have_text("Uberlândia, BR")
    expect(marker_label(page)).to_have_text("Uberlândia")
    assert (
        page.evaluate("async () => (await import('/js/state.js')).getState().city.markerLabel")
        == "Uberlândia"
    )


def test_rn_051_scale_change_does_not_move_the_map(page: Page, tiles):
    """RN-051, P-011: trocar a escala não mexe no mapa arrastado nem no zoom."""
    open_map(page)
    drag_map(page, -200, 60)
    before = marker_offset(page)

    page.get_by_role("button", name="°F").click()
    expect(page.locator(".current-temp")).to_have_text("69°")
    page.wait_for_timeout(200)

    assert marker_offset(page) == pytest.approx(before, abs=0.5)
    assert map_zoom(page) == 6


# ---------- Falhas (T-11.4) ----------


def test_ca_035_rain_layer_failure_keeps_base_map_and_marker(page: Page, tiles):
    """CA-035, RF-052, feature 6 (categorias 3 e 4): com a camada de chuva falhando (cota
    excedida), o mapa base e o marcador continuam e aparece a faixa de aviso."""
    tiles.rain_fails = lambda tile: True
    open_map(page)

    banner = page.locator("#map .map-rain-unavailable")
    expect(banner).to_have_text("Camada de chuva indisponível no momento.")
    expect(banner).to_be_visible()
    expect(banner).to_have_attribute("role", "status")
    expect(marker(page)).to_be_visible()
    expect(marker_label(page)).to_have_text("Uberlândia")
    expect(
        page.locator("#map .leaflet-layer").first.locator("img.leaflet-tile-loaded")
    ).not_to_have_count(0)
    expect(page.locator("#map .map-unavailable")).to_be_hidden()
    expect(page.locator("#map .map-attribution")).to_be_visible()


def test_rf_052_rain_banner_leaves_after_a_load_without_errors(page: Page, tiles, geo_api):
    """RF-052: a faixa some no próximo carregamento da camada sem erro (aqui, ao trocar de
    cidade com o provedor de volta)."""
    tiles.rain_fails = lambda tile: True
    open_map(page)
    banner = page.locator("#map .map-rain-unavailable")
    expect(banner).to_be_visible()

    tiles.rain_fails = lambda tile: False
    choose_curitiba(page)

    expect(marker_label(page)).to_have_text("Curitiba")
    expect(banner).to_be_hidden()


def test_ca_032_without_minute_forecast_the_map_stays_visible(page: Page, tiles, weather_api):
    """CA-032, RF-045, P-021: sem a previsão por minuto, o painel mostra a mensagem de
    indisponibilidade e o mapa continua visível, com o marcador e as camadas."""
    weather_api.queue = [view_of(_load("onecall_no_minutely.json"))]
    open_map(page)

    expect(page.locator(".minutely .block-state")).to_have_text(
        "Previsão por minuto indisponível para esta localidade."
    )
    expect(the_map(page)).to_be_visible()
    expect(marker_label(page)).to_have_text("Uberlândia")
    assert_centered(page)
    assert tiles.base and tiles.rain
    expect(page.locator("#map .map-unavailable")).to_be_hidden()
    expect(page.locator("#map .map-attribution")).to_be_visible()


def test_ca_036_base_map_failure_shows_message_and_minute_panel_stays(page: Page, tiles):
    """CA-036, RF-051, P-021, feature 6 (categoria 4): com o mapa base fora do ar, o bloco
    mostra só a mensagem, e o painel por minuto e os demais blocos continuam."""
    tiles.base_fails = lambda tile: True
    page.set_viewport_size({"width": 1280, "height": 900})
    page.goto("/")

    message = page.locator("#map .map-unavailable")
    expect(message).to_have_text("Mapa indisponível no momento.")
    expect(message).to_be_visible()
    # A mensagem cobre o mapa inteiro: marcador, controles e camada de chuva.
    area = the_map(page).bounding_box()
    assert message.bounding_box() == pytest.approx(area, abs=0.5)
    expect(page.locator(".minutely")).to_have_attribute("data-block-state", "ready")
    expect(page.locator(".minutely-bars")).to_be_visible()
    panel = page.locator(".minutely").bounding_box()
    text = message.evaluate(
        """(node) => {
            const range = document.createRange();
            range.selectNodeContents(node);
            const box = range.getBoundingClientRect();
            return { x: box.x, y: box.y, width: box.width, height: box.height };
        }"""
    )
    assert not boxes_overlap(text, panel), "o painel por minuto cobre a mensagem"
    for block in (".current", ".hourly"):
        expect(page.locator(block)).to_have_attribute("data-block-state", "ready")


def test_f6_some_base_tiles_failing_leave_only_those_areas_blank(page: Page, tiles):
    """Feature 6 (categoria 9), RF-051: se só algumas partes do mapa base falham, o restante
    funciona, sem a mensagem de indisponibilidade."""
    tiles.base_fails = lambda tile: tile[1] % 2 == 0
    open_map(page)

    expect(marker(page)).to_be_visible()
    page.wait_for_timeout(200)
    expect(page.locator("#map .map-unavailable")).to_be_hidden()
    assert any(tile[1] % 2 == 0 for tile in tiles.base)


def test_p_021_weather_failure_does_not_affect_the_map(page: Page, tiles, weather_api):
    """P-021: com a consulta de clima falhando, o mapa continua centrado na cidade."""
    weather_api.queue = [(502, "provider_unavailable")]
    open_map(page)

    expect(page.locator(".current")).to_have_attribute("data-block-state", "error")
    expect(marker_label(page)).to_have_text("Uberlândia")
    assert_centered(page)
    expect(page.locator("#map .map-unavailable")).to_be_hidden()


def test_p_021_map_library_failure_leaves_other_blocks_working(page: Page, tiles):
    """P-021, RF-051: sem o Leaflet (o arquivo não carregou), o bloco do mapa mostra a
    mensagem e os demais blocos carregam normalmente."""
    page.route(re.compile(r"/vendor/leaflet-1\.9\.4/leaflet\.js$"), lambda route: route.abort())
    page.goto("/")

    expect(page.locator("#map .map-unavailable")).to_have_text("Mapa indisponível no momento.")
    expect(page.locator("#map .map-unavailable")).to_be_visible()
    expect(page.locator(".current")).to_have_attribute("data-block-state", "ready")
    expect(page.locator(".minutely")).to_have_attribute("data-block-state", "ready")
    assert tiles.base == []


# ---------- Mouse, teclado e toque (T-11.5) ----------


def test_rf_049_mouse_drags_and_zooms_the_map(page: Page, tiles):
    """RF-049: o mouse arrasta o mapa e aproxima pelos botões."""
    open_map(page)

    drag_map(page, -150, 60)
    dx, dy = marker_offset(page)
    assert dx == pytest.approx(-150, abs=2) and dy == pytest.approx(60, abs=2)

    zoom_button(page, "Aproximar").click()
    wait_zoom(page, 7)


def test_rf_049_keyboard_moves_and_zooms_the_map(page: Page, tiles):
    """RF-049, RNF-024, P-023: o mapa recebe o foco pelo Tab, as setas o movem, e + e − mudam
    o zoom. Os botões de zoom têm nomes em pt-BR e também são alcançados pelo teclado."""
    open_map(page)
    expect(the_map(page)).to_have_attribute("tabindex", "0")

    the_map(page).focus()
    start = marker_offset(page)
    page.keyboard.press("ArrowRight")
    dx, dy = wait_map_still(page, moved_from=start)
    assert dx == pytest.approx(-80, abs=2) and abs(dy) <= 1.5  # passo do teclado: 80 px

    page.keyboard.press("Equal")
    wait_zoom(page, 7)
    page.keyboard.press("Minus")
    wait_zoom(page, 6)

    zoom_in = zoom_button(page, "Aproximar")
    zoom_in.focus()
    page.keyboard.press("Enter")
    wait_zoom(page, 7)
    expect(zoom_button(page, "Afastar")).to_be_visible()


def touch(cdp, kind: str, points: list[tuple[float, float]]) -> None:
    cdp.send(
        "Input.dispatchTouchEvent",
        {
            "type": kind,
            "touchPoints": [{"x": x, "y": y, "id": i} for i, (x, y) in enumerate(points)],
        },
    )


@pytest.mark.browser_context_args(has_touch=True, is_mobile=True)
def test_rn_052_one_finger_scrolls_page_and_shows_hint(page: Page, tiles):
    """RN-052, feature 6 (categoria 10): numa tela de toque, um dedo sobre o mapa rola a
    página, não move o mapa, e a dica "Use dois dedos para mover o mapa." aparece por 1,5 s."""
    open_map(page, 390, 700)
    the_map(page).scroll_into_view_if_needed()
    before_scroll = page.evaluate("() => scrollY")
    before = marker_offset(page)
    box = the_map(page).bounding_box()
    x, y = box["x"] + box["width"] * 0.6, box["y"] + box["height"] * 0.7
    cdp = page.context.new_cdp_session(page)
    # Registra, no tempo da página, quando a dica aparece e quando some.
    page.evaluate(
        """() => {
            const hint = document.querySelector('#map .map-hint');
            window.hintTimes = [];
            new MutationObserver(() => window.hintTimes.push([hint.hidden, performance.now()]))
                .observe(hint, { attributes: true, attributeFilter: ['hidden'] });
        }"""
    )

    touch(cdp, "touchStart", [(x, y)])
    for step in range(1, 11):
        touch(cdp, "touchMove", [(x, y - 15 * step)])
    touch(cdp, "touchEnd", [])
    hint = page.locator("#map .map-hint")
    expect(hint).to_have_text("Use dois dedos para mover o mapa.")
    expect(hint).to_be_visible()

    page.wait_for_timeout(300)
    assert page.evaluate("() => scrollY") > before_scroll, "a página não rolou"
    assert marker_offset(page) == pytest.approx(before, abs=1), "um dedo moveu o mapa"
    expect(hint).to_be_hidden(timeout=3000)
    times = page.evaluate("window.hintTimes")
    assert [hidden for hidden, _ in times] == [False, True]
    # 1,5 s depois do último movimento; os movimentos do toque duram poucos ms.
    assert 1_450 <= times[1][1] - times[0][1] <= 1_800


@pytest.mark.browser_context_args(has_touch=True, is_mobile=True)
def test_rn_052_two_fingers_move_the_map(page: Page, tiles):
    """RN-052, RF-049: numa tela de toque, dois dedos movem o mapa, sem a dica."""
    open_map(page, 390, 700)
    the_map(page).scroll_into_view_if_needed()
    box = the_map(page).bounding_box()
    x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
    start = marker_offset(page)
    cdp = page.context.new_cdp_session(page)

    touch(cdp, "touchStart", [(x - 40, y)])
    touch(cdp, "touchStart", [(x - 40, y), (x + 40, y)])
    for step in range(1, 11):  # os dois dedos andam juntos 80 px à esquerda e 40 px abaixo
        dx, dy = -8 * step, 4 * step
        touch(cdp, "touchMove", [(x - 40 + dx, y + dy), (x + 40 + dx, y + dy)])
    touch(cdp, "touchEnd", [])

    dx, dy = wait_map_still(page, moved_from=start)
    assert dx == pytest.approx(-80, abs=8) and dy == pytest.approx(40, abs=8)
    expect(page.locator("#map .map-hint")).to_be_hidden()


def test_rn_052_mouse_screen_keeps_one_pointer_dragging(page: Page, tiles):
    """RN-052: sem tela de toque, o arrasto com o mouse continua ligado e a dica não aparece."""
    open_map(page)
    drag_map(page, -100, 0)

    assert marker_offset(page)[0] == pytest.approx(-100, abs=2)
    expect(page.locator("#map .map-hint")).to_be_hidden()


# ---------- Tiles da área visível (T-11.6) ----------


@pytest.mark.parametrize("width", [360, 1280])
def test_rnf_023_only_visible_tiles_are_requested(page: Page, tiles, width):
    """RNF-023: o mapa base e a camada de chuva pedem só as tiles da área visível, cada uma uma
    vez."""
    open_map(page, width)
    size = the_map(page).bounding_box()

    inner = tile_range(*UBERLANDIA, 6, size, margin=-1)
    visible = tile_range(*UBERLANDIA, 6, size, margin=1)
    assert inner <= set(tiles.base) <= visible
    assert set(tiles.rain) == set(tiles.base)
    assert len(tiles.base) == len(set(tiles.base)), "tile pedida mais de uma vez"


def test_rnf_023_dragging_requests_only_the_new_visible_tiles(page: Page, tiles):
    """RNF-023: depois de arrastar o mapa, só as tiles que entraram na área visível são
    pedidas."""
    open_map(page)
    size = the_map(page).bounding_box()
    before = set(tiles.base)
    tiles.base.clear()
    tiles.rain.clear()

    drag_map(page, -2 * TILE_SIZE, 0)  # a vista anda 512 px para o leste
    wait_tiles(page)

    shifted = tile_range(*UBERLANDIA, 6, size, margin=1, shift=(2 * TILE_SIZE, 0))
    new = set(tiles.base)
    assert new, "arrastar não pediu tiles novas"
    assert new <= shifted
    assert not new & before, "tile já carregada pedida de novo"
    assert set(tiles.rain) == new
