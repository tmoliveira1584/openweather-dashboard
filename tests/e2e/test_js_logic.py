"""Lógica JavaScript testada no Chrome com `page.evaluate(import(...))` (arquitetura, seção 9.1).

O `main.js` é trocado por um módulo vazio: a tela não dispara consultas, e cada teste importa
só os módulos que exercita.
"""

import re

import pytest
from playwright.sync_api import Page

from tests.e2e.clock import open_paused
from tests.e2e.weather_api import TOKYO, UBERLANDIA
from tests.fakes import CAPTURE_NOW

# Mensagens do spec (feature 1) para cada código de erro (arquitetura, seção 7.3).
SPEC_ERROR_MESSAGES = {
    "provider_unauthorized": "O serviço de clima recusou o acesso. Tente novamente mais tarde.",
    "provider_rate_limited": (
        "Limite de consultas ao serviço de clima atingido. Tente novamente em alguns minutos."
    ),
    "provider_unavailable": "O serviço de clima está indisponível no momento.",
    "server_unreachable": "O serviço de clima está indisponível no momento.",
    "invalid_request": "O serviço de clima está indisponível no momento.",
    "provider_timeout": "O serviço de clima demorou para responder.",
    "network_unavailable": "Sem conexão com a internet. Verifique sua rede e tente novamente.",
}


def empty_main(page: Page) -> None:
    """Troca o `main.js` por um módulo vazio: a tela não dispara consultas."""
    page.route(
        re.compile(r"/js/main\.js$"),
        lambda route: route.fulfill(content_type="text/javascript", body=""),
    )


@pytest.fixture
def logic_page(page: Page) -> Page:
    """Página do servidor de testes com o `main.js` vazio."""
    empty_main(page)
    page.goto("/")
    return page


def evaluate(page: Page, module: str, body: str, arg=None):
    """Importa `/js/<module>` como `m` e executa `body` (corpo de função assíncrona)."""
    return page.evaluate(
        f"async (arg) => {{ const m = await import('/js/{module}'); {body} }}", arg
    )


# ---------- messages.js ----------


@pytest.mark.parametrize(("code", "expected"), SPEC_ERROR_MESSAGES.items())
def test_rnf_008_error_codes_translate_to_spec_messages(logic_page: Page, code, expected):
    """RNF-008, P-022: cada código de erro da seção 6.4 vira a mensagem do spec."""
    assert evaluate(logic_page, "messages.js", "return m.weatherErrorMessage(arg);", code) == (
        expected
    )


def test_p_004_unknown_error_code_never_reaches_the_user(logic_page: Page):
    """P-004: código desconhecido ou ausente vira a mensagem genérica, nunca o código."""
    messages = evaluate(
        logic_page,
        "messages.js",
        "return [m.weatherErrorMessage('erro_novo'), m.weatherErrorMessage(null)];",
    )
    assert messages == [SPEC_ERROR_MESSAGES["provider_unavailable"]] * 2


def test_rnf_008_error_messages_have_no_codes_or_technical_terms(logic_page: Page):
    """RNF-008, P-004: as mensagens de erro não têm códigos, números de status nem termos
    técnicos."""
    messages = evaluate(logic_page, "messages.js", "return Object.values(m.MESSAGES.errors);")
    technical = re.compile(r"_|\d|http|erro|error|timeout|api|json", re.IGNORECASE)
    for message in messages:
        assert not technical.search(message), message


def test_p_022_block_state_texts_come_from_the_spec(logic_page: Page):
    """P-022, RN-012, RF-013, RF-014: textos dos estados de bloco copiados do spec."""
    texts = evaluate(
        logic_page,
        "messages.js",
        "return [m.MESSAGES.stillLoading, m.MESSAGES.retry, m.MESSAGES.refreshing];",
    )
    assert texts == ["Ainda carregando…", "Tentar novamente", "Atualizando…"]


def test_p_022_messages_catalog_is_frozen(logic_page: Page):
    """Guardrail 10: o catálogo é a única fonte dos textos fixos e não pode ser alterado."""
    assert evaluate(
        logic_page,
        "messages.js",
        "return Object.isFrozen(m.MESSAGES) && Object.isFrozen(m.MESSAGES.errors);",
    )


# ---------- state.js ----------

