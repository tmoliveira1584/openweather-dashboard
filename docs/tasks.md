# Tarefas de implementação — OpenWeather Dashboard (MVP)

Lista de tarefas que leva a aplicação de zero a 100% dos requisitos, uma fatia por vez. Detalha a seção 10 de [arquitetura.md](arquitetura.md) e é o ponto de partida de toda sessão de implementação.

- **Precedência:** [constitution.md](constitution.md) > [spec.md](spec.md) > [arquitetura.md](arquitetura.md) > este arquivo. Este arquivo não repete contratos nem regras: ele aponta para as seções da arquitetura e para os IDs do spec. Se algo aqui contrariar a arquitetura, corrija este arquivo.
- **Escopo:** 217 IDs rastreáveis: 58 RF, 59 RN, 29 RNF e 44 CA do spec, mais os princípios P-001 a P-027.

## Onde paramos

> Atualize este bloco ao concluir cada tarefa, antes de passar para a próxima. Ele vai para o Git no commit do fim da fatia (D-06).

| Item | Valor |
|---|---|
| Fatia atual | 9 — Hora a hora (não iniciada) |
| Próxima tarefa | T-9.1 |
| Concluídas, ainda sem commit | — |
| Último commit de implementação | Fatia 8, commit `feat(ui): exibir a previsão diária em abas com o resumo de cada dia` de 2026-10-06 (o hash é registrado aqui no início da fatia 9). Fatia 7: `320a0b8`. Fatia 6c: `38d51e0`. Fatia 6b: `30b078a`. Fatia 6a: `f442956`. Fatia 5: `ecc8bf0`. Fatia 4: `4ee7d59`. Fatia 3: `8f56a1a`. Fatia 2: `8fb0ce7`. Fatia 1: `b5ff9c1`. Fatia 0: `880fa41` |
| IDs fechados | 129 de 217 (59,4%) |

## Como usar

1. **Ao abrir uma sessão:** leia o [CLAUDE.md](../CLAUDE.md), o bloco "Onde paramos" e as seções da arquitetura citadas na fatia atual. Rode `git status`: os arquivos não commitados são o trabalho da fatia atual já registrado em "Onde paramos".
2. **Antes de codificar:** explique a decisão da próxima tarefa não marcada e aguarde a confirmação (CLAUDE.md). Use o modelo de pedido da seção 10 da arquitetura, se quiser registrar o prompt com `/costar`.
3. **Ordem dentro da tarefa:** testes dos IDs primeiro (nome `test_<id>_<comportamento>`, seção 9.3), depois o código.
4. **Marcar o ✓:** ao concluir uma tarefa, marque `[x]` e atualize "Onde paramos" **na hora**, sem esperar o commit. Assim, uma nova sessão sabe onde continuar mesmo com o trabalho ainda sem commit.
5. **Fechar a fatia:** quando todas as tarefas e a definição de pronto (seção 9.4 da arquitetura) estiverem marcadas, atualize a tabela "Progresso" com os IDs que a fatia fecha.
6. **Trabalho não previsto:** se surgir algo fora da lista, acrescente uma tarefa nova na fatia (ex.: T-7.7) antes de fazê-la. Se um contrato mudar, atualize a arquitetura antes do código.
7. **Um commit por fatia:** as tarefas ficam na pasta de trabalho até a última da fatia, que cumpre a definição de pronto e faz um único commit com o código, as marcações e a tabela "Progresso" (D-06). Uma tarefa cabe numa sessão.

**O que "fecha" quer dizer:** cada ID tem uma única fatia em que fica totalmente atendido e testado, listada na linha **Fecha** dela. Uma fatia anterior pode ter testes de unidade que citam o mesmo ID (ex.: CA-039 nas regras de conversão da fatia 1), mas o ID só conta como fechado na fatia indicada.

## Progresso

| Fatia | Nome | IDs que fecha | Status |
|---|---|---|---|
| 0 | Setup | 1 | Concluída |
| 1 | Domínio: formatação, unidades e horas | 12 | Concluída |
| 2 | Domínio: regras de clima | 11 | Concluída |
| 3 | View model | 3 | Concluída |
| 4 | Cliente e rotas | 4 | Concluída |
| 5 | Estrutura da tela | 1 | Concluída |
| 6a | Estado, cache e chamadas ao backend | 13 | Concluída |
| 6b | Cabeçalho, busca e seletor de escala | 24 | Concluída |
| 6c | Localização inicial e cidade padrão | 12 | Concluída |
| 7 | Condições atuais | 23 | Concluída |
| 8 | Previsão diária | 25 | Concluída |
| 9 | Hora a hora | 23 | Pendente |
| 10 | Por minuto | 22 | Pendente |
| 11 | Mapa | 24 | Pendente |
| 12 | Robustez, desempenho e acessibilidade | 15 | Pendente |
| 13 | Fechamento | 4 | Pendente |
| | **Total** | **217** | **59,4%** |

---

## Fatia 0 — Setup

Arquitetura: seções 1, 5.1, 7.6, 9.1, 9.2 e 11. **Pré-requisito:** `.env` com a chave e a assinatura "One Call by Call" da One Call 4.0 ativa (a T-0.8 usa 10 chamadas da One Call e 3 de geocodificação).

