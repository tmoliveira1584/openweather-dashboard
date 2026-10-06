"""Feature 1, localização inicial e cidade padrão: pedido de localização, prazo de 10 s,
localização tardia, aviso de localização e geocodificação reversa.

Sem permissão concedida, o Chrome do Playwright nega a localização na hora (permissão negada).
Com `allow_location`, ele informa a coordenada na hora (permissão autorizada). Para o usuário
que não responde e para a localização tardia, a página usa a geolocalização falsa de
`location.py`, com o tempo controlado por `page.clock`. O `/api/weather` e o `/api/geo/*` são
simulados com `page.route` (ver `weather_api.py` e `geo_api.py`).
"""

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.clock import open_paused
from tests.e2e.location import FakeGeolocation, allow_location, remove_geolocation

NOTICE = (
    "Não foi possível usar sua localização. Mostrando Uberlândia, BR. "
    "Use a busca para escolher outra cidade."
)
# Coordenada do dispositivo nos testes: uma cidade pública, nunca a de alguém (P-006).
TOKYO_DEVICE = (35.6895, 139.6917)
TOKYO_QUERY = "lat=35.69&lon=139.69"
DEFAULT_QUERY = "lat=-18.92&lon=-48.28"
SEARCHED_TOKYO_QUERY = "lat=35.68&lon=139.76"  # Tóquio da busca (geo_api.TOKYO)


def city_name(page: Page):
    return page.locator(".city-name")


def notice(page: Page):
    return page.locator(".location-notice")


def search_box(page: Page):
    return page.get_by_role("combobox", name="Buscar cidade")


def search_and_choose(page: Page, term: str, option: str | None = None) -> None:
    """Busca o termo e, se a lista abrir, escolhe a opção."""
    search_box(page).fill(term)
    search_box(page).press("Enter")
    if option:
        page.get_by_role("option", name=option).click()


def expect_default_city_with_notice(page: Page, weather_api) -> None:
    expect(city_name(page)).to_have_text("Uberlândia, BR")
    expect(notice(page)).to_be_visible()
    expect(notice(page).locator(".location-notice-text")).to_have_text(NOTICE)
    expect(page.locator(".current")).to_have_attribute("data-block-state", "ready")
    assert [DEFAULT_QUERY in url for url in weather_api.urls] == [True]


def selected_city(page: Page) -> dict:
    return page.evaluate("async () => (await import('/js/state.js')).getState().city")


# ---------- Pedido de localização (T-6c.1) ----------


def test_rf_001_page_asks_browser_for_location_once_on_open(page: Page, weather_api):
    """RF-001, P-005: ao abrir, a página pede a localização uma vez, pelo pedido de permissão
    do navegador, com as opções da seção 7.4 (sem a opção `timeout`, que não conta o tempo da
    permissão). Enquanto não há resposta, nenhuma consulta de clima é feita."""
    geo = FakeGeolocation(page)
    open_paused(page)

    assert geo.calls() == [{"enableHighAccuracy": False, "maximumAge": 600000}]
    assert weather_api.urls == []


def test_p_005_browser_without_geolocation_uses_default_city(page: Page, weather_api):
    """P-005, RF-003: sem o recurso de localização no navegador, a localização não vem de
    nenhuma outra fonte: a cidade padrão entra com o aviso, como na permissão negada."""
    remove_geolocation(page)
    page.goto("/")

    expect_default_city_with_notice(page, weather_api)


# ---------- Localização obtida ou não (T-6c.2) ----------


def test_ca_001_allowed_location_shows_city_name_and_its_weather(page: Page, weather_api, geo_api):
    """CA-001, RF-002: com a localização autorizada, a coordenada vira a cidade selecionada, o
    nome vem da geocodificação reversa e os blocos mostram os dados dessa cidade, sem aviso."""
    allow_location(page, *TOKYO_DEVICE)
    page.goto("/")

    expect(city_name(page)).to_have_text("Tóquio, JP")
    expect(page.locator(".current")).to_have_attribute("data-block-state", "ready")
    expect(notice(page)).to_be_hidden()
    assert geo_api.reverse_coords == [("35.6895", "139.6917")]
    assert [TOKYO_QUERY in url for url in weather_api.urls] == [True]
    city = selected_city(page)
    assert (city["lat"], city["lon"], city["source"]) == (*TOKYO_DEVICE, "geolocation")


def test_ca_002_denied_location_shows_default_city_with_notice(page: Page, weather_api, geo_api):
    """CA-002, RF-003, RN-001: com a localização negada, o dashboard mostra Uberlândia, BR
    (lat -18.9186, lon -48.2772) e o aviso de localização. Não há geocodificação reversa."""
    page.goto("/")

    expect_default_city_with_notice(page, weather_api)
    assert geo_api.reverse_coords == []
    city = selected_city(page)
    assert (city["lat"], city["lon"], city["source"]) == (-18.9186, -48.2772, "default")