INITIAL_STATE = {
    "city": None,
    "selectionId": 0,
    "scale": "c",
    "selectedDay": None,
    "weather": None,
    "weatherStatus": "idle",
    "weatherError": None,
    "fetchedAt": None,
    "locationNotice": False,
    "search": {"status": "idle", "results": [], "truncated": False, "message": None},
}


def test_state_starts_with_the_initial_state_of_section_6_5(logic_page: Page):
    """Seção 6.5, RF-054, RF-025: estado inicial com °C, aba "Hoje" e nada carregado."""
    assert evaluate(logic_page, "state.js", "return m.getState();") == INITIAL_STATE


def test_state_set_state_merges_patch_and_notifies_listeners(logic_page: Page):
    """Seção 6.5: `setState` aplica só as chaves do patch e avisa cada assinante com o estado
    novo e o anterior."""
    result = evaluate(
        logic_page,
        "state.js",
        """
        const calls = [];
        m.subscribe((state, previous) => calls.push([state.weatherStatus, previous.weatherStatus]));
        m.setState({ weatherStatus: 'loading', selectionId: 1 });
        const { scale, selectionId } = m.getState();
        return { calls, scale, selectionId };
        """,
    )
    assert result == {"calls": [["loading", "idle"]], "scale": "c", "selectionId": 1}


def test_state_unsubscribe_stops_notifications(logic_page: Page):
    """Seção 6.6: `subscribe` devolve a função que cancela a assinatura."""
    calls = evaluate(
        logic_page,
        "state.js",
        """
        let calls = 0;
        const unsubscribe = m.subscribe(() => { calls += 1; });
        m.setState({ scale: 'f' });
        unsubscribe();
        m.setState({ scale: 'c' });
        return calls;
        """,
    )
    assert calls == 1


def test_state_is_never_mutated_in_place(logic_page: Page):
    """Seção 6.5: cada `setState` cria um estado novo; o anterior continua como estava."""
    result = evaluate(
        logic_page,
        "state.js",
        """
        const before = m.getState();
        m.setState({ weatherStatus: 'ready' });
        return [before.weatherStatus, m.getState().weatherStatus, Object.isFrozen(m.getState())];
        """,
    )
    assert result == ["idle", "ready", True]


# ---------- services/cache.js ----------

TEN_MINUTES_MS = 600_000


@pytest.mark.parametrize(
    ("lat", "lon", "key"),
    [
        (-18.9186, -48.2772, "-18.92,-48.28"),
        (-18.9151, -48.2849, "-18.92,-48.28"),  # outra coordenada da mesma área de ~1 km
        (35.6895, 139.6917, "35.69,139.69"),
        (-0.001, 0.004, "0.00,0.00"),  # nunca "-0.00"
        (0, 180, "0.00,180.00"),
    ],
)
def test_rn_010_cache_key_rounds_coordinates_to_2_places(logic_page: Page, lat, lon, key):
    """RN-010: a chave do cache são as coordenadas arredondadas a 2 casas decimais."""
    assert (
        evaluate(logic_page, "services/cache.js", "return m.cacheKey(...arg);", [lat, lon]) == key
    )


def test_rn_010_cache_entry_is_valid_for_less_than_10_minutes(logic_page: Page):
    """RN-010, P-010: o dado vale por 10 min a partir do recebimento; com 10 min, venceu."""
    result = evaluate(
        logic_page,
        "services/cache.js",
        """
        const t0 = 1_000_000;
        m.set('k', { temp: 20 }, t0);
        return [
            m.get('k', t0),
            m.get('k', t0 + arg - 1),
            m.get('k', t0 + arg),
            m.get('k', t0),
        ];
        """,
        TEN_MINUTES_MS,
    )
    fresh = {"value": {"temp": 20}, "storedAt": 1_000_000}
    assert result == [fresh, fresh, None, None]  # o vencido sai do cache


def test_rn_010_cache_miss_for_unknown_key(logic_page: Page):
    """RN-010: sem dado guardado, `get` devolve `null`."""
    assert evaluate(logic_page, "services/cache.js", "return m.get('nada', 0);") is None