- [x] **T-0.1** Criar o ambiente conda (`conda env create -f environment.yml`) e conferir `python --version` (3.13.5) e `pip check`.
- [x] **T-0.2** Criar o `pyproject.toml` só com a configuração de ferramentas: pytest (`testpaths`, marcadores `e2e` e `live`, `addopts`) e ruff (`line-length = 100`, `target-version = "py313"`).
- [x] **T-0.3** `app/config.py`: ler `OPENWEATHER_API_KEY` do ambiente e falhar ao iniciar se ela não existir. Teste em `tests/unit/test_config.py`. (P-002)
- [x] **T-0.4** `app/logging_setup.py`: middleware que registra `método rota status duração` (modelo da rota, ou caminho sem query se não houver rota), e loggers `httpx`/`httpcore` em `WARNING`. (P-001, P-006)
- [x] **T-0.5** `app/main.py`: `create_app(client=None)` com o `lifespan` do `httpx.AsyncClient` e `StaticFiles` servindo um `static/index.html` mínimo com `<html lang="pt-BR">`.
- [x] **T-0.6** Copiar o Leaflet 1.9.4 para `static/vendor/leaflet-1.9.4/` (`leaflet.js`, `leaflet.css`, `images/`) e registrar a origem, a versão e o SHA-256 em `static/vendor/README.md`.
- [x] **T-0.7** `tests/conftest.py`: fixtures para carregar JSON, app com cliente simulado (`httpx.MockTransport`) e `live_server` numa thread. Interceptar `/api/*`, as tiles do CARTO e os ícones do OpenWeatherMap, para os testes de ponta a ponta rodarem sem internet. Incluir um teste de fumaça que abre a página no Chrome (`--browser-channel chrome`).
- [x] **T-0.8** Capturar as fixtures reais da One Call 4.0 de Uberlândia e de Tóquio, uma por endpoint (`onecall4/<cidade>/current.json`, `1min.json`, `1h_p1.json`, `1h_p2.json` e `1day.json`), e as de geocodificação (`geo_direct_santa_maria.json`, `geo_direct_empty.json` e `geo_reverse_uberlandia.json`). Não gravar a chave e remover os campos `next`/`prev`, que a contêm. Descrever a origem em `tests/fixtures/README.md` e registrar ali o que as capturas mostram sobre as lacunas da documentação (risco da seção 13 da arquitetura). Conferir com `git grep` que a chave não aparece. (P-001, ADR-013)
- [x] **T-0.10** (não prevista) Ajustar spec, arquitetura e tarefas aos achados da T-0.8: data de cada dia da previsão diária, alertas por dia e primeiro minuto da previsão por minuto. Fica antes da T-0.9, que fecha a fatia.
- [x] **T-0.9** Definição de pronto (seção 9.4) + commit. Sugestão: `build: configurar ambiente, app mínimo e fixtures reais`.

**Fecha:** P-002

## Fatia 1 — Domínio: formatação, unidades e horas

Arquitetura: seções 6.3, 6.6, 7.5 e 8.1. Testes em `tests/unit/`.

- [x] **T-1.1** `domain/formatting.py`: `format_number` (vírgula, sem separador de milhar, nunca "-0") e `format_temp` (com "°" ou com a escala completa), mais os formatos de umidade, visibilidade, pressão, índice UV e ponto de orvalho. (RN-014, RN-020 a RN-025)
- [x] **T-1.2** `domain/units.py`: `celsius_to_fahrenheit` e `ms_to_mph`, sempre a partir do valor original. Testes com 20,4 °C → "69°", alternância repetida sem erro acumulado, -40 °C e -17,8 °C → "0°". (RN-053 a RN-055, P-014)
- [x] **T-1.3** `domain/time.py`: `local_datetime`, `time_label`, `hour_label`, `weekday_label`, `date_label` e `local_date`, com `dt + offset` em UTC e nunca o fuso da máquina. Testes com Uberlândia e Tóquio. (RN-015, RN-028, RN-030, RN-035)
- [x] **T-1.4** Definição de pronto + commit.

**Fecha:** RN-014, RN-015, RN-020, RN-021, RN-022, RN-023, RN-024, RN-025, RN-053, RN-054, RN-055, P-014

## Fatia 2 — Domínio: regras de clima

Arquitetura: seções 6.3 e 6.6. Testes em `tests/unit/`.

- [x] **T-2.1** `domain/conditions.py`: `condition_group` por faixa de código (fora das faixas → `neutral`), `wind_direction` na rosa de 8 pontos (0° e 360° → "N", limites dos setores) e `wind_label` ("Calmo" abaixo de 0,5 m/s originais, só a velocidade se faltar a direção). (RN-017, RN-019)
- [x] **T-2.2** `domain/precipitation.py`: `pop_label`, `rain_label` (2 casas, `null` quando arredonda para 0), `intensity_band` (limite superior incluído, negativo ou não numérico → `None`) e `minute_tooltip`. (RN-036, RN-037, RN-041, RN-045)
- [x] **T-2.3** `domain/alerts.py`: `alerts_label` ("1 alerta", "N alertas", "99+ alertas", `None` com 0) `count_alert_ids` (IDs distintos e não vazios, lista ausente = 0, para o selo de "Hoje") e `count_alerts_on_day` (sobreposição maior que zero, alerta sem início ou fim conta em todos os dias, fim às 00:00 conta só no dia anterior). (RN-018, RN-032)
- [x] **T-2.4** `domain/places.py`: `city_option` com nome em português ou o nome padrão, e os rótulos do cabeçalho, da lista e do marcador. (RN-006 a RN-008)
- [x] **T-2.5** Definição de pronto + commit.

**Fecha:** RN-006, RN-007, RN-008, RN-017, RN-018, RN-019, RN-032, RN-036, RN-037, RN-041, RN-045

## Fatia 3 — View model

Arquitetura: seções 6.2, 6.3 e 9.2. Testes em `tests/unit/test_view_model.py`.

- [x] **T-3.1** `clients/openweather.py`, só a função pura `merge_onecall` (seção 6.2, ADR-013): combina as respostas da One Call 4.0 no pacote, une as 2 páginas por hora sem repetir `dt`, descarta `next`/`prev`, deixa o bloco ausente quando a resposta é `None` (404) ou tem `data` vazia e junta em `alerts` o detalhe de cada alerta. Testar com as capturas da T-0.8. Depois, criar os pacotes variantes `onecall_no_minutely.json`, `onecall_partial.json`, `onecall_alerts.json` e `onecall_minutely_bands.json` a partir do pacote de Uberlândia, com a origem e a alteração descritas em `tests/fixtures/README.md`.
- [x] **T-3.2** `schemas/provider.py`: modelos do pacote (`OneCallBundle`, seção 6.2) e da geocodificação, com todos os campos opcionais, `extra="ignore"`, e valor fora do formato vira `None` em vez de erro 500.
- [x] **T-3.3** `schemas/view.py`: `WeatherView`, `Scaled`, `CitySearchResult`, `ReverseResult` e os `Literal` (`Scale`, `ConditionGroup`, `Band`).
- [x] **T-3.4** `view_model.build_weather_view`: blocos `current`, `daily`, `hourly` e `minutely` conforme a tabela de regras da seção 6.3. Descrição com inicial maiúscula e "Sensação de", dia da semana só às 00:00, `"—"` e `null` para ausentes, bloco ausente ou vazio → `null`, `daily` com todos os dias recebidos (o limite de 8 fica no frontend, D-14), data do dia pela data UTC do `dt` (funções de data com `offset = 0`), visibilidade do dia quando houver, selo de "Hoje" pelos IDs de `current.alerts` e selo de cada dia pela vigência (RN-032). Testar contra o exemplo JSON da seção 6.3. (RN-016, RN-035, P-013)
- [x] **T-3.5** `view_model.build_search_result`: até 5 itens, `truncated` com exatamente 5, lista vazia sem resultados.
- [x] **T-3.6** Definição de pronto + commit.

