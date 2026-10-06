"""Feature 1, cabeçalho e busca de cidade: cidade selecionada, campo, lista e teclado.

A página abre com a cidade padrão: sem permissão concedida, o Chrome do Playwright nega a
localização na hora (ver `test_f1_location.py`). O `/api/weather` e o `/api/geo/search` são
simulados com `page.route` (ver `weather_api.py` e `geo_api.py`).
"""

import re

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.clock import open_paused
from tests.e2e.weather_api import TOKYO

LONG_NAME = "Santa Maria Madalena da Serra das Cachoeiras Altas do Rio Grande, BR"


def select_city(page: Page, city: dict) -> None:
    """Seleciona a cidade sem esperar a consulta de clima terminar."""
    page.evaluate(
        "async (city) => { (await import('/js/actions.js')).selectCity(city); }",
        city,
    )


def is_truncated(page: Page) -> bool:
    return page.locator(".city-name").evaluate("(n) => n.scrollWidth > n.clientWidth")


# ---------- Cidade selecionada no cabeçalho (T-6b.1) ----------


def test_rf_010_header_shows_selected_city_with_country_code(page: Page, weather_api):
    """RF-010, RN-007: o cabeçalho mostra a cidade selecionada no formato "<nome>, <país>"."""
    page.goto("/")

    expect(page.locator(".city-name")).to_have_text("Uberlândia, BR")


def test_rn_013_header_changes_at_once_while_blocks_load(page: Page, weather_api):
    """RN-013: ao trocar de cidade, o cabeçalho mostra a nova cidade na hora, e os blocos de
    dados mostram carregamento no lugar dos dados da cidade anterior."""
    page.goto("/")
    expect(page.locator(".current")).to_have_attribute("data-block-state", "ready")

    weather_api.hold = True
    select_city(page, TOKYO)

    expect(page.locator(".city-name")).to_have_text("Tóquio, JP")
    expect(page.locator(".current")).to_have_attribute("data-block-state", "loading")


def test_rf_010_long_city_name_is_cut_and_shown_in_full_on_hover_and_focus(page: Page, weather_api):
    """RF-010, P-024, feature 1 (categoria 10): em 360 px, um nome longo é cortado com "…",
    sem rolagem horizontal da página, e aparece completo ao passar o cursor ou ao focar."""
    page.set_viewport_size({"width": 360, "height": 740})
    page.goto("/")
    select_city(page, {**TOKYO, "headerLabel": LONG_NAME})
    name = page.locator(".city-name")
    expect(name).to_have_text(LONG_NAME)

    assert is_truncated(page)
    assert name.evaluate("(n) => getComputedStyle(n).textOverflow") == "ellipsis"
    assert page.evaluate("document.documentElement.scrollWidth") <= 360

    page.locator(".city").hover()
    assert not is_truncated(page)
    page.mouse.move(0, 700)
    assert is_truncated(page)

    page.locator(".city").focus()
    assert not is_truncated(page)
    assert page.evaluate("document.documentElement.scrollWidth") <= 360


# ---------- Campo de busca (T-6b.2) ----------


def search_box(page: Page):
    return page.get_by_role("combobox", name="Buscar cidade")


def message(page: Page):
    return page.locator(".search-message")


def test_rnf_007_search_field_has_accessible_label(page: Page, weather_api):
    """RNF-007: o campo de busca tem o rótulo acessível "Buscar cidade", e a lupa também tem
    nome acessível."""
    page.goto("/")

    expect(search_box(page)).to_be_visible()
    expect(page.get_by_role("button", name="Buscar", exact=True)).to_be_visible()


def test_rn_004_field_does_not_accept_more_than_100_characters(page: Page, weather_api):
    """RN-004, feature 1 (categoria 1): o campo para de aceitar caracteres depois do 100º."""
    page.goto("/")
    box = search_box(page)

    box.press_sequentially("a" * 105)

    expect(box).to_have_value("a" * 100)


def test_rf_006_enter_and_magnifier_confirm_the_search(page: Page, weather_api, geo_api):
    """RF-006: a busca é confirmada pela tecla Enter ou pelo ícone de lupa, com o termo sem
    os espaços das pontas (RN-004)."""
    page.goto("/")
    box = search_box(page)

    box.fill("  Curitiba  ")
    box.press("Enter")
    expect(page.get_by_role("listbox")).to_be_visible()
    page.keyboard.press("Escape")

    page.get_by_role("button", name="Buscar", exact=True).click()
    expect(page.get_by_role("listbox")).to_be_visible()
    assert geo_api.terms == ["Curitiba", "Curitiba"]


