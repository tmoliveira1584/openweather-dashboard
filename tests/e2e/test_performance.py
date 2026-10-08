"""Desempenho e escala única (fatia 12, T-12.3).

Os tempos são medidos com o `/api` e as tiles simulados (decisão D-03): o tempo da rede e do
provedor real não entra na conta. O que se mede é o tempo da própria página, do momento em
que a cidade é definida (ou a escala é escolhida) até a tela mostrar o resultado.
"""

import time

from playwright.sync_api import Page, expect

from tests.e2e.tiles import TILES_DONE_JS
from tests.e2e.weather_api import TOKYO, UBERLANDIA

BLOCKS = [".day-tabs", ".current", ".hourly", ".minutely"]

# Escolhe a escala pelo clique e lê, na mesma tarefa, as temperaturas de todos os blocos.
SWITCH_SCALE_JS = """(scale) => {
    const button = document.querySelector(`.scale-option[data-scale="${scale}"]`);
    const texts = (selector) =>
        [...document.querySelectorAll(selector)].map((node) => node.textContent);
    const start = performance.now();
    button.click();
    const shown = {
        tabs: texts('.day-tab-temp'),
        current: texts('.current-temp'),
        feelsLike: texts('.current-feels-like'),
        indicators: texts('.indicator-value'),
        hours: texts('.hour-temp'),
    };
    return { elapsed: performance.now() - start, shown };
}"""


def expect_all_ready(page: Page, timeout: float) -> None:
    for selector in BLOCKS:
        expect(page.locator(selector)).to_have_attribute(
            "data-block-state", "ready", timeout=timeout
        )


def select_city(page: Page, city: dict) -> None:
    page.evaluate(
        "async (city) => { (await import('/js/actions.js')).selectCity(city); }",
        city,
    )


def test_rnf_001_blocks_appear_within_3s_after_the_city_is_defined(page: Page, weather_api):
    """RNF-001, RNF-018: com o provedor respondendo normalmente, todos os blocos de dados ficam
    visíveis em até 3 s depois que a cidade é definida, na abertura e numa cidade nova."""
    start = time.perf_counter()
    page.goto("/")
    expect_all_ready(page, timeout=3_000)
    assert time.perf_counter() - start < 3

    start = time.perf_counter()
    select_city(page, TOKYO)
    expect_all_ready(page, timeout=3_000)
    expect(page.locator(".city-name")).to_have_text("Tóquio, JP", timeout=3_000)
    assert time.perf_counter() - start < 3
    for content in [".day-tabs-list", ".indicators", ".hourly-scroll", ".minutely-bars"]:
        expect(page.locator(content)).to_be_visible()


def test_rnf_002_cached_city_appears_within_200ms_without_loading(page: Page, weather_api):
    """RNF-002, RN-010: os dados de uma cidade em cache aparecem em até 200 ms, sem que nenhum
    bloco passe pelo indicador de carregamento."""
    page.goto("/")
    expect_all_ready(page, timeout=5_000)
    select_city(page, TOKYO)
    expect(page.locator(".city-name")).to_have_text("Tóquio, JP")
    expect_all_ready(page, timeout=5_000)

    result = page.evaluate(
        """async (city) => {
            const { selectCity } = await import('/js/actions.js');
            const seen = [];
            const observer = new MutationObserver((records) => {
                for (const record of records) seen.push(record.target.dataset.blockState);
            });
            for (const block of document.querySelectorAll('[data-block-state]')) {
                observer.observe(block, { attributes: true, attributeFilter: ['data-block-state'] });
            }
            const start = performance.now();
            selectCity(city);
            const shown = [
                document.querySelector('.city-name').textContent,
                document.querySelector('.current-time').textContent,
            ];
            const elapsed = performance.now() - start;
            await new Promise((resolve) => setTimeout(resolve, 300));
            observer.disconnect();
            return { elapsed, shown, seen };
        }""",
        UBERLANDIA,
    )

    assert result["shown"] == ["Uberlândia, BR", "16:41"]
    assert result["elapsed"] < 200
    assert not {"loading", "slow"} & set(result["seen"])
    assert len(weather_api.urls) == 2