**Fecha:** RN-016, RN-035, P-013

## Fatia 4 — Cliente e rotas

Arquitetura: seções 6.1, 6.4, 7.6 e ADR-003. Testes em `tests/api/` com `TestClient` e `httpx.MockTransport`.

- [x] **T-4.1** `clients/openweather.py`: `OpenWeatherClient(http, api_key, clock)` com `weather`, `geocode` (`limit=5`), `reverse` (`limit=1`) e `tile`, tempo limite de 15 s por chamada e `ProviderError` com os códigos da seção 6.4 (401/403, 429, outros erros, JSON inválido, `TimeoutException`, `ConnectError`). O `weather` faz as 5 chamadas em paralelo do ADR-013 (`units=metric`, `lang=pt_br`, `start` da previsão por hora pelo relógio injetado), trata 404 numa previsão como bloco ausente, busca numa segunda rodada o detalhe de cada alerta distinto (404 → alerta sem vigência), aplica a precedência de erros da seção 6.4 e devolve o pacote de `merge_onecall`. (RN-012, RN-059)
- [x] **T-4.2** `api/routes.py`: as 4 rotas, com validação antes de chamar o provedor (lat/lon, termo de 2 a 100 caracteres sem os espaços das pontas, z/x/y), `400 invalid_request` no lugar do 422 e `Cache-Control: no-store`. (RN-004)
- [x] **T-4.3** Tratadores de exceção em `main.py`: formato `{"error": "<código>"}`, 502/504, sem repassar o corpo do provedor. (P-004)
- [x] **T-4.4** Testes de segurança: com uma chave falsa de teste, ela não aparece em nenhuma resposta, cabeçalho ou log (`caplog`), e o log não contém query string nem coordenadas. Os links `next`/`prev` de uma resposta simulada do provedor não aparecem na resposta do `/api/weather` nem no log (guardrail 13). (RNF-004, P-001, P-006)
- [x] **T-4.5** Definição de pronto + commit.

**Fecha:** RN-059, RNF-004, P-001, P-006

## Fatia 5 — Estrutura da tela

Arquitetura: seções 7.1 e 8.4. Referência: [print](referencia/referencia_visual.png). Os textos de exemplo desta fatia são provisórios e saem nas fatias 6a a 11, quando os textos passam a vir do `messages.js` e do view model (guardrail 10).

- [x] **T-5.1** `static/index.html`: esqueleto semântico com cabeçalho, faixa de abas, card principal e 6 indicadores, bloco hora a hora, mapa e painel por minuto. Carregar o `main.js` como módulo e o Leaflet copiado.
- [x] **T-5.2** `static/css/tokens.css` com os tokens da seção 7.1.
- [x] **T-5.3** `static/css/styles.css`: layout do print com CSS Grid e Flexbox, breakpoint de 600 px, largura mínima de 360 px sem rolagem horizontal da página, faixa de abas com rolagem própria, indicadores em 3/2 colunas, painel por minuto sobreposto ou abaixo do mapa e altura mínima do mapa de 300 px. (RNF-011)
- [x] **T-5.4** `tests/e2e/test_layout.py`: larguras de 360, 599, 600 e 1280 px, sem rolagem horizontal da página e com o número certo de colunas nos indicadores.
- [x] **T-5.5** Definição de pronto, com conferência visual contra o print, + commit.

**Fecha:** RNF-011

## Fatia 6a — Estado, cache e chamadas ao backend

Arquitetura: seções 6.5, 6.6, 7.3 e 7.4. Testes de lógica em `tests/e2e/test_js_logic.py` (`page.evaluate`) e de interface em `tests/e2e/test_f1_loading.py`.

- [x] **T-6a.1** `messages.js`: objeto `MESSAGES` com os textos fixos copiados literalmente do spec e a tradução dos códigos de erro da seção 7.3. (RNF-008, P-022)
- [x] **T-6a.2** `state.js`: `getState`, `setState` e `subscribe`, com o estado inicial da seção 6.5.
- [x] **T-6a.3** `services/cache.js`: `cacheKey` com 2 casas, `get` e `set` com `nowMs`, validade de 10 min, só respostas de sucesso. (RN-010, RN-011, P-010)
- [x] **T-6a.4** `services/api.js`: `fetchWeather` (coordenadas arredondadas a 2 casas), `searchCities` e `reverseGeocode`, retorno `{ ok, data | error }`, `server_unreachable`, trava de 17 s e promessas em andamento compartilhadas por URL.
- [x] **T-6a.5** `actions.js`: `selectCity` (incrementa `selectionId`, status `loading`, consulta o cache, `slow` após 3 s, descarta resposta antiga, grava no cache) e `retry` (refaz só a consulta que falhou). (RF-004, RN-012, P-012)
- [x] **T-6a.6** `ui/dom.js`: `el()`, `setText()` e os estados de bloco (carregando, "Ainda carregando…", erro com "Tentar novamente", indisponível, "Atualizando…"), aplicados aos blocos da fatia 5. (RF-005, RF-013, P-020)
- [x] **T-6a.7** `main.js` provisório: monta os blocos e seleciona a cidade padrão direto (a localização entra na 6c).
- [x] **T-6a.8** Testes de ponta a ponta com `page.route` e `page.clock`: carregamento, "Ainda carregando…", cada código de erro com sua mensagem e "Tentar novamente", acerto de cache sem consulta, erro que não vai para o cache e resposta de cidade antiga descartada. (CA-008, P-004)
- [x] **T-6a.9** Definição de pronto + commit.

**Fecha:** RF-004, RF-005, RF-013, RN-010, RN-011, RN-012, RNF-008, CA-008, P-004, P-010, P-012, P-020, P-022

## Fatia 6b — Cabeçalho, busca e seletor de escala