def test_rn_010_new_set_replaces_entry_and_restarts_validity(logic_page: Page):
    """RN-010: uma resposta nova substitui a anterior e a validade conta do novo recebimento."""
    result = evaluate(
        logic_page,
        "services/cache.js",
        """
        m.set('k', 'antigo', 0);
        m.set('k', 'novo', 500_000);
        return m.get('k', 500_000 + arg - 1);
        """,
        TEN_MINUTES_MS,
    )
    assert result == {"value": "novo", "storedAt": 500_000}


# ---------- services/api.js ----------

API_URL = re.compile(r"/api/")


def answer(page: Page, status=200, body=None, json=None):
    """Simula todo o `/api` com uma resposta fixa e devolve a lista de URLs pedidas."""
    urls = []

    def handle(route):
        urls.append(route.request.url)
        if json is not None:
            route.fulfill(status=status, json=json)
        else:
            route.fulfill(status=status, body=body or "", content_type="text/html")

    page.route(API_URL, handle)
    return urls


def test_rn_010_fetch_weather_sends_coordinates_rounded_to_2_places(logic_page: Page):
    """RN-010, P-008, seção 7.4: o `/api/weather` recebe as mesmas coordenadas da chave do
    cache, e a resposta de sucesso volta como `{ ok: true, data }`."""
    urls = answer(logic_page, json={"timezone_offset": -10800})

    result = evaluate(logic_page, "services/api.js", "return m.fetchWeather(-18.9186, -48.2772);")

    assert result == {"ok": True, "data": {"timezone_offset": -10800}}
    assert urls == [f"{logic_page.url}api/weather?lat=-18.92&lon=-48.28"]


@pytest.mark.parametrize(
    ("status", "code"),
    [
        (502, "provider_unauthorized"),
        (502, "provider_rate_limited"),
        (502, "provider_unavailable"),
        (504, "provider_timeout"),
        (502, "network_unavailable"),
        (400, "invalid_request"),
    ],
)
def test_p_004_api_errors_keep_only_the_code(logic_page: Page, status, code):
    """P-004, seção 6.4: um erro do backend vira `{ ok: false, error: <código> }`."""
    answer(logic_page, status=status, json={"error": code})

    result = evaluate(logic_page, "services/api.js", "return m.fetchWeather(-18.92, -48.28);")

    assert result == {"ok": False, "error": code}


@pytest.mark.parametrize(
    ("status", "body", "json"),
    [
        (500, "<h1>Internal Server Error</h1>", None),  # corpo que não é JSON
        (502, None, {"error": "codigo_novo"}),  # código fora da seção 6.4
        (502, None, {"detail": "x"}),  # sem o campo error
        (200, "não é JSON", None),  # sucesso com corpo inválido
    ],
)
def test_p_004_unexpected_api_answer_becomes_provider_unavailable(
    logic_page: Page, status, body, json
):
    """P-004: resposta fora do contrato nunca chega à tela; vira `provider_unavailable`."""
    answer(logic_page, status=status, body=body, json=json)

    result = evaluate(logic_page, "services/api.js", "return m.fetchWeather(-18.92, -48.28);")

    assert result == {"ok": False, "error": "provider_unavailable"}


def test_server_unreachable_when_backend_does_not_answer(logic_page: Page):
    """Seção 7.3: `fetch` ao próprio backend falhou (servidor parado) → `server_unreachable`."""
    logic_page.route(API_URL, lambda route: route.abort())

    result = evaluate(logic_page, "services/api.js", "return m.fetchWeather(-18.92, -48.28);")

    assert result == {"ok": False, "error": "server_unreachable"}


def test_network_unavailable_when_browser_is_offline(logic_page: Page):
    """Seção 7.3: sem rede (`navigator.onLine === false`), a falha vira `network_unavailable`."""
    evaluate(logic_page, "services/api.js", "return true;")  # módulo carregado antes
    logic_page.context.set_offline(True)
    try:
        result = evaluate(logic_page, "services/api.js", "return m.fetchWeather(-18.92, -48.28);")
    finally:
        logic_page.context.set_offline(False)

    assert result == {"ok": False, "error": "network_unavailable"}