def test_rn_004_empty_term_shows_message_without_query(page: Page, weather_api, geo_api):
    """RN-004, feature 1 (categoria 1): campo vazio ou só com espaços não consulta nada, mostra
    "Digite o nome de uma cidade." e o foco fica no campo, também pela lupa."""
    page.goto("/")
    box = search_box(page)

    box.press("Enter")
    expect(message(page)).to_have_text("Digite o nome de uma cidade.")
    expect(box).to_be_focused()

    box.fill("   ")
    page.get_by_role("button", name="Buscar", exact=True).click()
    expect(message(page)).to_have_text("Digite o nome de uma cidade.")
    expect(box).to_be_focused()
    assert geo_api.terms == []


def test_rn_004_one_character_shows_message_without_query(page: Page, weather_api, geo_api):
    """RN-004, feature 1 (categoria 1): termo com 1 caractere não consulta nada, mostra
    "Digite pelo menos 2 caracteres." e o foco fica no campo; editar o termo apaga a
    mensagem."""
    page.goto("/")
    box = search_box(page)

    box.fill(" a ")
    box.press("Enter")
    expect(message(page)).to_have_text("Digite pelo menos 2 caracteres.")
    expect(message(page)).to_have_attribute("role", "status")
    expect(box).to_be_focused()
    assert geo_api.terms == []

    box.press_sequentially("b")
    expect(message(page)).to_have_text("")


# ---------- Lista de resultados (T-6b.3) ----------

SANTA_MARIA_LABELS = [
    "Santa Maria, Rio Grande do Sul, BR",
    "Santa Maria, California, US",
    "Santa-Maria-Siché, Corsica, FR",
    "Ilha de Santa Maria, PT",
    "Santa Maria, Piedmont, IT",
]
TRUNCATED_HINT = (
    "Mostrando as 5 primeiras cidades. Inclua o estado ou o país para refinar "
    "(ex.: Santa Maria, BR)."
)


def run_search(page: Page, term: str) -> None:
    box = search_box(page)
    box.fill(term)
    box.press("Enter")


def expect_city_kept(page: Page, weather_api) -> None:
    """A cidade selecionada e os dados dela continuam na tela, sem nova consulta de clima."""
    expect(page.locator(".city-name")).to_have_text("Uberlândia, BR")
    expect(page.locator(".current")).to_have_attribute("data-block-state", "ready")
    assert len(weather_api.urls) == 1


def test_ca_004_santa_maria_lists_5_cities_with_state_and_country(page: Page, weather_api, geo_api):
    """CA-004, RF-006, RF-009, RN-005: "Santa Maria" lista até 5 cidades, na ordem do
    provedor, cada uma com nome, estado (quando houver) e país, e a dica das 5 primeiras."""
    page.goto("/")

    run_search(page, "Santa Maria")

    listbox = page.get_by_role("listbox", name="Cidades encontradas")
    expect(listbox).to_be_visible()
    expect(listbox.get_by_role("option")).to_have_text(SANTA_MARIA_LABELS)
    expect(page.get_by_text(TRUNCATED_HINT)).to_be_visible()
    expect(search_box(page)).to_have_attribute("aria-expanded", "true")
    expect_city_kept(page, weather_api)


def test_rn_005_hint_is_hidden_with_less_than_5_cities(page: Page, weather_api, geo_api):
    """RN-005, feature 1 (categoria 10): com menos de 5 cidades, a lista não mostra a dica."""
    page.goto("/")

    run_search(page, "Curitiba")

    expect(page.get_by_role("option")).to_have_count(2)
    expect(page.get_by_text(TRUNCATED_HINT)).to_be_hidden()


def test_ca_005_choosing_curitiba_updates_header_and_blocks(page: Page, weather_api, geo_api):
    """CA-005, RF-008: escolher "Curitiba, Paraná, BR" fecha a lista, limpa o campo, mostra
    "Curitiba, BR" no cabeçalho e consulta o clima de Curitiba."""
    page.goto("/")
    expect(page.locator(".current")).to_have_attribute("data-block-state", "ready")
    run_search(page, "Curitiba")

    page.get_by_role("option", name="Curitiba, Paraná, BR").click()

    expect(page.get_by_role("listbox")).to_be_hidden()
    expect(search_box(page)).to_have_value("")
    expect(search_box(page)).to_have_attribute("aria-expanded", "false")
    expect(page.locator(".city-name")).to_have_text("Curitiba, BR")
    expect(page.locator(".current")).to_have_attribute("data-block-state", "ready")
    assert len(weather_api.urls) == 2
    assert "lat=-25.43&lon=-49.27" in weather_api.urls[-1]