def test_rnf_022_map_and_rain_layer_appear_within_3s(page: Page, weather_api, tiles):
    """RNF-022: com os provedores respondendo normalmente, o mapa base e a camada de chuva
    aparecem em até 3 s."""
    start = time.perf_counter()
    page.goto("/")
    page.wait_for_function(TILES_DONE_JS, timeout=3_000)
    assert time.perf_counter() - start < 3
    assert tiles.base and tiles.rain


def test_rnf_022_map_loading_does_not_delay_the_other_blocks(page: Page, weather_api, tiles):
    """RNF-022, P-021: com as tiles do mapa ainda sem resposta, os demais blocos aparecem em
    até 3 s, como sem o mapa."""
    tiles.hold = True
    start = time.perf_counter()
    page.goto("/")

    expect_all_ready(page, timeout=3_000)
    assert time.perf_counter() - start < 3
    assert tiles.held
    assert not page.evaluate(TILES_DONE_JS)


def test_rnf_026_new_scale_in_all_blocks_within_100ms(page: Page, weather_api, weather_views):
    """RNF-026, RNF-029, RF-055: depois da escolha da escala, todos os blocos já mostram a nova
    escala em até 100 ms, e nenhum valor fica na escala anterior."""
    page.goto("/")
    expect_all_ready(page, timeout=5_000)
    view = weather_views["uberlandia"]

    for scale in ("f", "c"):
        result = page.evaluate(SWITCH_SCALE_JS, scale)

        assert result["elapsed"] < 100
        shown = result["shown"]
        assert shown["tabs"] == [day["max"][scale] for day in view["daily"][:8]]
        assert shown["current"] == [view["current"]["temp"][scale]]
        assert shown["feelsLike"] == [view["current"]["feels_like"][scale]]
        assert shown["hours"] == [hour["temp"][scale] for hour in view["hourly"][:24]]
        indicators = view["current"]["indicators"]
        assert shown["indicators"][0] == indicators["wind"][scale]
        assert shown["indicators"][5] == indicators["dew_point"][scale]


def test_rnf_029_all_blocks_always_use_the_same_scale(page: Page, weather_api, weather_views):
    """RNF-029, RN-056: em °F, nenhum bloco mostra °C nem m/s; de volta a °C, nenhum mostra
    °F nem mph. O seletor é o único lugar com as duas escalas. Os pontos da curva e o texto
    alternativo dela, que o RNF-026 não lê, também seguem a escala ativa."""
    page.goto("/")
    expect_all_ready(page, timeout=5_000)
    blocks_text = """() => [...document.querySelectorAll('.dashboard')]
        .map((node) => node.textContent).join(' ')"""

    for scale, absent in [("°F", ("°C", "m/s")), ("°C", ("°F", "mph"))]:
        page.get_by_role("button", name=scale, exact=True).click()
        text = page.evaluate(blocks_text)
        for unit in absent:
            assert unit not in text, f"{unit} visível com {scale} ativo"
        key = "f" if scale == "°F" else "c"
        hours = weather_views["uberlandia"]["hourly"][:24]
        labels = page.locator(".hourly-point").evaluate_all(
            "(nodes) => nodes.map((n) => n.getAttribute('aria-label'))"
        )
        assert [label.split(" · ")[1] for label in labels] == [h["temp"][key] for h in hours]
        low, high = ("65°", "83°") if key == "f" else ("18°", "29°")
        expect(page.locator(".hourly-curve")).to_have_attribute(
            "aria-label",
            f"Nas próximas 24 horas, mínima de {low} às 06:00 e máxima de {high} às 14:00",
        )