Arquitetura: seções 6.3, 6.5, 7.3 e 7.4. Testes em `tests/e2e/test_f1_search.py` e `tests/e2e/test_f7_scale_selector.py`.

- [x] **T-6b.1** `ui/header.js`: título e cidade selecionada (`header_label`), atualizada na hora da troca, cortada com "…" e com o nome completo ao passar o cursor ou focar. (RF-010, RN-013)
- [x] **T-6b.2** Campo de busca: rótulo acessível "Buscar cidade", `maxlength` 100, confirmação por Enter ou lupa, validação de campo vazio e de 1 caractere com o foco mantido no campo. (RF-006, RN-004)
- [x] **T-6b.3** `actions.search` e `closeSearch`: lista de resultados (combobox ARIA) com estados `loading`, `open`, `empty` e `error`, seleção direta com resultado único, escolha que seleciona, fecha e limpa o campo, Esc ou clique fora, mensagem de nenhum resultado, dica das 5 primeiras, erro da busca, pedidos repetidos ignorados, termo e resultados sempre como texto. (RF-007 a RF-009, RF-011, RF-012, RF-015, RN-005, P-003)
- [x] **T-6b.4** Teclado na lista: setas, Enter e Esc. (RNF-007)
- [x] **T-6b.5** Seletor °C/°F: inicia em °C, `aria-pressed` e destaque além da cor, `setScale` muda só o estado (zero consultas) e nada é persistido. (RF-053, RF-054, RN-058, RNF-027, RNF-028)
- [x] **T-6b.6** Testes de ponta a ponta: CA-004, CA-005, CA-006, CA-007 (escolher de novo uma cidade em cache) e CA-044, contagem de consultas (RNF-003), `<b>Rio</b>` exibido como texto e campo de busca em 360 px.
- [x] **T-6b.7** Definição de pronto + commit.

**Fecha:** RF-006, RF-007, RF-008, RF-009, RF-010, RF-011, RF-012, RF-015, RF-053, RF-054, RN-004, RN-005, RN-013, RN-058, RNF-003, RNF-007, RNF-027, RNF-028, CA-004, CA-005, CA-006, CA-007, CA-044, P-003

## Fatia 6c — Localização inicial e cidade padrão

Arquitetura: seções 2.2 e 7.4. Testes em `tests/e2e/test_f1_location.py`, com permissões e geolocalização simuladas e `page.clock` para o prazo de 10 s.

- [x] **T-6c.1** `services/location.js`: `requestLocation({ timeoutMs, onLate })` com `setTimeout` próprio de 10 s e as opções da seção 7.4. Recurso ausente ou contexto inseguro → `unavailable`. (P-005)
- [x] **T-6c.2** `actions.start()`: localização obtida → geocodificação reversa → `header_label` ou "Sua localização" → `selectCity`. Indisponível → `DEFAULT_CITY` (Uberlândia) com o aviso. Substitui o `main.js` provisório da 6a. (RF-001 a RF-003, RN-001, RN-009)
- [x] **T-6c.3** Localização tardia: aplicada se a cidade ainda for a padrão, descartada se o usuário já escolheu outra. (RN-003)
- [x] **T-6c.4** Aviso de localização no cabeçalho: pode ser fechado e some quando outra cidade é escolhida. (RN-002)
- [x] **T-6c.5** Busca funcionando com o pedido de localização pendente, e a cidade escolhida prevalece. (P-009)
- [x] **T-6c.6** Testes de ponta a ponta: CA-001, CA-002, CA-003, os dois casos de localização tardia e a falha da geocodificação reversa.
- [x] **T-6c.7** Definição de pronto + commit.

**Fecha:** RF-001, RF-002, RF-003, RN-001, RN-002, RN-003, RN-009, CA-001, CA-002, CA-003, P-005, P-009

## Fatia 7 — Condições atuais

Arquitetura: seções 6.3, 7.1 e ADR-012. Testes em `tests/e2e/test_f2_current.py`.

- [x] **T-7.1** 7 ilustrações SVG próprias em `static/img/conditions/` e a camada escura sobre elas. Se a imagem falhar, fundo neutro com texto legível. (RF-017, RNF-009)
- [x] **T-7.2** `ui/current.js`, card principal na aba "Hoje": temperatura, descrição (até 2 linhas), sensação, hora local, selo de alertas (oculto sem alertas) e ícone com texto alternativo. (RF-016, RF-018, RF-019)
- [x] **T-7.3** Seis cards de indicadores, com rótulos do `messages.js`, "Calmo" e "—" para ausentes. (RF-020 a RF-023)
- [x] **T-7.4** Escala ativa: o bloco escolhe o texto `c` ou `f` e redesenha ao trocar a escala ou ao chegar dado novo, com vento em m/s ou mph. (RF-056, RF-058)
- [x] **T-7.5** Testes de ponta a ponta: CA-009 a CA-015 e CA-039 a CA-043.
- [x] **T-7.6** Definição de pronto, com conferência visual, + commit.

**Fecha:** RF-016, RF-017, RF-018, RF-019, RF-020, RF-021, RF-022, RF-023, RF-056, RF-058, RNF-009, CA-009, CA-010, CA-011, CA-012, CA-013, CA-014, CA-015, CA-039, CA-040, CA-041, CA-042, CA-043

## Fatia 8 — Previsão diária

Arquitetura: seções 6.3, 6.6 e 7.4. Testes em `tests/e2e/test_js_logic.py` e `tests/e2e/test_f3_daily.py`.

- [x] **T-8.1** `logic/time-window.js`: `cityToday` e `visibleDays` (descarta os dias passados e limita a 8 a partir de "Hoje", D-14), com testes de virada da meia-noite e de fuso diferente (Tóquio). (RN-026, RN-027)
- [x] **T-8.2** `ui/day-tabs.js`: aba "Hoje" + dias da semana, máxima e ícone com texto alternativo, padrão ARIA de tablist (setas e Enter), `aria-selected` com destaque além da cor, rolagem própria, aba selecionada trazida para a área visível e mensagem "Previsão diária indisponível.". (RF-024, RF-025, RF-032, RN-028, RN-029, RNF-014, RNF-015)
- [x] **T-8.3** `actions.selectDay` e resumo do dia no card principal e nos cards: máxima, "Mín. X°", sensação diurna, data, visibilidade prevista ou "—", ilustração do dia e selo com os alertas do dia. (RF-026 a RF-028, RF-030, RN-030, RN-031, RN-033)
- [x] **T-8.4** Troca de cidade volta para "Hoje", dados atualizados mantêm o dia se ele ainda existir, e a escala é mantida. (RF-031, RF-057)
- [x] **T-8.5** Testes de ponta a ponta: CA-016, CA-017, CA-018, CA-020 e CA-021, atualização em até 100 ms e nenhuma consulta ao trocar de aba. (RNF-013, P-011)
- [x] **T-8.6** Definição de pronto + commit.