def test_rf_007_single_city_is_selected_without_list(page: Page, weather_api, geo_api):
    """RF-007: a busca com uma única cidade a seleciona sem abrir a lista."""
    page.goto("/")
    page.evaluate(
        """async () => {
            const { subscribe } = await import('/js/state.js');
            window.searchStatuses = [];
            subscribe((state) => window.searchStatuses.push(state.search.status));
        }"""
    )

    run_search(page, "Tóquio")

    expect(page.locator(".city-name")).to_have_text("Tóquio, JP")
    expect(search_box(page)).to_have_value("")
    expect(page.get_by_role("listbox")).to_be_hidden()
    assert "open" not in page.evaluate("window.searchStatuses")
    assert "lat=35.68&lon=139.76" in weather_api.urls[-1]


def test_ca_006_unknown_city_shows_message_and_keeps_city(page: Page, weather_api, geo_api):
    """CA-006, RF-012: "Xyzabc" mostra a mensagem de nenhum resultado, a lista não abre e a
    cidade selecionada continua exibida."""
    page.goto("/")

    run_search(page, "Xyzabc")

    expect(message(page)).to_have_text(
        'Nenhuma cidade encontrada para "Xyzabc". Verifique a grafia.'
    )
    expect(page.get_by_role("listbox")).to_be_hidden()
    expect_city_kept(page, weather_api)


def test_rf_012_search_failure_shows_message_and_keeps_city(page: Page, weather_api, geo_api):
    """RF-012, P-004, feature 1 (categoria 4): se a geocodificação falhar, a lista não abre,
    a mensagem do spec aparece sem detalhe técnico e a cidade selecionada continua."""
    geo_api.answers["Rio"] = (502, "provider_unavailable")
    page.goto("/")

    run_search(page, "Rio")

    expect(message(page)).to_have_text("Não foi possível buscar cidades agora. Tente novamente.")
    expect(page.get_by_role("listbox")).to_be_hidden()
    expect_city_kept(page, weather_api)


def test_rf_011_escape_closes_list_without_changing_city(page: Page, weather_api, geo_api):
    """RF-011: Esc fecha a lista sem alterar a cidade selecionada nem apagar o termo."""
    page.goto("/")
    run_search(page, "Curitiba")
    expect(page.get_by_role("listbox")).to_be_visible()

    page.keyboard.press("Escape")

    expect(page.get_by_role("listbox")).to_be_hidden()
    expect(search_box(page)).to_have_value("Curitiba")
    expect_city_kept(page, weather_api)


def test_rf_011_click_outside_closes_list_and_message(page: Page, weather_api, geo_api):
    """RF-011: clicar fora da lista a fecha sem alterar a cidade selecionada; o mesmo vale
    para a mensagem de nenhum resultado."""
    page.goto("/")
    run_search(page, "Curitiba")
    expect(page.get_by_role("listbox")).to_be_visible()

    page.locator(".app-title").click()

    expect(page.get_by_role("listbox")).to_be_hidden()
    expect_city_kept(page, weather_api)

    run_search(page, "Xyzabc")
    expect(message(page)).not_to_have_text("")
    page.locator(".app-title").click()
    expect(message(page)).to_have_text("")


def test_rf_015_repeated_confirmations_make_a_single_search(page: Page, weather_api, geo_api):
    """RF-015, feature 1 (categoria 7): duplo Enter e duplo clique na lupa, com a busca em
    andamento ou com a lista dela aberta, fazem uma única busca."""
    geo_api.hold = True
    page.goto("/")
    box = search_box(page)
    magnifier = page.get_by_role("button", name="Buscar", exact=True)

    box.fill("Santa Maria")
    box.press("Enter")
    box.press("Enter")
    magnifier.dblclick()
    expect(page.locator(".search")).to_have_attribute("aria-busy", "true")
    geo_api.release(0)

    expect(page.get_by_role("option")).to_have_count(5)
    expect(page.locator(".search")).to_have_attribute("aria-busy", "false")
    box.press("Enter")
    magnifier.click()
    page.wait_for_timeout(300)
    assert geo_api.terms == ["Santa Maria"]
    expect(page.get_by_role("option")).to_have_count(5)


