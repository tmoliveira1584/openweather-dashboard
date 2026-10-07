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
| 2 — Revisão dos testes pela IA | Não iniciada | — | — |
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