**Fecha:** RF-024, RF-025, RF-026, RF-027, RF-028, RF-030, RF-031, RF-032, RF-057, RN-026, RN-027, RN-028, RN-029, RN-030, RN-031, RN-033, RNF-013, RNF-014, RNF-015, CA-016, CA-017, CA-018, CA-020, CA-021, P-011

## Fatia 9 — Hora a hora

Arquitetura: seções 6.3, 6.6 e ADR-007. Testes em `tests/e2e/test_js_logic.py` e `tests/e2e/test_f4_hourly.py`.

- [ ] **T-9.1** Lógica: `hourlyWindow` (descarta horas passadas), `monotonePath` (Fritsch–Carlson, sem passar da mínima nem da máxima, linha reta no centro com temperaturas iguais), `groupRainLabels` e `hourlyAltText`. (RN-034, RN-038, RN-039, RNF-016)
- [ ] **T-9.2** `ui/hourly.js`, cards: até 24 horas com hora (e dia da semana às 00:00), ícone com texto alternativo, chance de precipitação e temperatura, com rolagem horizontal. (RF-033, RF-037, RNF-010)
- [ ] **T-9.3** Curva SVG com `temp_value` da escala ativa, etiquetas de chuva, pontos focáveis com hora, temperatura e chuva, e texto alternativo. (RF-034 a RF-036, RN-040, RNF-017)
- [ ] **T-9.4** Mensagem de indisponibilidade sem afetar os demais blocos. (RF-038)
- [ ] **T-9.5** Testes de ponta a ponta: CA-022 a CA-026, CA-019 (aba "Qui" mantém a janela atual), troca de escala convertendo todas as temperaturas da tela e nenhuma consulta adicional. (RF-029, RF-055, RN-056, RNF-018)
- [ ] **T-9.6** Definição de pronto, com conferência visual, + commit.

**Fecha:** RF-029, RF-033, RF-034, RF-035, RF-036, RF-037, RF-038, RF-055, RN-034, RN-038, RN-039, RN-040, RN-056, RNF-010, RNF-016, RNF-017, RNF-018, CA-019, CA-022, CA-023, CA-024, CA-025, CA-026

## Fatia 10 — Por minuto

Arquitetura: seções 6.3, 6.6, 7.1 e ADR-007. Testes em `tests/e2e/test_js_logic.py` e `tests/e2e/test_f5_minutely.py`.

- [ ] **T-10.1** Lógica: `minuteWindow` (descarta minutos passados), `minuteMarks` (o marco de k minutos só aparece com pelo menos k barras, e o de 60 min fica no fim da última barra), `minuteSummary` (4 frases) e `barHeight` (teto de 10 mm/h e altura mínima). (RN-042, RN-043, RN-044, RN-047, P-015)
- [ ] **T-10.2** `ui/minutely.js`: barras coloridas por faixa, espaço vazio para minuto ausente, marcos com horário, legenda das 5 faixas em texto e resumo. (RF-039 a RF-043)
- [ ] **T-10.3** Gráfico como um único elemento focável: setas percorrem os minutos e anunciam "HH:MM — X,XX mm/h", e o mesmo valor aparece ao passar o cursor. (RF-044, RNF-020)
- [ ] **T-10.4** Mensagem de indisponibilidade, painel que não muda com a escala e posição sobreposta ou abaixo do mapa. (RF-045, RN-046, RN-057, RNF-021)
- [ ] **T-10.5** Testes de ponta a ponta: CA-027 a CA-031, e contraste das barras conferido contra os tokens. (RNF-019)
- [ ] **T-10.6** Definição de pronto, com conferência visual, + commit.

**Fecha:** RF-039, RF-040, RF-041, RF-042, RF-043, RF-044, RF-045, RN-042, RN-043, RN-044, RN-046, RN-047, RN-057, RNF-019, RNF-020, RNF-021, CA-027, CA-028, CA-029, CA-030, CA-031, P-015

## Fatia 11 — Mapa

Arquitetura: seções 7.2 e ADR-006. Testes em `tests/e2e/test_f6_map.py`, com as tiles simuladas por `page.route`.

- [ ] **T-11.1** `ui/map.js`: mapa base CARTO Voyager, camada de chuva por `/api/tiles/precipitation` com opacidade 0,6, zoom 6 (mínimo 3, máximo 10), marcador com `marker_label` ou "Sua localização" e `aria-label` do mapa. (RF-046, RF-047, RN-048, RN-049, RN-050, RNF-024)
- [ ] **T-11.2** Atribuições no canto inferior direito, sem sobreposição do painel por minuto. (RF-050, RNF-025, P-019)
- [ ] **T-11.3** Troca de cidade recentraliza, move o marcador e restaura o zoom. Interagir com o mapa não consulta o clima nem muda a cidade. (RF-048, RN-051)
- [ ] **T-11.4** Falhas: mapa base indisponível (contagem de `tileload`/`tileerror`) e faixa "Camada de chuva indisponível no momento.", sem afetar os demais blocos. (RF-051, RF-052, P-021)
- [ ] **T-11.5** Teclado (zoom e arraste) e dois dedos em telas de toque, com a dica de 1,5 s. (RF-049, RN-052)
- [ ] **T-11.6** Testes de ponta a ponta: CA-032 a CA-038, e só as tiles da área visível são pedidas. (RNF-023)
- [ ] **T-11.7** Definição de pronto, com conferência visual, + commit.

**Fecha:** RF-046, RF-047, RF-048, RF-049, RF-050, RF-051, RF-052, RN-048, RN-049, RN-050, RN-051, RN-052, RNF-023, RNF-024, RNF-025, CA-032, CA-033, CA-034, CA-035, CA-036, CA-037, CA-038, P-019, P-021