def test_p_003_markup_in_term_and_results_is_shown_as_text(page: Page, weather_api, geo_api):
    """P-003, RN-004, feature 1 (categoria 1): um termo com marcação, como "<b>Rio</b>", é
    enviado e exibido como texto, e os resultados também, sem criar elementos."""
    term = "<b>Rio</b>"
    page.goto("/")

    run_search(page, term)
    expect(message(page)).to_have_text(
        f'Nenhuma cidade encontrada para "{term}". Verifique a grafia.'
    )
    assert geo_api.terms == [term]

    geo_api.answers[term] = [
        {"name": term, "state": "<i>RJ</i>", "country": "BR", "lat": -22.9, "lon": -43.2},
        {"name": "<img src=x onerror=alert(1)>", "country": "BR", "lat": -10.0, "lon": -50.0},
    ]
    page.locator(".app-title").click()
    run_search(page, term)

    expect(page.get_by_role("option")).to_have_text(
        ["<b>Rio</b>, <i>RJ</i>, BR", "<img src=x onerror=alert(1)>, BR"]
    )
    assert page.locator(".search b, .search i, .search img").count() == 0


# ---------- Teclado na lista (T-6b.4) ----------


def selected_options(page: Page) -> list[str]:
    return page.locator('[role="option"][aria-selected="true"]').all_inner_texts()


def test_rnf_007_arrows_move_through_the_list_and_enter_chooses(page: Page, weather_api, geo_api):
    """RNF-007, P-023, RF-008: com a lista aberta, as setas percorrem as cidades (dando a
    volta nas pontas), o campo aponta a opção destacada e o Enter escolhe a cidade."""
    page.goto("/")
    box = search_box(page)
    run_search(page, "Santa Maria")
    expect(page.get_by_role("option")).to_have_count(5)
    expect(box).not_to_have_attribute("aria-activedescendant", re.compile(".+"))

    box.press("ArrowDown")
    assert selected_options(page) == [SANTA_MARIA_LABELS[0]]
    active_id = box.get_attribute("aria-activedescendant")
    expect(page.locator(f"#{active_id}")).to_have_text(SANTA_MARIA_LABELS[0])

    box.press("ArrowUp")
    assert selected_options(page) == [SANTA_MARIA_LABELS[4]]
    box.press("ArrowDown")
    assert selected_options(page) == [SANTA_MARIA_LABELS[0]]
    box.press("ArrowDown")
    assert selected_options(page) == [SANTA_MARIA_LABELS[1]]
    expect(box).to_be_focused()

    box.press("Enter")

    expect(page.get_by_role("listbox")).to_be_hidden()
    expect(page.locator(".city-name")).to_have_text("Santa Maria, US")
    expect(box).to_have_value("")
    assert geo_api.terms == ["Santa Maria"]


def test_rnf_007_arrow_up_starts_at_the_last_city(page: Page, weather_api, geo_api):
    """RNF-007: sem opção destacada, a seta para cima começa pela última cidade."""
    page.goto("/")
    run_search(page, "Santa Maria")
    expect(page.get_by_role("option")).to_have_count(5)

    search_box(page).press("ArrowUp")

    assert selected_options(page) == [SANTA_MARIA_LABELS[4]]


def test_rnf_007_highlighted_option_is_not_shown_only_by_color(page: Page, weather_api, geo_api):
    """RNF-007, P-018: a opção destacada tem negrito e barra lateral, além da cor."""
    page.goto("/")
    run_search(page, "Curitiba")
    expect(page.get_by_role("listbox")).to_be_visible()
    search_box(page).press("ArrowDown")

    styles = page.locator('[role="option"]').evaluate_all(
        "(nodes) => nodes.map((n) => [getComputedStyle(n).fontWeight, "
        "getComputedStyle(n).boxShadow])"
    )

    (selected_weight, selected_bar), (other_weight, other_bar) = styles
    assert int(selected_weight) >= 700 > int(other_weight)
    assert selected_bar != "none" and other_bar == "none"


def test_rnf_007_escape_closes_the_list_and_keeps_focus(page: Page, weather_api, geo_api):
    """RNF-007, RF-011: o Esc fecha a lista com uma opção destacada, o foco fica no campo e a
    cidade selecionada não muda; uma nova busca começa sem opção destacada."""
    page.goto("/")
    box = search_box(page)
    run_search(page, "Curitiba")
    expect(page.get_by_role("listbox")).to_be_visible()
    box.press("ArrowDown")

    box.press("Escape")

    expect(page.get_by_role("listbox")).to_be_hidden()
    expect(box).to_be_focused()
    expect(box).not_to_have_attribute("aria-activedescendant", re.compile(".+"))
    expect_city_kept(page, weather_api)

    box.press("Enter")
    expect(page.get_by_role("option")).to_have_count(2)
    assert selected_options(page) == []