def test_rf_015_identical_requests_in_progress_share_one_fetch(logic_page: Page):
    """RF-015, seção 7.4: pedidos idênticos em andamento recebem a mesma promessa; depois
    que ela termina, um pedido novo vai ao backend."""
    held = []
    logic_page.route(API_URL, lambda route: held.append(route))

    evaluate(
        logic_page,
        "services/api.js",
        """
        window.first = m.fetchWeather(-18.9186, -48.2772);
        window.second = m.fetchWeather(-18.9191, -48.2801);  // mesma área de ~1 km
        window.same = window.first === window.second;
        """,
    )
    logic_page.wait_for_timeout(200)
    assert len(held) == 1
    held[0].fulfill(json={"ok": 1})
    assert logic_page.evaluate("async () => [window.same, await window.second]") == [
        True,
        {"ok": True, "data": {"ok": 1}},
    ]

    evaluate(logic_page, "services/api.js", "window.third = m.fetchWeather(-18.92, -48.28);")
    logic_page.wait_for_timeout(200)
    assert len(held) == 2
    held[1].fulfill(json={"ok": 2})


def test_rn_012_request_guard_gives_up_after_17s_as_timeout(page: Page):
    """RN-012, seção 7.4: sem resposta em 17 s, o `api.js` cancela o pedido e devolve
    `provider_timeout` (o backend já desiste em 15 s)."""
    open_with_clock(page)
    held = []
    page.route(API_URL, lambda route: held.append(route))

    evaluate(page, "services/api.js", "window.result = m.fetchWeather(-18.92, -48.28);")
    page.wait_for_timeout(200)
    assert len(held) == 1
    page.clock.run_for(16_999)
    assert page.evaluate("Promise.race([window.result, 'pendente'])") == "pendente"
    page.clock.run_for(1)

    assert page.evaluate("window.result") == {"ok": False, "error": "provider_timeout"}


def test_p_003_search_term_and_coordinates_are_encoded_in_the_url(logic_page: Page):
    """P-003, RN-004: o termo vai como texto na query string; a geocodificação reversa e a
    busca devolvem `{ ok, data }` como as demais chamadas."""
    urls = answer(logic_page, json={"results": [], "truncated": False})

    result = evaluate(
        logic_page,
        "services/api.js",
        "return [await m.searchCities('<b>Rio</b> & Co'), await m.reverseGeocode(-18.9, -48.2)];",
    )

    assert result == [{"ok": True, "data": {"results": [], "truncated": False}}] * 2
    assert urls == [
        f"{logic_page.url}api/geo/search?q=%3Cb%3ERio%3C%2Fb%3E%20%26%20Co",
        f"{logic_page.url}api/geo/reverse?lat=-18.9&lon=-48.2",
    ]


# ---------- actions.js: selectCity e retry ----------

# Importa actions e state, e registra em `window.statuses` cada `weatherStatus` novo.
WATCH_JS = """async () => {
    window.actions = await import('/js/actions.js');
    window.state = await import('/js/state.js');
    window.statuses = [];
    window.state.subscribe((s, prev) => {
        if (s.weatherStatus !== prev.weatherStatus) window.statuses.push(s.weatherStatus);
    });
}"""


def watch(page: Page) -> None:
    page.evaluate(WATCH_JS)


def select(page: Page, city: dict) -> None:
    """Chama `selectCity` sem esperar: a promessa fica em `window.done`."""
    page.evaluate("(city) => { window.done = window.actions.selectCity(city); }", city)


def settle(page: Page) -> dict:
    """Espera `window.done` e devolve o estado com os status registrados."""
    page.evaluate("() => window.done")
    return page.evaluate("() => ({ ...window.state.getState(), statuses: window.statuses })")


def status(page: Page) -> str:
    return page.evaluate("() => window.state.getState().weatherStatus")


def open_with_clock(page: Page) -> None:
    """Página com o `main.js` vazio e o relógio simulado parado (ver `open_paused`)."""
    empty_main(page)
    open_paused(page)


def test_rf_004_selected_city_gets_one_weather_query(logic_page: Page, weather_api):
    """RF-004, RF-005, RF-031: a cidade escolhida entra no estado com status `loading`, aba
    "Hoje" e uma única consulta; a resposta vira `weather` com status `ready`."""
    watch(logic_page)
    select(logic_page, UBERLANDIA)
    state = settle(logic_page)

    assert state["statuses"] == ["loading", "ready"]
    assert state["city"] == UBERLANDIA
    assert state["selectionId"] == 1
    assert state["selectedDay"] is None
    assert state["weather"] == weather_api.views["uberlandia"]
    assert state["weatherError"] is None
    assert isinstance(state["fetchedAt"], int | float)
    assert len(weather_api.urls) == 1


