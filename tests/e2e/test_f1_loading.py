"""Feature 1, carregamento dos dados: estados dos blocos, erros, cache e respostas antigas.

A página abre com a cidade padrão (o `main.js` provisório da fatia 6a). O `/api/weather` é
simulado com `page.route` (ver `weather_api.py`) e o tempo, com `page.clock`.
"""

import re

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.clock import open_paused
from tests.e2e.weather_api import TOKYO, UBERLANDIA

# Blocos de dados da tela (seção 7.1) e um elemento do conteúdo de cada um.
BLOCKS = {
    ".day-tabs": ".day-tabs-list",
    ".current": ".indicators",
    ".hourly": ".hourly-scroll",
    ".minutely": ".minutely-bars",
}

ERROR_CASES = [
    (
        (502, "provider_unauthorized"),
        "O serviço de clima recusou o acesso. Tente novamente mais tarde.",
    ),
    (
        (502, "provider_rate_limited"),
        "Limite de consultas ao serviço de clima atingido. Tente novamente em alguns minutos.",
    ),
    ((502, "provider_unavailable"), "O serviço de clima está indisponível no momento."),
    ((504, "provider_timeout"), "O serviço de clima demorou para responder."),
    (
        (502, "network_unavailable"),
        "Sem conexão com a internet. Verifique sua rede e tente novamente.",
    ),
    ((400, "invalid_request"), "O serviço de clima está indisponível no momento."),
    ("abort", "O serviço de clima está indisponível no momento."),  # servidor fora do ar
]


def block_states(page: Page) -> dict[str, str]:
    return {sel: page.locator(sel).get_attribute("data-block-state") for sel in BLOCKS}


def expect_all(page: Page, state: str) -> None:
    for selector in BLOCKS:
        expect(page.locator(selector)).to_have_attribute("data-block-state", state)


def select_city(page: Page, city: dict) -> str:
    """Seleciona a cidade como a busca fará na 6b e devolve o estado do card logo depois."""
    return page.evaluate(
        """async (city) => {
            const actions = await import('/js/actions.js');
            actions.selectCity(city);
            return document.querySelector('.current').dataset.blockState;
        }""",
        city,
    )


def weather_in_state(page: Page) -> dict | None:
    return page.evaluate("async () => (await import('/js/state.js')).getState().weather")


def test_rf_005_blocks_show_loading_while_weather_is_fetched(page: Page, weather_api):
    """RF-005, P-020: enquanto a consulta não volta, cada bloco de dados mostra o indicador
    de carregamento no lugar do conteúdo; com a resposta, o conteúdo aparece."""
    weather_api.hold = True
    page.goto("/")

    expect_all(page, "loading")
    for selector, content in BLOCKS.items():
        block = page.locator(selector)
        expect(block).to_have_attribute("aria-busy", "true")
        expect(block.locator(".block-state-spinner")).to_be_visible()
        expect(block.locator(".block-state")).to_have_text("Carregando…")
        expect(block.locator(content)).to_be_hidden()
    expect(page.locator(".hourly .panel-title")).to_be_visible()

    weather_api.release()

    expect_all(page, "ready")
    for selector, content in BLOCKS.items():
        expect(page.locator(selector)).to_have_attribute("aria-busy", "false")
        expect(page.locator(f"{selector} > .block-state")).to_be_hidden()
        expect(page.locator(content)).to_be_visible()
    assert len(weather_api.urls) == 1


def test_rn_012_blocks_show_still_loading_after_3s(page: Page, weather_api):
    """RN-012, P-020: depois de 3 s sem resposta, o indicador continua com "Ainda
    carregando…"."""
    weather_api.hold = True
    open_paused(page)
    expect_all(page, "loading")

    page.clock.run_for(2_999)
    expect(page.get_by_text("Ainda carregando…")).to_have_count(0)
    page.clock.run_for(1)

    expect(page.get_by_text("Ainda carregando…")).to_have_count(len(BLOCKS))
    for selector in BLOCKS:
        expect(page.locator(f"{selector} .block-state-spinner")).to_be_visible()


def test_rn_012_no_answer_in_17s_shows_slow_service_message(page: Page, weather_api):
    """RN-012, RF-013: se nem o backend responder, a trava de 17 s encerra a consulta como
    lentidão, com a mensagem do spec e "Tentar novamente"."""
    weather_api.hold = True
    open_paused(page)

    page.clock.run_for(17_000)

    expect_all(page, "error")
    expect(page.get_by_text("O serviço de clima demorou para responder.")).to_have_count(
        len(BLOCKS)
    )


def test_ca_008_provider_down_shows_message_and_retry_button(page: Page, weather_api):
    """CA-008, RF-013, P-022: com o provedor fora do ar, os blocos mostram "O serviço de clima
    está indisponível no momento." e o botão "Tentar novamente"."""
    weather_api.queue = [(502, "provider_unavailable")]
    page.goto("/")

    expect_all(page, "error")
    for selector, content in BLOCKS.items():
        block = page.locator(selector)
        expect(
            block.get_by_text("O serviço de clima está indisponível no momento.")
        ).to_be_visible()
        expect(block.get_by_role("button", name="Tentar novamente")).to_be_visible()
        expect(block.locator(content)).to_be_hidden()
    # O cabeçalho e a busca continuam disponíveis (feature 1, categoria 3).
    expect(page.locator(".search-input")).to_be_visible()