def test_rnf_007_tab_out_of_the_search_closes_the_list(page: Page, weather_api, geo_api):
    """RNF-007, RF-011: sair da busca pelo teclado fecha a lista, como clicar fora."""
    page.goto("/")
    run_search(page, "Curitiba")
    expect(page.get_by_role("listbox")).to_be_visible()

    page.keyboard.press("Tab")

    expect(page.get_by_role("listbox")).to_be_hidden()
    expect_city_kept(page, weather_api)


# ---------- Cache, cota e tela estreita (T-6b.6) ----------


def record_weather_statuses(page: Page) -> None:
    page.evaluate(
        """async () => {
            const { subscribe } = await import('/js/state.js');
            window.weatherStatuses = [];
            subscribe((state) => window.weatherStatuses.push(state.weatherStatus));
        }"""
    )


def choose(page: Page, term: str, label: str) -> None:
    run_search(page, term)
    page.get_by_role("option", name=label, exact=True).click()


def test_ca_007_choosing_curitiba_again_after_5_minutes_uses_the_cache(
    page: Page, weather_api, geo_api
):
    """CA-007, RN-010, RNF-002, feature 1 (categoria 7): Curitiba consultada há 5 minutos,
    escolhida de novo pela busca, aparece sem nova consulta de clima e sem carregamento."""
    open_paused(page)
    choose(page, "Curitiba", "Curitiba, Paraná, BR")
    expect(page.locator(".current")).to_have_attribute("data-block-state", "ready")
    expect(page.locator(".city-name")).to_have_text("Curitiba, BR")
    run_search(page, "Tóquio")  # cidade única: selecionada direto (RF-007)
    expect(page.locator(".city-name")).to_have_text("Tóquio, JP")
    assert len(weather_api.urls) == 3

    page.clock.run_for(5 * 60_000)
    record_weather_statuses(page)
    choose(page, "Curitiba", "Curitiba, Paraná, BR")

    expect(page.locator(".city-name")).to_have_text("Curitiba, BR")
    expect(page.locator(".current")).to_have_attribute("data-block-state", "ready")
    assert set(page.evaluate("window.weatherStatuses")) == {"ready"}
    assert len(weather_api.urls) == 3


def test_rnf_003_one_weather_query_per_city_and_one_geocoding_per_search(
    page: Page, weather_api, geo_api
):
    """RNF-003, P-010: cada busca confirmada faz 1 consulta de geocodificação, e cada cidade
    faz no máximo 1 consulta de clima a cada 10 minutos, mesmo escolhida várias vezes."""
    page.goto("/")  # Uberlândia: 1ª consulta de clima

    choose(page, "Santa Maria", "Santa Maria, Rio Grande do Sul, BR")
    expect(page.locator(".city-name")).to_have_text("Santa Maria, BR")
    choose(page, "Curitiba", "Curitiba, Paraná, BR")
    expect(page.locator(".city-name")).to_have_text("Curitiba, BR")
    choose(page, "Santa Maria", "Santa Maria, Rio Grande do Sul, BR")
    expect(page.locator(".city-name")).to_have_text("Santa Maria, BR")
    choose(page, "Curitiba", "Curitiba, Paraná, BR")
    expect(page.locator(".city-name")).to_have_text("Curitiba, BR")
    expect(page.locator(".current")).to_have_attribute("data-block-state", "ready")

    assert geo_api.terms == ["Santa Maria", "Curitiba", "Santa Maria", "Curitiba"]
    assert len(weather_api.urls) == 3


def test_p_024_search_at_360px_fills_the_width_and_opens_below(page: Page, weather_api, geo_api):
    """P-024, feature 1 (categoria 10): em 360 px, o campo ocupa a largura disponível, e a
    lista e as mensagens abrem logo abaixo dele, sem rolagem horizontal da página."""
    page.set_viewport_size({"width": 360, "height": 740})
    page.goto("/")
    header = page.locator(".app-header").bounding_box()
    form = page.locator(".search").bounding_box()
    assert form["width"] == pytest.approx(header["width"], abs=1)

    for term in ("Santa Maria", "Xyzabc"):
        run_search(page, term)
        popup = page.locator(".search-popup" if term == "Santa Maria" else ".search-message")
        expect(popup).to_be_visible()
        box = popup.bounding_box()
        assert box["y"] >= form["y"] + form["height"]
        assert box["y"] - (form["y"] + form["height"]) <= 8
        assert box["x"] == pytest.approx(form["x"], abs=1)
        assert box["width"] == pytest.approx(form["width"], abs=1)
        assert page.evaluate("document.documentElement.scrollWidth") <= 360
        page.keyboard.press("Escape")