def test_ca_003_no_answer_in_10_seconds_shows_default_city_with_notice(page: Page, weather_api):
    """CA-003, RN-002: sem resposta ao pedido, a cidade padrão entra com o aviso quando passam
    10 s, contados a partir do pedido, e não antes."""
    FakeGeolocation(page)
    open_paused(page)

    page.clock.run_for(9_999)
    expect(city_name(page)).to_have_text("")
    expect(notice(page)).to_be_hidden()
    assert weather_api.urls == []

    page.clock.run_for(1)
    expect_default_city_with_notice(page, weather_api)


@pytest.mark.parametrize(
    "answer",
    [(502, "provider_unavailable"), []],
    ids=["falha", "sem-resultado"],
)
def test_rn_009_reverse_geocoding_without_name_shows_your_location(
    page: Page, weather_api, geo_api, answer
):
    """RN-009, feature 1 (categoria 2): se a geocodificação reversa falhar ou não trouxer um
    nome, o cabeçalho mostra "Sua localização", sem mensagem de erro, e os dados
    meteorológicos aparecem normalmente."""
    geo_api.reverse_answer = answer
    allow_location(page, *TOKYO_DEVICE)
    page.goto("/")

    expect(city_name(page)).to_have_text("Sua localização")
    expect(page.locator(".current")).to_have_attribute("data-block-state", "ready")
    expect(notice(page)).to_be_hidden()
    assert [TOKYO_QUERY in url for url in weather_api.urls] == [True]
    assert selected_city(page)["markerLabel"] == "Sua localização"


# ---------- Localização tardia (T-6c.3) ----------


def test_rn_003_late_location_replaces_default_city(page: Page, weather_api, geo_api):
    """RN-003, feature 1 (categoria 2): a localização que chega depois do prazo, com a cidade
    padrão ainda selecionada, substitui a cidade padrão, e o aviso some."""
    geo = FakeGeolocation(page)
    open_paused(page)
    page.clock.run_for(10_000)
    expect_default_city_with_notice(page, weather_api)

    geo.succeed(*TOKYO_DEVICE)

    expect(city_name(page)).to_have_text("Tóquio, JP")
    expect(notice(page)).to_be_hidden()
    expect(page.locator(".current")).to_have_attribute("data-block-state", "ready")
    assert geo_api.reverse_coords == [("35.6895", "139.6917")]
    assert TOKYO_QUERY in weather_api.urls[-1]


def test_rn_003_late_location_is_discarded_after_user_chose_city(page: Page, weather_api, geo_api):
    """RN-003, feature 1 (categoria 2): a localização que chega depois de o usuário escolher
    outra cidade é descartada, sem geocodificação reversa nem consulta de clima."""
    geo = FakeGeolocation(page)
    open_paused(page)
    page.clock.run_for(10_000)
    expect_default_city_with_notice(page, weather_api)
    search_and_choose(page, "Curitiba", "Curitiba, Paraná, BR")
    expect(city_name(page)).to_have_text("Curitiba, BR")
    consultations = len(weather_api.urls)

    geo.succeed(*TOKYO_DEVICE)
    page.wait_for_timeout(300)

    expect(city_name(page)).to_have_text("Curitiba, BR")
    assert geo_api.reverse_coords == []
    assert len(weather_api.urls) == consultations


# ---------- Aviso de localização (T-6c.4) ----------


def test_rn_002_location_notice_can_be_closed(page: Page, weather_api):
    """RN-002: o aviso de localização pode ser fechado pelo usuário. A cidade padrão continua
    selecionada, sem nova consulta."""
    page.goto("/")
    expect_default_city_with_notice(page, weather_api)

    page.get_by_role("button", name="Fechar aviso").click()

    expect(notice(page)).to_be_hidden()
    expect(city_name(page)).to_have_text("Uberlândia, BR")
    assert len(weather_api.urls) == 1


def test_rn_002_location_notice_disappears_when_another_city_is_chosen(
    page: Page, weather_api, geo_api
):
    """RN-002, P-009: com a localização negada, a busca continua disponível, e o aviso some
    quando outra cidade é escolhida."""
    page.goto("/")
    expect_default_city_with_notice(page, weather_api)

    search_and_choose(page, "Tóquio")

    expect(city_name(page)).to_have_text("Tóquio, JP")
    expect(notice(page)).to_be_hidden()


# ---------- Busca com a localização pendente (T-6c.5) ----------


def test_p_009_search_works_while_location_is_pending_and_chosen_city_prevails(
    page: Page, weather_api, geo_api
):
    """P-009, feature 1 (categoria 2): com o pedido de localização pendente, a busca funciona
    normalmente, e a cidade escolhida prevalece: a localização que chega depois, no prazo ou
    não, é descartada, e a cidade padrão não entra quando o prazo vence."""
    geo = FakeGeolocation(page)
    open_paused(page)

    search_and_choose(page, "Tóquio")
    expect(city_name(page)).to_have_text("Tóquio, JP")
    expect(page.locator(".current")).to_have_attribute("data-block-state", "ready")

    geo.succeed(-25.4296, -49.2713)  # no prazo, mas depois da escolha
    page.clock.run_for(10_000)
    page.wait_for_timeout(300)

    expect(city_name(page)).to_have_text("Tóquio, JP")
    expect(notice(page)).to_be_hidden()
    assert geo_api.reverse_coords == []
    assert [SEARCHED_TOKYO_QUERY in url for url in weather_api.urls] == [True]
