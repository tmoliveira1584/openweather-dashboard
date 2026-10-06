"""Privacidade da localização no navegador (fatia 12, T-12.4).

Cada teste usa a página como um usuário faria: localização autorizada (Tóquio, cidade
pública, P-006), busca e escolha de outra cidade, troca de escala e de aba e zoom no mapa.
Depois, confere o que ficou guardado no navegador e para onde foram as requisições.
"""

import re

from playwright.sync_api import Page, expect

from tests.e2e.location import allow_location

DEVICE = (35.6895, 139.6917)  # coordenada informada pelo navegador
# Partes da coordenada do dispositivo, com e sem o arredondamento a 2 casas.
COORDINATE_PARTS = ("35.6", "139.6")

STORED_JS = """async () => ({
    localStorage: localStorage.length,
    sessionStorage: sessionStorage.length,
    cookie: document.cookie,
    indexedDB: (await indexedDB.databases()).length,
    cacheStorage: (await caches.keys()).length,
    serviceWorkers: (await navigator.serviceWorker.getRegistrations()).length,
})"""
NOTHING_STORED = {
    "localStorage": 0,
    "sessionStorage": 0,
    "cookie": "",
    "indexedDB": 0,
    "cacheStorage": 0,
    "serviceWorkers": 0,
}


def wait_ready(page: Page) -> None:
    expect(page.locator(".current")).to_have_attribute("data-block-state", "ready")


def use_the_page(page: Page) -> None:
    """Abre com a localização autorizada e usa a busca, a escala, as abas e o mapa."""
    allow_location(page, *DEVICE)
    page.goto("/")
    expect(page.locator(".city-name")).to_have_text("Tóquio, JP")
    wait_ready(page)

    page.locator(".search-input").fill("Curitiba")
    page.locator(".search-input").press("Enter")
    page.get_by_role("option").first.click()
    expect(page.locator(".city-name")).to_have_text("Curitiba, BR")
    wait_ready(page)

    page.get_by_role("button", name="°F", exact=True).click()
    page.locator(".day-tab").nth(2).click()
    page.get_by_role("button", name="Aproximar").click()


def request_recorder(page: Page) -> list[str]:
    """URLs de todas as requisições da página, também as que o teste não deixa sair."""
    urls: list[str] = []
    page.on("request", lambda request: urls.append(request.url))
    return urls


def test_rnf_005_nothing_is_stored_on_the_device(page: Page, weather_api, geo_api, tiles):
    """RNF-005, P-007, RN-058: depois de usar a página, nada fica guardado no navegador:
    `localStorage`, `sessionStorage`, cookies, IndexedDB, Cache Storage e service workers
    continuam vazios."""
    use_the_page(page)

    assert page.evaluate(STORED_JS) == NOTHING_STORED
    assert page.context.cookies() == []


def test_p_007_reload_forgets_location_cache_and_search(page: Page, weather_api, geo_api, tiles):
    """P-007, feature 1 (categoria 8): recarregar a página recomeça do início, com novo pedido
    de localização, cache vazio (nova consulta da mesma coordenada), termo de busca em branco
    e °C."""
    use_the_page(page)
    page.locator(".search-input").fill("Santa")
    weather_before = len(weather_api.urls)
    reverse_before = len(geo_api.reverse_coords)

    page.reload()

    expect(page.locator(".city-name")).to_have_text("Tóquio, JP")
    wait_ready(page)
    assert len(geo_api.reverse_coords) == reverse_before + 1
    assert len(weather_api.urls) == weather_before + 1
    expect(page.locator(".search-input")).to_have_value("")
    expect(page.get_by_role("button", name="°C", exact=True)).to_have_attribute(
        "aria-pressed", "true"
    )
    assert page.evaluate(STORED_JS) == NOTHING_STORED


def test_p_008_requests_go_only_to_the_backend_carto_and_icons(
    page: Page, weather_api, geo_api, tiles, base_url
):
    """P-008, guardrail 2 e 3: as requisições da página vão só para o próprio servidor
    (arquivos da página e `/api`), para as tiles do CARTO e para os ícones do OpenWeatherMap.
    Nada vai direto ao OpenWeatherMap nem a outro serviço."""
    urls = request_recorder(page)
    use_the_page(page)

    allowed = re.compile(
        rf"^{re.escape(base_url)}/"
        r"|^https://[a-d]\.basemaps\.cartocdn\.com/rastertiles/voyager/"
        r"|^https://openweathermap\.org/img/wn/\w+@2x\.png$"
    )
    outside = [url for url in urls if not url.startswith("data:") and not allowed.match(url)]
    assert outside == []
    api = [url for url in urls if url.startswith(f"{base_url}/api/")]
    assert all(
        re.match(rf"{re.escape(base_url)}/api/(weather|geo/search|geo/reverse|tiles/)", url)
        for url in api
    )


def test_p_008_device_coordinates_go_only_to_weather_and_reverse(
    page: Page, weather_api, geo_api, tiles, base_url
):
    """P-008: a coordenada do dispositivo só vai para o `/api/weather` (arredondada a 2 casas)
    e para o `/api/geo/reverse`. As tiles do mapa levam só `z/x/y`."""
    urls = request_recorder(page)
    use_the_page(page)

    with_coords = {
        url.removeprefix(base_url).split("?")[0]
        for url in urls
        if any(part in url for part in COORDINATE_PARTS)
    }
    assert with_coords == {"/api/weather", "/api/geo/reverse"}
    assert weather_api.urls[0].endswith("/api/weather?lat=35.69&lon=139.69")
