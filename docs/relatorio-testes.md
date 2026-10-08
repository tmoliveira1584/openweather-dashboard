# Relatório de testes — OpenWeather Dashboard (MVP)

Resultados da etapa de Testes, fase por fase. O [plano-testes.md](plano-testes.md) diz **o que** cada fase faz. Este relatório mostra **o que cada fase entregou**, para acompanhar a etapa de forma didática.

- **Rotina:** ao fim de cada fase, antes do commit dela, uma seção nova entra aqui, sempre com a mesma estrutura: a ideia da fase, o resultado em números, o que foi feito, o que se aprendeu, as verificações e o parecer.
- **Fase 6:** consolida as seções num resumo da etapa inteira, com a comparação entre a linha de base e o fim.

## Linha de base (v0.1.0, 2026-10-06)

| Nível | Testes |
|---|---|
| Unidade (Python) | 303 |
| API | 200 (+4 de fumaça `live`) |
| Lógica JavaScript | 100 |
| Ponta a ponta (Chrome) | 236 |
| **Total da suíte comum** | **839** |

Detalhes no [plano-testes.md](plano-testes.md), seção 3.

## Painel da etapa

| Fase | Situação | Testes na suíte | Parecer |
|---|---|---|---|
| 1 — Cobertura de código | Concluída em 2026-10-07 | 846 (+7) | ✅ Sucesso |
| 2 — Revisão dos testes pela IA | Concluída em 2026-10-07 | 847 (+1) | ✅ Sucesso |
| 3 — Testes exploratórios automatizados | Não iniciada | — | — |
| 4 — Teste de mutação | Não iniciada | — | — |
| 5 — Registro de defeitos (contínua) | 0 defeitos | — | — |
| 6 — Relatório final | Não iniciada | — | — |

---

## Fase 1 — Cobertura de código (2026-10-07)

**A ideia:** cobertura é o quanto do código os testes executam. Uma linha que nenhum teste executa pode quebrar sem que ninguém perceba.

### Resultado

| Medida | Antes (839 testes) | Depois (846 testes) | Meta |
|---|---|---|---|
| Python, linhas | 99,7% (621 de 623) | **100%** (621 de 621) | 90% |
| Python, ramos (`if`) incompletos | 5 | **0** | — |
| JavaScript, linhas | 99,9% (1.597 de 1.598) | **100%** (1.598 de 1.598) | 85% |
| JavaScript, linhas parciais | 10 | **7** (todas justificadas) | — |

- **Linha parcial:** linha que rodou, mas com algum trecho que nunca rodou (o outro lado de um `?:`, de um `??` ou de um `if` de uma linha só). É o equivalente aos ramos do Python.
- **Por arquivo, antes da fase:** só dois arquivos não estavam em 100% de linhas: `app/clients/openweather.py` (96%) e `static/js/ui/hourly.js` (99,6%). Os outros 14 do Python e 16 do JavaScript já estavam completos.

### O que foi feito