def test_rn_010_city_in_cache_shows_at_once_without_query(logic_page: Page, weather_api):
    """RN-010, P-010, RNF-002: a cidade consultada há menos de 10 min volta do cache, sem
    consulta e sem passar por `loading`; `fetchedAt` continua o do recebimento."""
    watch(logic_page)
    select(logic_page, UBERLANDIA)
    first = settle(logic_page)
    logic_page.evaluate("() => { window.statuses = []; }")

    nearby = {**UBERLANDIA, "lat": -18.9191, "lon": -48.2801}  # mesma chave de cache
    select(logic_page, nearby)
    state = settle(logic_page)

    assert len(weather_api.urls) == 1
    assert state["statuses"] == []
    assert state["weatherStatus"] == "ready"
    assert state["city"] == nearby
    assert state["selectionId"] == 2
    assert state["fetchedAt"] == first["fetchedAt"]


def test_rn_010_cache_expires_after_10_minutes(page: Page, weather_api):
    """RN-010: com 10 min do recebimento, o cache venceu e a cidade é consultada de novo."""
    open_with_clock(page)
    watch(page)

    select(page, UBERLANDIA)
    settle(page)
    page.clock.run_for(TEN_MINUTES_MS - 1)
    select(page, UBERLANDIA)
    settle(page)
    assert len(weather_api.urls) == 1

    page.clock.run_for(1)
    select(page, UBERLANDIA)
    assert settle(page)["weatherStatus"] == "ready"
    assert len(weather_api.urls) == 2


def test_rn_011_failed_query_is_not_cached(logic_page: Page, weather_api):
    """RN-011, RF-013: a falha vira status `error` com o código, e nada vai para o cache:
    escolher a cidade de novo faz outra consulta."""
    weather_api.queue = [(502, "provider_unavailable")]
    watch(logic_page)

    select(logic_page, UBERLANDIA)
    state = settle(logic_page)
    assert state["statuses"] == ["loading", "error"]
    assert state["weatherError"] == "provider_unavailable"
    assert state["weather"] is None

    select(logic_page, UBERLANDIA)
    assert settle(logic_page)["weatherStatus"] == "ready"
    assert len(weather_api.urls) == 2


def test_rn_012_status_becomes_slow_after_3s_without_answer(page: Page, weather_api):
    """RN-012: depois de 3 s sem resposta, o status passa de `loading` para `slow`; a resposta
    que chega depois leva a `ready`."""
    open_with_clock(page)
    weather_api.hold = True
    watch(page)

    select(page, UBERLANDIA)
    page.clock.run_for(2_999)
    assert status(page) == "loading"
    page.clock.run_for(1)
    assert status(page) == "slow"

    weather_api.release()
    assert settle(page)["statuses"] == ["loading", "slow", "ready"]


def test_p_012_answer_for_previous_city_is_discarded(logic_page: Page, weather_api):
    """P-012, RN-013: com A escolhida e depois B, a resposta de A que chega por último não
    aparece; ela vai para o cache, e voltar para A não consulta de novo (P-010)."""
    weather_api.hold = True
    watch(logic_page)
    select(logic_page, UBERLANDIA)
    logic_page.evaluate("() => { window.first = window.done; }")
    select(logic_page, TOKYO)
    weather_api.wait_for_held(2)

    weather_api.release(1)  # B (Tóquio) responde primeiro
    settle(logic_page)
    weather_api.release(0)  # A (Uberlândia) responde depois
    logic_page.evaluate("() => window.first")
    state = settle(logic_page)

    assert state["city"] == TOKYO
    assert state["weather"] == weather_api.views["tokyo"]
    assert state["statuses"] == ["loading", "ready"]

    weather_api.hold = False
    select(logic_page, UBERLANDIA)
    assert settle(logic_page)["weather"] == weather_api.views["uberlandia"]
    assert len(weather_api.urls) == 2


def test_p_012_slow_timer_of_previous_city_does_not_touch_the_new_one(page: Page, weather_api):
    """P-012, RN-012: o prazo de 3 s da cidade anterior não marca a nova como `slow`."""
    open_with_clock(page)
    weather_api.hold = True
    watch(page)

    select(page, UBERLANDIA)
    page.clock.run_for(2_000)
    select(page, TOKYO)
    page.clock.run_for(1_500)  # 3,5 s depois de A, 1,5 s depois de B

    assert status(page) == "loading"