## Fatia 12 — Robustez, desempenho e acessibilidade

Arquitetura: seções 4, 7.4 e 8.4. Os tempos são medidos nos testes de ponta a ponta com o `/api` e as tiles simulados (decisão D-03).

- [ ] **T-12.1** Retorno à página: `visibilitychange` → `refreshIfStale`, status `refreshing` com os dados antigos visíveis e "Atualizando…". (RF-014)
- [ ] **T-12.2** Revisão de concorrência e de tempo em todos os blocos: cidade A e depois B, vários cliques em "Tentar novamente", troca de escala durante o carregamento e virada da meia-noite com dados em cache.
- [ ] **T-12.3** Desempenho: blocos em até 3 s, cache em até 200 ms sem indicador, mapa em até 3 s sem atrasar os demais blocos, nova escala em até 100 ms e todos os blocos sempre na mesma escala. (RNF-001, RNF-002, RNF-022, RNF-026, RNF-029)
- [ ] **T-12.4** Privacidade: nada em `localStorage`, `sessionStorage`, IndexedDB ou cookies, e as requisições da página só vão para `/api`, o CARTO e os ícones do OpenWeatherMap. (RNF-005, P-007, P-008)
- [ ] **T-12.5** Acessibilidade e consistência: percorrer a página inteira só pelo teclado, nenhuma informação só pela cor, unidade identificável em cada valor, todos os textos em pt-BR e o mesmo formato para o mesmo tipo de valor em todos os blocos. (RNF-012, P-016, P-017, P-018, P-023)
- [ ] **T-12.6** Revisão em 360 px de todos os blocos, com valores de 3 dígitos e sinal negativo em °F e nomes de cidade longos. (P-024)
- [ ] **T-12.7** Definição de pronto + commit.

**Fecha:** RF-014, RNF-001, RNF-002, RNF-005, RNF-012, RNF-022, RNF-026, RNF-029, P-007, P-008, P-016, P-017, P-018, P-023, P-024

## Fatia 13 — Fechamento

Arquitetura: seções 9 e 11.

- [ ] **T-13.1** `tests/unit/test_traceability.py`: todo RF, RN, RNF e CA do spec aparece no nome ou na docstring de pelo menos um teste. (P-027)
- [ ] **T-13.2** Rodar a suíte completa (`pytest -m "not e2e"`, `pytest -m e2e`, ruff) e conferir que todos os CA passam de ponta a ponta.
- [ ] **T-13.3** `tests/api/test_live.py` com o marcador `live`: uma chamada real a cada rota, executada manualmente uma vez (usa a cota).
- [ ] **T-13.4** Compatibilidade: registrar no README o resultado da suíte no Chrome. Nenhum outro navegador é testado (limitação L-01). (RNF-006)
- [ ] **T-13.5** Revisão final: sem cadastro nem login, artefatos de requisitos sem detalhes de stack e commits citando os IDs. (P-025, P-026)
- [ ] **T-13.6** Atualizar o README: status, funcionalidades, estrutura do projeto, exemplos de uso, limitações e tabela de releases.
- [ ] **T-13.7** Release `v0.1.0`: tag e registro no README, com a confirmação antes de enviar a tag ao GitHub.
- [ ] **T-13.8** Definição de pronto + commit.

**Fecha:** RNF-006, P-025, P-026, P-027

---

## Decisões e limitações