1. **Medir o Python (TS-1.1):** `coverage==7.16.2`, só para desenvolvimento ([ADR-014](arquitetura.md#adr-014--cobertura-do-python-com-coveragepy)). Mede também o backend que os testes de ponta a ponta sobem numa thread.
2. **Medir o JavaScript (TS-1.2):** o plugin `tests/js_coverage.py`, sem dependência nova. Com `--js-coverage`, ele pede ao V8 do Chrome, pelo protocolo de depuração (CDP), os trechos executados e monta a tabela por arquivo e a lista de linhas parciais.
3. **Classificar as lacunas (TS-1.3):** cada trecho sem execução virou falta de teste, código morto ou tratamento defensivo (tabela abaixo).
4. **Fechar as lacunas (TS-1.4):** 7 testes novos e 1 ramo morto removido.

**Comando:** `coverage run -m pytest --js-coverage`, depois `coverage report`. A tabela do JavaScript sai no fim da execução e em `coverage-js/report.txt`.

### Lacunas e decisões

| Onde | O que não rodava | Classificação | Decisão |
|---|---|---|---|
| `openweather.py`, `_join_pages` | Registro por hora sem `dt` | Defensivo (dado do provedor) | Teste novo: `test_adr_013_hourly_records_without_dt_are_kept_without_dedup` |
| `openweather.py`, `_alert_validity` | Detalhe de alerta que não é objeto | **Código morto**: `_alert` sempre devolve um objeto, porque `_json` exige `dict` | Ramo removido |
| `openweather.py`, `merge_onecall` | Dados atuais sem `timezone_offset` | Defensivo (dado do provedor) | Teste novo: `test_adr_013_current_without_timezone_offset_leaves_it_out_of_bundle` |
| `openweather.py`, `_alert_ids` | ID de alerta vazio ou que não é texto | Defensivo (dado do provedor) | Teste novo: `test_adr_013_blank_or_non_text_alert_ids_are_ignored` |
| `openweather.py`, `_raise_first_error` | Erro inesperado (não `ProviderError`) numa rodada | Falta de teste | Teste novo: `test_rn_012_unexpected_error_is_not_hidden_as_provider_error` |
| `hourly.js:243` | Cursor sai da curva com um ponto focado: a dica volta ao ponto focado | Falta de teste | Teste novo: `test_rf_036_leaving_the_curve_returns_the_tip_to_the_focused_point` |
| `hourly.js:313` (parcial) | `pointermove` sem mudança de posição, gerado pela rolagem pelo teclado | Falta de teste | Teste novo: `test_rf_036_pointer_event_without_movement_keeps_the_focused_point` |
| `actions.js:270` (parcial) | Resposta atrasada de uma busca já substituída por outra | Falta de teste | Teste novo: `test_rf_015_late_answer_of_a_replaced_search_is_discarded` |
| `actions.js:196` (parcial) | `term ?? ''` com termo nulo | Defensivo: a interface sempre passa o texto do campo | Justificada |
| `day-tabs.js:128`, `hourly.js:325` (parciais) | Tecla sem um ponto ou uma aba como alvo | Defensivo: só pontos e abas recebem o foco | Justificadas |
| `hourly.js:308` (parcial) | Alvo sem `closest` ou fora de um ponto | Defensivo: os filhos do contêiner são todos pontos | Justificada |
| `hourly.js:55`, `minutely.js:63` (parciais) | Estado sem `weather` ou sem `timezone_offset` ao desenhar | Defensivo: sem fuso, o view model já manda o bloco como `null` | Justificadas |
| `minutely.js:206` e `216` (parciais) | Cursor ou tecla no gráfico sem minutos | Defensivo: o gráfico fica oculto quando o bloco não tem dados | Justificadas |

### O que se aprendeu

- **Um teste antigo passava sem testar o que dizia.** O `test_rf_036_keyboard_wins_over_the_resting_cursor` nunca exercitava a guarda que deveria proteger, porque o Chrome sem janela não gera o evento esperado. Só a medida de linhas parciais revelou isso. O teste novo dispara o evento diretamente.
- **Um teste novo só vale se falhar quando o código quebra.** Cada um dos 7 testes novos foi rodado com a guarda que ele protege removida do código. Os 7 falharam, e o código foi restaurado. É uma prévia, feita à mão, do teste de mutação da fase 4.
- **100% de cobertura não prova que os testes são bons.** A cobertura diz que o código rodou, não que as asserções conferem o resultado certo. As fases 2 (revisão) e 4 (mutação) respondem a isso.
- **O papel da IA:** escolheu a ferramenta e registrou o ADR, escreveu o plugin de cobertura do Chrome, leu cada lacuna no código, classificou, escreveu os testes e provou que eles detectam a quebra.

### Verificações

- Suíte comum verde: 846 testes passando (839 + 7), com ruff sem apontamentos.
- A chave da API não aparece em nenhum arquivo do repositório.
- Os arquivos gerados pela medição (`.coverage`, `coverage-js/`) ficam fora do Git (`.gitignore`).
- Nenhum defeito do produto encontrado: a fase 5 continua com 0 registros.

### Parecer

✅ **Sucesso.** As metas de cobertura já eram atendidas com folga pela suíte da v0.1.0. A fase fechou as últimas lacunas, removeu um ramo morto e encontrou um teste que só cobria a guarda no nome. Como cobertura não mede a qualidade das asserções, as fases 2 e 4 continuam necessárias.

---

## Fase 2 — Revisão dos testes pela IA (2026-10-07)

**A ideia:** um teste pode rodar o código e mesmo assim não conferir nada de útil. Nesta fase, a IA lê cada teste ao lado do código que ele testa e se pergunta: "se o código estivesse errado, este teste falharia?".

### Resultado

| Medida | Antes | Depois |
|---|---|---|
| Achados confirmados em aberto | 31 | **0** |
| Mutantes manuais detectados (19 defeitos plantados) | 1 de 19 | **19 de 19** |
| Testes na suíte comum | 846 | **847** (+4 novos, −3 duplicados) |
| `expect(...)` sem verificação | 2 | **0** |

- **Mutante manual:** um defeito pequeno plantado de propósito no código do produto, como trocar `>` por `>=`. O teste ligado ao achado roda com o defeito, e o arquivo é restaurado logo depois. Se o teste passa, o defeito "sobreviveu" e o teste é fraco.
- **Antes e depois:** os mesmos 19 mutantes rodaram contra os testes antigos (versão do último commit) e contra os corrigidos. Só 1 era pego antes: o de `time.py`, por outro teste do mesmo arquivo.

### O que foi feito

1. **Revisar (TS-2.1):** o `/code-review` só revisa um diff. Rodado sobre o último commit de `tests/`, não achou defeitos. Para revisar a suíte inteira, 5 agentes de IA trabalharam em paralelo, um por nível: unidade, API, lógica JS e ponta a ponta (em duas partes). Cada um só lia, sem alterar arquivos, e tinha de apontar o código errado que o teste deixaria passar (DT-05).
2. **Conferir (TS-2.2):** cada um dos 31 achados foi conferido no código do produto e procedeu. Os revisores também listaram cerca de 40 suspeitas que eles próprios descartaram, com o motivo. Exemplo: esperas fixas que provam que algo **não** acontece são legítimas.
3. **Corrigir (TS-2.3):** 31 correções em 17 arquivos de teste, sem tocar no código do produto. Depois, os 19 mutantes provaram as correções.

### Achados por tipo

| Tipo | Quantos | Exemplo |
|---|---|---|
| Asserção fraca | 14 | `-0,004` com 2 casas era conferido só como "não começa com -". Um código que devolvesse "0" em vez de "0,00" passava |
| Passaria com o código errado | 5 | Dois `expect(...)` sem verificação (`.to_have_count(1)` faltando): o texto alternativo da curva em °F nunca era conferido |
| Espera fixa ou leitura cedo demais | 5 | Esperas de 200 ms e 400 ms trocadas por esperas pela condição (o pedido chegar, o mapa parar) |
| Nome ou descrição enganosa | 4 | `test_rn_051_scale_and_weather_…` nunca atualizava os dados; virou `test_rn_051_scale_change_…` |
| Duplicação | 2 | Testes que forçavam dados novos com `setState`, já cobertos pelo caminho real (relógio, volta à página) |
| Dependência de ordem | 1 | O teste do log do httpx só falhava se rodasse antes dos testes de unidade. Agora ele zera os níveis antes de começar |

### Os achados mais importantes

| Onde | O que o teste deixava passar | Correção |
|---|---|---|
| `test_routes.py` | Uma rota que trocasse `lon` por `lat` ou `x` por `y` (o simulador só olha o `lat`) | Confere as coordenadas e o z/x/y repassados ao provedor |
| `test_f1_location.py` | O prazo de 10 s vencendo depois de uma busca e trazendo a cidade padrão de volta: o cenário estava no nome, mas nunca rodava | Teste novo: `test_p_009_deadline_after_a_search_does_not_bring_the_default_city` |
| `test_f1_loading.py` | Uma trava de 5 s em vez de 17 s | Confere que nada acontece em 16,999 s e que o erro aparece aos 17 s |
| `test_f6_map.py` | Uma dica de toque visível por 1 s ou 3 s, em vez de 1,5 s | Mede, na página, quanto tempo a dica fica visível |
| `test_f2_current.py` | O contraste medido antes de a ilustração aparecer, ou seja, sobre a cor de reserva | Espera a ilustração carregar antes da medida |
| `test_js_logic.py` | Empate na máxima indo para a hora mais tarde; "estável" decidido pelo valor bruto, e não pelo exibido | Casos novos com empate na máxima e com 21,6° e 22,4° (os dois exibidos como "22°") |
| `test_units.py` | Um teste citava o CA-042, mas chamava a mesma função 10 vezes com a mesma entrada | Removido. O CA-042 continua coberto pelo teste de ponta a ponta |

### O que se aprendeu

- **A IA acha o que a cobertura não acha.** A fase 1 mostrou 100% de linhas, e mesmo assim 18 dos 19 defeitos plantados passavam pelos testes-alvo. Cobertura diz que o código rodou. A revisão diz se alguém conferiu o resultado.
- **Achado sem prova não vale.** A IA também erra: num caso, ela esperava "0 mm/h", mas o spec manda "0,00 mm/h" (RN-045), e quem estava errado era o teste novo. O mutante de cada correção é o que transforma uma suspeita em fato.
- **Citar um requisito não é verificar.** O teste de rastreabilidade (P-027) conta quantos IDs aparecem nos testes. O CA-042 estava "coberto" por um teste incapaz de falhar. A fase 4 (mutação) mede isso de forma sistemática.
- **Dividir para revisar:** 5 revisores com escopo pequeno e regra clara ("mostre o código errado que passaria") deram achados concretos e poucos falsos positivos.
- **O papel da IA:** revisou as 9.600 linhas de testes em paralelo, conferiu cada achado no código, escreveu as correções e plantou os defeitos que provam cada uma.

### Verificações

- Suíte comum verde: 847 testes passando, com ruff sem apontamentos.
- O código do produto (`app/`, `static/`) não mudou: os mutantes foram aplicados e restaurados um a um, e o `git status` confirmou.
- A rastreabilidade (P-027) continua completa: os 217 IDs têm pelo menos um teste.
- Nenhum defeito do produto encontrado: a fase 5 continua com 0 registros.

### Parecer

✅ **Sucesso.** A revisão encontrou 31 pontos fracos reais numa suíte que já tinha 100% de cobertura, e todos foram corrigidos. Dois testes não conferiam nada, e um cenário inteiro do nome de um teste nunca rodava. Os 19 mutantes mostram o ganho: os testes-alvo pegavam 1 defeito plantado e agora pegam os 19. A fase 4 vai repetir essa prova de forma sistemática, com um script e sobre todo o domínio.