def test_rn_013_retry_repeats_only_the_failed_query_once(logic_page: Page, weather_api):
    """RN-013, RF-013, RF-015: "Tentar novamente" refaz a consulta da cidade atual; vários
    cliques geram uma única consulta, e sem erro o retry não faz nada."""
    weather_api.queue = [(504, "provider_timeout")]
    watch(logic_page)
    select(logic_page, UBERLANDIA)
    assert settle(logic_page)["weatherError"] == "provider_timeout"

    logic_page.evaluate(
        "() => { window.done = Promise.all([1, 2, 3].map(() => window.actions.retry())); }"
    )
    state = settle(logic_page)
    assert state["statuses"] == ["loading", "error", "loading", "ready"]
    assert state["selectionId"] == 1
    assert len(weather_api.urls) == 2

    logic_page.evaluate("() => { window.done = window.actions.retry(); }")
    settle(logic_page)
    assert len(weather_api.urls) == 2


def test_rn_001_default_city_is_uberlandia(logic_page: Page):
    """RN-001: a cidade padrão é Uberlândia, BR (lat -18.9186, lon -48.2772)."""
    city = evaluate(logic_page, "actions.js", "return m.DEFAULT_CITY;")
    assert city == {**UBERLANDIA, "source": "default"}


# ---------- ui/dom.js ----------


def test_p_003_el_puts_text_as_text_never_as_markup(logic_page: Page):
    """P-003, seção 8.2: `el()` cria o elemento e põe o texto por `textContent`."""
    result = evaluate(
        logic_page,
        "ui/dom.js",
        """
        const node = m.el('p', { class: 'a b', text: '<b>Rio</b>', attrs: { title: 'x' } },
                          [m.el('span', { text: 'filho' })]);
        return [node.outerHTML, node.children.length];
        """,
    )
    assert result == ['<p class="a b" title="x">&lt;b&gt;Rio&lt;/b&gt;<span>filho</span></p>', 1]


def test_p_003_set_text_replaces_text_and_accepts_missing_value(logic_page: Page):
    """P-003: `setText()` troca o texto do nó; valor ausente vira texto vazio."""
    result = evaluate(
        logic_page,
        "ui/dom.js",
        """
        const node = m.el('p', { text: 'antes' });
        m.setText(node, '<i>depois</i>');
        const first = node.innerHTML;
        m.setText(node, null);
        return [first, node.textContent];
        """,
    )
    assert result == ["&lt;i&gt;depois&lt;/i&gt;", ""]


@pytest.mark.parametrize(
    ("status", "error", "weather", "expected"),
    [
        ("idle", None, None, {"kind": "loading"}),
        ("loading", None, None, {"kind": "loading"}),
        ("slow", None, None, {"kind": "slow", "message": "Ainda carregando…"}),
        (
            "error",
            "provider_rate_limited",
            None,
            {
                "kind": "error",
                "message": "Limite de consultas ao serviço de clima atingido. "
                "Tente novamente em alguns minutos.",
            },
        ),
        ("ready", None, {"daily": [{}]}, {"kind": "ready"}),
        ("ready", None, {"daily": None}, {"kind": "unavailable", "message": "Indisponível."}),
        ("refreshing", None, {"daily": [{}]}, {"kind": "refreshing", "message": "Atualizando…"}),
    ],
)
def test_p_020_block_state_derives_from_weather_status(
    logic_page: Page, status, error, weather, expected
):
    """P-020, RF-005, RF-013, RN-012, seção 6.5: o estado de cada bloco é derivado do status
    da consulta e da parte do bloco no view model, nunca guardado."""
    result = evaluate(
        logic_page,
        "ui/dom.js",
        "return m.blockState(arg, { part: 'daily', unavailable: 'Indisponível.' });",
        {"weatherStatus": status, "weatherError": error, "weather": weather},
    )
    assert result == expected


def test_p_020_block_without_part_is_never_unavailable(logic_page: Page):
    """Seção 6.5: um bloco sem parte própria no view model fica `ready` com os dados."""
    result = evaluate(
        logic_page,
        "ui/dom.js",
        "return m.blockState({ weatherStatus: 'ready', weather: { daily: null } });",
    )
    assert result == {"kind": "ready"}