| ID | Data | Decisão |
|---|---|---|
| D-01 | 2026-10-04 | A fatia 6 da arquitetura foi dividida em 6a (estado, cache e chamadas ao backend), 6b (cabeçalho, busca e seletor de escala) e 6c (localização inicial e cidade padrão), para caber em sessões curtas. A fatia 12 passou a se chamar "Robustez, desempenho e acessibilidade" |
| D-02 | 2026-10-04 | Cada um dos 217 IDs fecha em uma única fatia (linhas **Fecha**). A distribuição foi conferida por script em 2026-10-04: nenhum ID faltando e nenhum repetido |
| D-03 | 2026-10-04 | Os requisitos de tempo (RNF-001, RNF-002, RNF-013, RNF-022 e RNF-026) são medidos nos testes de ponta a ponta com o `/api` e as tiles simulados. O tempo da rede e do provedor real não é medido |
| D-04 | 2026-10-05 | O log próprio registra o modelo da rota (ex.: `/api/tiles/precipitation/{z}/{x}/{y}.png`) em vez do caminho real, porque os `z/x/y` das tiles revelam a área vista no mapa (P-006). Sem rota encontrada, registra o caminho sem a query string. Seção 7.6 da arquitetura atualizada |
| D-05 | 2026-10-05 | `pythonpath = ["."]` na configuração do pytest, para o comando `pytest` (sem `python -m`) importar o pacote `app`. Seção 11 da arquitetura atualizada |
| D-06 | 2026-10-05 | Um commit por fatia, no fim dela. O `tasks.md` é atualizado a cada tarefa concluída, para que uma nova sessão saiba onde continuar mesmo com o trabalho ainda sem commit |
| D-07 | 2026-10-05 | O Starlette 1.7 emite `StarletteDeprecationWarning` ao usar o `TestClient` com o `httpx` e sugere o `httpx2`. O aviso fica visível e não é filtrado; adotar o `httpx2` exigiria um ADR (guardrail 1). Revisto na fatia 4: os testes de API usam o `TestClient` sem problema, e o aviso continua só como aviso |
| D-08 | 2026-10-05 | `.gitattributes` com `static/vendor/** -text`: os arquivos de terceiros ficam byte a byte como foram baixados, sem a conversão de fim de linha do `core.autocrlf`, para que o SHA-256 de `static/vendor/README.md` continue conferindo. O `LICENSE` do Leaflet (BSD-2-Clause) também foi copiado |
| D-09 | 2026-10-05 | **Troca da One Call API 3.0 pela 4.0** (ADR-013). A 3.0 foi descontinuada e não aceita novas assinaturas, e uma chave só com a 4.0 recebe 401 nela. Ela tinha sido mantida como "risco aceito" sem verificar se ainda era possível assiná-la. Mudanças: spec (serviços externos, glossário, RF-004, RF-027, RF-030, RF-039, RN-018, RN-027, RN-031, RN-032, RN-043, RN-047, RNF-003, CA-017, CA-021, casos de borda, dependências e premissas das features 1 a 5), arquitetura (seções 1, 2, 4, 5, 6, 7.6, 8.4, 9.2, 10 e 13, ADR-007 e o novo ADR-013), README, CLAUDE.md, `requisitos.md`, `.env.example` e as tarefas T-0.8, T-2.3, T-3.1, T-3.2, T-3.4, T-4.1, T-4.4, T-8.3 e T-10.1. As tarefas T-0.1 a T-0.7 não mudaram. Cada consulta de clima passa a custar 5 chamadas na cota |
| D-10 | 2026-10-05 | **Ajustes depois das capturas reais da 4.0** (T-0.10). (1) A previsão diária não traz alertas: o selo de cada dia volta à regra original da vigência (RF-030, RN-032, CA-021 e o caso das 00:00 voltam ao texto anterior à D-09), com o detalhe de cada alerta buscado numa segunda rodada (+1 chamada por alerta, opção escolhida entre três). (2) O `dt` de cada dia é 00:00 UTC da data do dia: a data do dia é a data UTC do `dt`, sem somar o fuso. (3) A previsão por minuto começa no minuto seguinte ao da consulta: RF-039, RN-043 e o "Dado" do CA-029 contam a partir do primeiro minuto da janela. (4) RN-018 volta a contar todos os alertas da resposta, inclusive os futuros. Achados detalhados em `tests/fixtures/README.md` |
| D-11 | 2026-10-05 | **Arredondamento na exibição.** O spec pede o "inteiro mais próximo" (RN-014) sem dizer o que fazer no empate, e as capturas reais já trazem um (sensação de 20,5 °C em Tóquio). O `format_number` arredonda o empate para longe do zero (20,5 → "21"; -20,5 → "-21") e parte do texto decimal do valor, não do float binário (2,675 com 2 casas → "2,68"). O `round()` do Python foi descartado porque arredonda o empate para o par (20,5 → "20"). Seção 6.6 da arquitetura atualizada |
| D-12 | 2026-10-05 | O tipo `Scale` (`Literal["c", "f"]`), usado pelo `format_temp`, foi criado em `app/schemas/view.py` já na fatia 1, que é onde a seção 6.6 o coloca. O restante do view model continua na fatia 3 |
| D-13 | 2026-10-05 | As regras da fatia 2 usam tipos que a seção 6.6 coloca em `app/schemas/`. Eles foram criados já na fatia 2, na forma mínima: `Alert` e `GeoResult` em `provider.py` (campos opcionais, `extra="ignore"`) e `Scaled`, `CityOption`, `ConditionGroup` e `Band` em `view.py`. As T-3.2 e T-3.3 completam os modelos, inclusive o valor fora do formato virar `None`. O `city_option` exige coordenadas: a T-3.5 descarta os itens da busca que vierem sem `lat` ou `lon` |
| D-14 | 2026-10-05 | O `daily` do view model traz todos os dias recebidos (até 10), e o limite de 8 a partir de "Hoje" fica só no `visibleDays` do frontend (T-8.1). O corte em 8 a partir do primeiro dia recebido, previsto antes na seção 6.3, deixaria 7 abas em Tóquio nas primeiras horas do dia local: o primeiro dia da 4.0 é a data UTC, que lá já é "ontem" (captura da T-0.8), e o RN-027 pede 8. Seções 6.3 e 6.6 da arquitetura atualizadas |
| D-15 | 2026-10-05 | Regras do view model que o spec não define, registradas na seção 6.3 da arquitetura: (1) um rótulo com prefixo e valor ausente mantém o prefixo (`"Sensação de —"`, `"Mín. —"`), como o tooltip `"08:18 — —"`; (2) sem `timezone_offset`, os blocos diário, hora a hora e por minuto ficam `null` e a hora do card principal mostra "—", porque não há fuso para achar a hora local nem o "Hoje"; (3) registro de previsão sem `dt` é descartado. A variante `onecall_alerts.json` ficou com 2 alertas (sem o alerta sem vigência, que contaria em todos os dias e impediria o selo oculto do CA-021) |
| D-16 | 2026-10-06 | **Layout entre 600 px e a largura do print.** Com os indicadores em 3 colunas a partir de 600 px (RNF-011), 1/3 da largura em 600 px daria cards de cerca de 55 px. Por isso, o card principal e a hora a hora usam `flex-wrap` com larguras-base de 300 px e 520 px: ficam lado a lado (cerca de 1/3 e 2/3) quando cabem e empilham quando não, sem um segundo breakpoint. Pelo mesmo motivo, a busca desce para a segunda linha do cabeçalho quando falta espaço. O painel por minuto fica 24 px acima da borda do mapa, para não cobrir a atribuição (RNF-025). Seção 7.1 da arquitetura atualizada |
| D-17 | 2026-10-06 | **Textos e dependências da fatia 6a.** (1) O indicador de carregamento é um ícone animado com o nome "Carregando…" para leitores de tela. O spec não dá texto ao indicador (só o "Ainda carregando…" depois de 3 s), e o nome fica no `messages.js` como os demais textos. (2) O `MESSAGES` já traz todos os textos fixos do spec, também os das fatias 6b a 11, para que exista uma única cópia deles. (3) O `DEFAULT_CITY` fica no `actions.js`, onde o `start()` da 6c o usa, com os rótulos "Uberlândia, BR" e "Uberlândia" vindos do `messages.js`. Por isso o `actions.js` passa a poder importar o `messages.js` (seção 5.2 da arquitetura atualizada), que também vai fornecer "Sua localização" na 6c |
| D-18 | 2026-10-06 | **Resposta de uma cidade anterior.** Ela é descartada da tela (P-012), mas, se for de sucesso, vai para o cache. Assim, voltar a essa cidade em menos de 10 min não gera outra consulta (P-010, RNF-003). O diagrama da seção 2.2 dava a entender que a gravação no cache vinha depois do descarte, e foi ajustado |
| D-19 | 2026-10-06 | **Cabeçalho e busca (fatia 6b).** (1) Contratos: o estado da busca ganhou o status `invalid` (termo vazio ou com 1 caractere, sem consulta), separado de `error` (falha da busca), e o `actions.js` passou a exportar `SEARCH_MAX_LENGTH` e `chooseSearchResult(result)`, que fecha a lista e seleciona a cidade, para a conversão do item em `City` ficar fora da `ui/`. Seções 6.5 e 6.6 da arquitetura atualizadas. (2) Textos fora do spec, no `messages.js` como na D-17: o título "Previsão do tempo" (do print) e os nomes para leitores de tela da lupa ("Buscar"), da lista ("Cidades encontradas") e do seletor ("Escala de temperatura"). (3) O nome longo da cidade aparece completo, em mais linhas, ao passar o cursor ou focar (a cidade é focável). O `title` foi descartado porque não aparece com o foco. (4) Comportamentos que o spec não detalha: o Esc fecha a lista sem apagar o termo; sair da busca pelo Tab também fecha a lista, como clicar fora; editar o termo apaga a mensagem anterior; e confirmar de novo o termo com a lista dele aberta não repete a busca, como com a busca em andamento (RF-015). (5) A mensagem da busca (termo inválido, nenhum resultado ou falha) abre abaixo do campo, no lugar da lista, com `role="status"` |
| D-20 | 2026-10-06 | **Localização inicial (fatia 6c).** (1) Contrato: o `actions.js` passou a exportar `dismissLocationNotice()`, que fecha o aviso de localização, e o `selectCity` fecha o aviso quando a cidade escolhida não é a padrão (RN-002). Seção 6.6 da arquitetura atualizada. (2) O aviso passou para dentro do `<header>`, como última linha, abaixo da busca, porque é o `header.js` que o desenha (seção 5.1). Ele ganhou um botão de fechar com o nome "Fechar aviso" para leitores de tela, que não está no spec e fica no `messages.js`, como na D-17. (3) Enquanto o pedido de localização está pendente (até 10 s), o cabeçalho fica sem cidade e os blocos mostram o indicador de carregamento, sem consulta de clima. (4) A localização que chega no prazo depois de o usuário escolher uma cidade pela busca também é descartada ("a cidade escolhida prevalece", feature 1, categoria 2), assim como a que chega enquanto o nome é buscado na geocodificação reversa e outra cidade é escolhida. (5) Testes: sem permissão concedida, o Chrome do Playwright nega a localização na hora, por isso os testes das fatias anteriores continuam abrindo com a cidade padrão. O usuário que não responde e a localização tardia usam um `navigator.geolocation` falso (`tests/e2e/location.py`). Dois testes da busca passaram a esperar a lista abrir antes das setas, porque falhavam de vez em quando com o passo assíncrono a mais na abertura da página |
| D-21 | 2026-10-06 | **Condições atuais (fatia 7).** (1) A ilustração do grupo de condição é o fundo do card principal, escolhida no CSS pelo `data-condition` do card, sob a camada escura. Se ela não carregar, sobra a cor neutra do novo token `--color-illustration-fallback` (`#475569`), com a mesma camada (feature 2, categoria 9; seção 7.1 da arquitetura atualizada). Ela é decorativa: a condição chega aos leitores de tela pela descrição e pelo texto alternativo do ícone (RNF-010). (2) As 7 ilustrações usam só tons médios e escuros, para o texto branco manter 4,5:1 sob a camada (RNF-009). O teste mede o contraste nos pixels do card renderizado, sem o texto: entre 4,87:1 (nublado) e 7,53:1 (neutra); sem a camada, a neve daria 1,96:1. (3) O card mostra o ícone do provedor acima da descrição, que o print não tem, porque a T-7.2 e o RNF-010 pedem o ícone com texto alternativo. O `dom.js` passou a exportar `setConditionIcon(img, icon, description)`, que as abas e a hora a hora também vão usar (seção 6.6 da arquitetura atualizada). (4) Textos e estrutura: o nome do bloco para leitores de tela é "Condições atuais", o título da feature 2 no spec, e fica no `messages.js` como na D-17. Os indicadores ganharam ícones decorativos, como no print. O bloco passou a ser montado pelo `ui/current.js`, que também desenha o estado dele, e saiu da lista provisória do `main.js`. (5) Testes: os cenários dos critérios de aceite partem do pacote real de Uberlândia com campos de `current` trocados e passam pelo view model do backend (`bundle` e `view_of` em `tests/e2e/weather_api.py`), cuja simulação passou a aceitar um `WeatherView` próprio do teste |
| D-22 | 2026-10-06 | **Previsão diária (fatia 8).** (1) Contrato: o `logic/time-window.js` exporta também `activeDay(days, selectedDay, nowSec, offset)`. O dia ativo é derivado a cada desenho, nas abas e no card: o `selectedDay` guardado só vale enquanto estiver entre os dias visíveis e não for hoje. Assim, dados atualizados mantêm o dia, e um dia que virou passado (dados em cache atravessando a meia-noite) leva a tela de volta para "Hoje" sem mudar o estado, porque um dia passado nunca volta a ser visível. Seções 6.6 e 7.4 da arquitetura atualizadas. A troca de cidade já zerava o `selectedDay` no `selectCity` (RF-031). (2) As abas seguem o padrão de abas da ARIA com ativação manual: as setas movem o foco, dando a volta nas pontas, e o Enter, o Espaço ou o clique selecionam (RNF-014). Home e End, que o spec não cita, vão para a primeira e a última aba, como no padrão. Só a aba selecionada entra na ordem do Tab, e uma aba com o foco continua com ele quando as abas são recriadas. (3) No card, a mínima ("Mín. X°") fica abaixo da máxima, e a data ocupa o lugar da hora (RN-030). (4) O nome da faixa para leitores de tela, "Dias da previsão", saiu do `index.html` da fatia 5 e foi para o `messages.js`, como na D-17. Se nenhum dia da previsão for de hoje em diante, a faixa mostra "Previsão diária indisponível.". (5) Testes: o relógio de toda página de ponta a ponta começa no momento das capturas (`CAPTURE_NOW`) e anda normalmente, e o `open_paused` pausa 1 minuto depois dele. Sem isso, "Hoje" e as abas dependeriam da data em que os testes rodam, e as abas sumiriam dias depois da captura. O tempo da suíte não mudou (conferido com e sem o relógio) |
| L-01 | 2026-10-04 | **Limitação:** os testes são feitos só no Google Chrome instalado. Edge, Firefox e Safari não são testados, nem em computador nem em celular. O RNF-006 continua no spec como meta, mas a compatibilidade com outros navegadores não é verificada no MVP |
