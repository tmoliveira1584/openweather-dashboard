"""Revisão de concorrência e de tempo em todos os blocos (fatia 12, T-12.2).

- Concorrência: respostas que chegam fora de ordem, a mesma cidade escolhida de novo com a
  consulta em andamento e a escala trocada durante a atualização.
- Tempo: com a página aberta e parada, o minuto, a hora e o dia que passaram saem da tela sem
  consulta (seção 7.4, passagem do tempo).

O relógio começa parado às 16:42:05 de segunda, 05/10/2026, em Uberlândia (`open_paused`).
"""

from playwright.sync_api import Page, expect

from tests.e2e.clock import open_paused
from tests.e2e.visibility import leave_page, return_to_page
from tests.e2e.weather_api import TOKYO, UBERLANDIA

BLOCKS = [".day-tabs", ".current", ".hourly", ".minutely"]


def expect_all(page: Page, state: str) -> None:
    for selector in BLOCKS:
        expect(page.locator(selector)).to_have_attribute("data-block-state", state)


def select_city(page: Page, city: dict) -> None:
    page.evaluate(
        "async (city) => { (await import('/js/actions.js')).selectCity(city); }",
        city,
    )


def header_city(page: Page):
    return page.locator(".city-name")


def bars(page: Page):
    return page.locator(".minutely-bars .bar")


def open_ready(page: Page, weather_api) -> None:
    """Abre com o relógio parado; os pedidos seguintes ao primeiro ficam pendentes."""
    weather_api.hold = True
    open_paused(page)
    weather_api.release(0)
    expect_all(page, "ready")


# ---------- Concorrência ----------


def test_p_012_refresh_of_previous_city_is_discarded(page: Page, weather_api, weather_views):
    """P-012, RF-014, feature 1 (categoria 7): com Uberlândia sendo atualizada na volta à
    página, o usuário escolhe Tóquio. A resposta da atualização, que chega depois, não muda a
    tela, que mostra Tóquio."""
    open_ready(page, weather_api)
    leave_page(page)
    page.clock.run_for(600_000)
    return_to_page(page)
    expect_all(page, "refreshing")

    select_city(page, TOKYO)
    expect_all(page, "loading")
    weather_api.release(2)  # Tóquio responde
    expect_all(page, "ready")
    weather_api.release(1)  # a atualização de Uberlândia chega depois
    page.wait_for_timeout(300)

    expect_all(page, "ready")
    expect(header_city(page)).to_have_text("Tóquio, JP")
    weather = page.evaluate("async () => (await import('/js/state.js')).getState().weather")
    assert weather == weather_views["tokyo"]


def test_rf_015_city_chosen_again_while_loading_reuses_the_query(page: Page, weather_api):
    """RF-015, P-012, feature 1 (categoria 7): cidade A, depois B e de novo A antes das
    respostas. A volta para A não gera outra consulta, a resposta de A é aplicada e a de B,
    que chega por último, é descartada."""
    weather_api.hold = True
    open_paused(page)  # A: Uberlândia
    expect_all(page, "loading")
    select_city(page, TOKYO)  # B
    weather_api.wait_for_held(2)
    select_city(page, UBERLANDIA)  # A de novo
    page.wait_for_timeout(300)
    assert len(weather_api.urls) == 2

    weather_api.release(0)
    expect_all(page, "ready")
    weather_api.release(1)
    page.wait_for_timeout(300)

    expect(header_city(page)).to_have_text("Uberlândia, BR")
    expect(page.locator(".current-time")).to_have_text("16:41")


def test_rnf_029_scale_switched_during_refresh_applies_to_old_and_new_data(
    page: Page, weather_api, weather_views
):
    """RNF-029, RF-058, RF-014: trocar para °F durante a atualização muda na hora os dados
    antigos, ainda visíveis, e os dados novos chegam já em °F, sem consulta adicional."""
    open_ready(page, weather_api)
    leave_page(page)
    page.clock.run_for(600_000)
    return_to_page(page)
    expect_all(page, "refreshing")

    page.get_by_role("button", name="°F", exact=True).click()

    current = weather_views["uberlandia"]["current"]
    expect(page.locator(".current-temp")).to_have_text(current["temp"]["f"])
    updated = {
        **weather_views["uberlandia"],
        "current": {**current, "temp": {"c": "23°", "f": "73°"}},
    }
    weather_api.release(1, updated)
    expect_all(page, "ready")
    expect(page.locator(".current-temp")).to_have_text("73°")
    assert len(weather_api.urls) == 2


# ---------- Passagem do tempo com a página aberta ----------


def test_rn_047_minute_window_advances_with_the_page_open(page: Page, weather_api):
    """RN-047, feature 5 (categoria 8): com a página aberta e sem nenhuma ação, a cada minuto
    o minuto que passou sai do painel. Às 16:47, sobram 55 barras, e o "Agora" é 16:47."""
    open_ready(page, weather_api)
    expect(bars(page)).to_have_count(60)

    page.clock.fast_forward("05:00")

    expect(bars(page)).to_have_count(55)
    expect(page.locator(".mark-time").first).to_have_text("16:47")
    assert len(weather_api.urls) == 1


def test_rn_034_hour_window_advances_with_the_page_open(page: Page, weather_api):
    """RN-034, feature 4 (categoria 8): com a página aberta e sem nenhuma ação, quando começa
    uma nova hora, a janela passa a começar nela."""
    open_ready(page, weather_api)
    expect(page.locator(".hour-label").first).to_have_text("16:00")

    page.clock.fast_forward("18:00")  # 17:00:05

    expect(page.locator(".hour-label").first).to_have_text("17:00")
    expect(page.locator(".hour-card")).to_have_count(24)
    assert len(weather_api.urls) == 1


def test_rn_026_midnight_with_the_page_open_drops_the_past_day(page: Page, weather_api):
    """RN-026, feature 3 (categoria 8): com a página aberta, os dados atravessam a meia-noite
    da cidade. A segunda virou passado: "Hoje" passa a ser a terça, e a seleção de terça volta
    para "Hoje". Sem nova consulta, a previsão por minuto, toda no passado, fica
    indisponível."""
    open_ready(page, weather_api)
    page.locator(".day-tab", has_text="Ter").click()

    page.clock.fast_forward("07:18:00")  # 00:00:05 de terça

    expect(page.locator(".day-tab-label")).to_have_text(
        ["Hoje", "Qua", "Qui", "Sex", "Sáb", "Dom", "Seg", "Ter"]
    )
    expect(page.locator('.day-tab[aria-selected="true"]')).to_contain_text("Hoje")
    expect(page.locator(".current-time")).to_have_text("16:41")
    expect(page.locator(".hour-label").first).to_have_text("00:00 Ter")  # RN-035
    expect(page.locator(".minutely")).to_have_attribute("data-block-state", "unavailable")
    assert len(weather_api.urls) == 1


def test_rn_047_returning_to_the_page_updates_the_windows_at_once(page: Page, weather_api):
    """RN-047, RN-034, seção 7.4: em segundo plano, o navegador atrasa os relógios da página.
    Ao voltar antes de 10 min, as janelas são recalculadas na hora, sem consulta."""
    open_ready(page, weather_api)
    leave_page(page)
    # Sem disparar timers. No Python, o `set_system_time` recebe segundos.
    page.clock.set_system_time(page.evaluate("Date.now() / 1000") + 8 * 60)

    return_to_page(page)

    expect(bars(page)).to_have_count(52)
    expect_all(page, "ready")
    assert len(weather_api.urls) == 1