# Bloco de teste com um título e um conteúdo, como os da fatia 5.
BLOCK_JS = """
    const block = m.el('section', {}, [
        m.el('h2', { class: 'panel-title', text: 'Título' }),
        m.el('p', { class: 'content', text: 'dados' }),
    ]);
    document.body.append(block);
    const visible = (selector) => {
        const node = block.querySelector(selector);
        return Boolean(node) && node.checkVisibility();
    };
    const snapshot = () => ({
        state: block.dataset.blockState,
        busy: block.getAttribute('aria-busy'),
        text: block.querySelector('.block-state').textContent,
        title: visible('.panel-title'),
        content: visible('.content'),
        button: visible('.block-state button'),
    });
"""


def test_rf_005_render_block_state_shows_each_state(logic_page: Page):
    """RF-005, RF-013, RN-012, P-020: carregamento com ícone e nome acessível, "Ainda
    carregando…", erro com "Tentar novamente", indisponível e "Atualizando…" com os dados
    antigos visíveis."""
    result = evaluate(
        logic_page,
        "ui/dom.js",
        BLOCK_JS
        + """
        const out = {};
        for (const view of [
            { kind: 'loading' },
            { kind: 'slow', message: 'Ainda carregando…' },
            { kind: 'error', message: 'Falhou.' },
            { kind: 'unavailable', message: 'Indisponível.' },
            { kind: 'refreshing', message: 'Atualizando…' },
            { kind: 'ready' },
        ]) {
            m.renderBlockState(block, view, { onRetry() {} });
            out[view.kind] = snapshot();
        }
        out.spinner = (m.renderBlockState(block, { kind: 'loading' }),
                       visible('.block-state-spinner'));
        return out;
        """,
    )
    expected = {
        "loading": ("true", "Carregando…", False, False),
        "slow": ("true", "Ainda carregando…", False, False),
        "error": ("false", "Falhou.Tentar novamente", False, True),
        "unavailable": ("false", "Indisponível.", False, False),
        "refreshing": ("true", "Atualizando…", True, False),
        "ready": ("false", "", True, False),
    }
    for kind, (busy, text, content, button) in expected.items():
        snap = result[kind]
        assert snap["state"] == kind
        assert snap["busy"] == busy, kind
        assert snap["text"] == text, kind
        assert snap["title"] is True, kind  # o título do bloco continua visível
        assert snap["content"] is content, kind
        assert snap["button"] is button, kind
    assert result["spinner"] is True


def test_rf_013_retry_button_calls_handler_and_survives_rerender(logic_page: Page):
    """RF-013, RNF-008: o botão "Tentar novamente" chama `onRetry`; redesenhar o mesmo erro
    não recria o botão, e o foco do teclado continua nele."""
    result = evaluate(
        logic_page,
        "ui/dom.js",
        BLOCK_JS
        + """
        let calls = 0;
        const options = { onRetry() { calls += 1; } };
        m.renderBlockState(block, { kind: 'error', message: 'Falhou.' }, options);
        const button = block.querySelector('.block-state button');
        button.focus();
        m.renderBlockState(block, { kind: 'error', message: 'Falhou.' }, options);
        const same = block.querySelector('.block-state button') === button;
        button.click();
        return [calls, same, document.activeElement === button, button.type];
        """,
    )
    assert result == [1, True, True, "button"]


# ---------- logic/time-window.js: dias ----------

# 00:00 de terça, 06/10/2026, em Uberlândia (03:00 UTC).
UBERLANDIA_MIDNIGHT = 1791255600
UBERLANDIA_OFFSET = -10800
TOKYO_OFFSET = 32400


def visible_dates(page: Page, daily, now_sec: int, offset: int) -> list[str]:
    return evaluate(
        page,
        "logic/time-window.js",
        "return m.visibleDays(arg.daily, arg.now, arg.offset).map((day) => day.local_date);",
        {"daily": daily, "now": now_sec, "offset": offset},
    )