@pytest.mark.parametrize(("answer", "message"), ERROR_CASES)
def test_rf_013_each_failure_shows_its_spec_message(page: Page, weather_api, answer, message):
    """RF-013, RNF-008, P-004: cada tipo de falha mostra a mensagem do spec, sem código,
    número de status nem detalhe técnico."""
    weather_api.queue = [answer]
    page.goto("/")

    expect_all(page, "error")
    expect(page.get_by_text(message, exact=True)).to_have_count(len(BLOCKS))
    expect(page.get_by_role("button", name="Tentar novamente")).to_have_count(len(BLOCKS))
    body = page.locator("body").inner_text()
    assert not re.search(r"provider_|network_|invalid_|server_|\b(400|502|504)\b", body)


def test_rf_013_retry_loads_the_city_again_with_a_single_query(page: Page, weather_api):
    """RF-013, RN-013, RF-015: "Tentar novamente" refaz a consulta; cliques repetidos, em
    um ou em vários blocos, geram uma única consulta."""
    weather_api.queue = [(502, "provider_rate_limited")]
    page.goto("/")
    expect_all(page, "error")

    weather_api.hold = True
    buttons = page.get_by_role("button", name="Tentar novamente")
    buttons.first.evaluate(
        """(button) => {
            button.click();
            button.click();
            for (const other of document.querySelectorAll('.block-state-retry')) other.click();
        }"""
    )
    expect_all(page, "loading")
    weather_api.release(0)

    expect_all(page, "ready")
    assert len(weather_api.urls) == 2


def test_rn_010_city_in_cache_appears_without_query_or_loading(page: Page, weather_api):
    """RN-010, P-010, RNF-002, feature 1 (categoria 7): escolher de novo uma cidade
    consultada há menos de 10 min mostra os dados do cache, sem consulta e sem carregamento."""
    page.goto("/")
    expect_all(page, "ready")

    assert select_city(page, UBERLANDIA) == "ready"
    assert block_states(page) == dict.fromkeys(BLOCKS, "ready")
    assert len(weather_api.urls) == 1


def test_rn_010_cache_expired_after_10_minutes_queries_again(page: Page, weather_api):
    """RN-010, feature 1 (categoria 8): consultada há 10 min ou mais, a cidade é consultada
    de novo, com carregamento."""
    weather_api.hold = True
    open_paused(page)
    weather_api.release(0)
    expect_all(page, "ready")

    page.clock.run_for(600_000)
    assert select_city(page, UBERLANDIA) == "loading"
    weather_api.release(1)

    expect_all(page, "ready")
    assert len(weather_api.urls) == 2


def test_rn_011_failure_is_not_cached(page: Page, weather_api):
    """RN-011: depois de uma falha, escolher a mesma cidade faz uma consulta nova."""
    weather_api.queue = [(502, "provider_unavailable")]
    page.goto("/")
    expect_all(page, "error")

    assert select_city(page, UBERLANDIA) == "loading"

    expect_all(page, "ready")
    assert len(weather_api.urls) == 2


def test_p_012_late_answer_of_previous_city_is_discarded(page: Page, weather_api, weather_views):
    """P-012, feature 1 (categoria 7): com a cidade A e depois a B, a resposta de A que chega
    por último, mesmo de erro, não muda a tela, que mostra B."""
    weather_api.hold = True
    page.goto("/")  # A: Uberlândia, a cidade padrão
    expect_all(page, "loading")
    select_city(page, TOKYO)  # B
    weather_api.wait_for_held(2)  # as duas consultas estão pendentes

    weather_api.release(1)  # B responde
    expect_all(page, "ready")
    weather_api.release(0, (502, "provider_unavailable"))  # A falha depois
    page.wait_for_timeout(300)

    assert block_states(page) == dict.fromkeys(BLOCKS, "ready")
    assert weather_in_state(page) == weather_views["tokyo"]


def test_p_021_block_missing_from_answer_shows_unavailable_and_others_keep_data(
    page: Page, weather_api, weather_views
):
    """P-021, P-013: um bloco que não veio na resposta mostra a mensagem de indisponibilidade
    do spec, e os demais blocos continuam com os dados."""
    weather_api.views = {
        **weather_views,
        "uberlandia": {
            **weather_views["uberlandia"],
            "daily": None,
            "hourly": None,
            "minutely": None,
        },
    }
    page.goto("/")

    expect(page.locator(".current")).to_have_attribute("data-block-state", "ready")
    expect(page.locator(".indicators")).to_be_visible()
    for selector, message in [
        (".day-tabs", "Previsão diária indisponível."),
        (".hourly", "Previsão hora a hora indisponível para esta cidade."),
        (".minutely", "Previsão por minuto indisponível para esta localidade."),
    ]:
        block = page.locator(selector)
        expect(block).to_have_attribute("data-block-state", "unavailable")
        expect(block.locator(".block-state")).to_have_text(message)
        expect(block.get_by_role("button")).to_have_count(0)