def test_rn_026_city_today_is_the_date_in_the_city_timezone(logic_page: Page):
    """RN-026, P-015: "Hoje" é a data atual no fuso da cidade. No momento da captura (19:41
    UTC de segunda, 05/10), já é terça em Tóquio; e a data de Uberlândia vira à meia-noite
    local, não à meia-noite UTC."""
    result = evaluate(
        logic_page,
        "logic/time-window.js",
        """return [
            m.cityToday(arg.capture, arg.uberlandia),
            m.cityToday(arg.capture, arg.tokyo),
            m.cityToday(arg.midnight - 1, arg.uberlandia),
            m.cityToday(arg.midnight, arg.uberlandia),
        ];""",
        {
            "capture": CAPTURE_NOW,
            "uberlandia": UBERLANDIA_OFFSET,
            "tokyo": TOKYO_OFFSET,
            "midnight": UBERLANDIA_MIDNIGHT,
        },
    )
    assert result == ["2026-10-05", "2026-10-06", "2026-10-05", "2026-10-06"]


def test_rn_027_visible_days_start_today_and_stop_at_8(logic_page: Page, weather_views):
    """RN-026, RN-027, D-14: dos 10 dias da captura, ficam 8 a partir de "Hoje". Em Tóquio,
    o primeiro dia recebido (05/10) já é passado e é descartado, e ainda sobram 8."""
    uberlandia = weather_views["uberlandia"]["daily"]
    tokyo = weather_views["tokyo"]["daily"]

    days = visible_dates(logic_page, uberlandia, CAPTURE_NOW, UBERLANDIA_OFFSET)
    assert days == [f"2026-10-{day:02d}" for day in range(5, 13)]
    days = visible_dates(logic_page, tokyo, CAPTURE_NOW, TOKYO_OFFSET)
    assert days == [f"2026-10-{day:02d}" for day in range(6, 14)]


def test_rn_026_cached_days_cross_the_city_midnight(logic_page: Page, weather_views):
    """RN-026, feature 3 (categoria 8): com os mesmos dados, o dia que virou passado à
    meia-noite da cidade é descartado e o seguinte passa a ser o primeiro. Perto do fim da
    previsão, sobram menos de 8 dias."""
    daily = weather_views["uberlandia"]["daily"]

    before = visible_dates(logic_page, daily, UBERLANDIA_MIDNIGHT - 1, UBERLANDIA_OFFSET)
    after = visible_dates(logic_page, daily, UBERLANDIA_MIDNIGHT, UBERLANDIA_OFFSET)
    last_days = visible_dates(logic_page, daily, UBERLANDIA_MIDNIGHT + 7 * 86400, UBERLANDIA_OFFSET)

    assert before[0] == "2026-10-05"
    assert after[0] == "2026-10-06"
    assert len(after) == 8
    assert last_days == ["2026-10-13", "2026-10-14"]


def test_rn_026_visible_days_are_chronological_and_absent_daily_is_empty(logic_page: Page):
    """RN-026, RF-024: os dias saem em ordem cronológica mesmo fora de ordem na entrada, e
    sem previsão diária não há dias."""
    daily = [{"local_date": date} for date in ("2026-10-07", "2026-10-05", "2026-10-06")]

    assert visible_dates(logic_page, daily, CAPTURE_NOW, UBERLANDIA_OFFSET) == [
        "2026-10-05",
        "2026-10-06",
        "2026-10-07",
    ]
    assert visible_dates(logic_page, None, CAPTURE_NOW, UBERLANDIA_OFFSET) == []


def test_rf_028_active_day_is_null_for_today_and_for_days_gone(logic_page: Page, weather_views):
    """RF-025, RF-028, seção 7.4 (feature 3, categoria 8): o dia ativo é o selecionado se
    ele ainda estiver entre os visíveis. "Hoje" (`null` ou a data de hoje) e um dia que virou
    passado dão `null`, ou seja, as condições atuais."""
    result = evaluate(
        logic_page,
        "logic/time-window.js",
        """const days = m.visibleDays(arg.daily, arg.now, arg.offset);
        const active = (selected) => m.activeDay(days, selected, arg.now, arg.offset);
        return [
            active(null),
            active('2026-10-05'),
            active('2026-10-08')?.local_date,
            active('2026-10-04'),
            active('2026-10-20'),
        ];""",
        {
            "daily": weather_views["uberlandia"]["daily"],
            "now": CAPTURE_NOW,
            "offset": UBERLANDIA_OFFSET,
        },
    )
    assert result == [None, None, "2026-10-08", None, None]
