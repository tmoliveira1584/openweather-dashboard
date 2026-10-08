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
| 3 — Testes exploratórios automatizados | Concluída em 2026-10-08 (escopo reduzido) | 852 (+5) | ✅ Sucesso |
| 4 — Teste de mutação | Concluída em 2026-10-08 (escopo reduzido) | 852 (+0) | ✅ Sucesso |
| 5 — Registro de defeitos (contínua) | 2 defeitos: DEF-01 corrigido, DEF-02 do provedor | — | — |
| 6 — Relatório final | Concluída em 2026-10-08 | 852 | ✅ Sucesso |

---

## Fase 1 — Cobertura de código (2026-10-07)

**A ideia:** cobertura é o quanto do código os testes executam. Uma linha que nenhum teste executa pode quebrar sem que ninguém perceba.

### Resultado

| Medida | Antes (839 testes) | Depois (846 testes) | Meta |
|---|---|---|---|
| Python, linhas | 99,7% (621 de 623) | **100%** (621 de 621) | 90% |
| Python, ramos (`if`) incompletos | 5 | **0** | — |
| JavaScript, linhas | 99,9% (1.597 de 1.598) | **100%** (1.598 de 1.598) | 85% |
| JavaScript, linhas parciais | 10 | **8** (todas justificadas)¹ | — |

- ¹ **Correção feita na fase 6:** esta seção dizia 7. A medição final e a tabela de lacunas abaixo mostram 8 linhas parciais, as mesmas antes e depois da etapa.
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

---

## Fase 3 — Testes exploratórios automatizados (2026-10-08)

**A ideia:** os testes anteriores conferem o que o spec descreve. O teste exploratório pergunta "e se…?" e procura falhas **fora** do que alguém pensou em especificar.

**Escopo reduzido (DT-06):** o plano previa 5 categorias de cenários. Pelo custo de tokens e de tempo num MVP acadêmico, em que o objetivo é aprender a técnica e não esgotá-la, a fase ficou com uma só: **fusos exóticos**.

### Resultado

| Medida | Valor |
|---|---|
| Cenários explorados | 3 fusos: +14:00 (Kiribati), +05:45 (Nepal) e −12:00 |
| Cenários automatizados | 2 (+14:00 e +05:45) |
| Defeitos encontrados | **1 (DEF-01), corrigido** |
| Testes na suíte comum | 847 → **852** (+2 de ponta a ponta, +3 casos de unidade) |

### O que foi feito

1. **Explorar (TS-3.1):** um script montou o view model da captura de Uberlândia com o fuso trocado e listou a hora atual, as horas da previsão, os dias e os minutos. Com +14:00 e −12:00, tudo saiu certo. Com +05:45 (Nepal), a hora atual era 01:26, mas a primeira hora da previsão aparecia como "00:00".
2. **Automatizar (TS-3.2):** o teste `test_exotic_timezones.py` abre a página com cada fuso e confere todos os blocos: a hora atual, "Hoje" (já terça, enquanto em UTC ainda é segunda), as horas da previsão e o marco "Agora".
   - **+14:00:** passou de primeira.
   - **+05:45:** falhou, com "00:00 Ter" no lugar de "00:45 Ter".
3. **Registrar e corrigir (TS-3.3):** o DEF-01 entrou na seção "Defeitos" do plano (fase 5).

### O defeito DEF-01

| | |
|---|---|
| **O que acontecia** | No Nepal (+05:45) e na Índia (+05:30), a previsão das 00:45 aparecia como "00:00": o horário mostrado não era o horário local da previsão |
| **Por quê** | O provedor entrega as horas em horas cheias de UTC, que nesses fusos caem em :45 ou :30 locais. O `hour_label` montava "HH:00" e descartava os minutos. O spec (RN-035) só tinha previsto fusos de hora cheia |
| **Regra violada** | P-015: "SEMPRE exibir datas e horas no fuso horário local da cidade". A constituição prevalece sobre o spec |
| **Correção** | O `hour_label` mostra o início da hora no fuso da cidade (`HH:MM`). Nos fusos de hora cheia, o resultado continua "16:00". RN-035 e arquitetura atualizadas |
| **Prova** | Os testes novos (de ponta a ponta, +05:45; de unidade, +05:45, +05:30 e −03:30) falhavam antes da correção e passam depois |

### O que ficou de fora e por quê

| Categoria do plano | Por que ficou de fora |
|---|---|
| Entradas incomuns (acentos, homônimas, termos enormes) | A suíte já cobre acentos ("Uberlândia", "Tóquio"), homônimas (5 "Santa Maria") e termos inválidos |
| Dados extremos ou malformados do provedor | A fase 1 já cobriu os tratamentos defensivos do cliente (registro sem `dt`, alerta sem ID, fuso ausente) |
| Falhas de rede no meio da consulta | Já há testes de queda de rede, de tempo esgotado e de falha numa das 5 chamadas da One Call |
| Sequências rápidas de ações | Já há testes de respostas fora de ordem, de busca substituída e de troca de escala durante a atualização |

### O que se aprendeu

- **O spec também tem pontos cegos.** Todos os testes seguiam o RN-035 ("HH:00"), e por isso todos passavam. Só uma pergunta de fora do spec ("e num fuso de 45 minutos?") revelou o defeito. Ele afeta, por exemplo, a Índia, com mais de 1 bilhão de pessoas.
- **Um único cenário bem escolhido rende.** Uma categoria e dois fusos foram suficientes para achar um defeito real do produto, num código com 100% de cobertura e testes revisados na fase 2.
- **A hierarquia de documentos decide.** O spec dizia "HH:00", mas a constituição (P-015) manda mostrar a hora local, e ela prevalece. Por isso a correção foi no produto e no spec, e não só no teste.
- **O papel da IA:** escolheu os fusos que estressam a regra (extremo, fracionário e negativo), explorou por script antes de escrever o teste, identificou a causa no código e propôs a correção mínima, compatível com os fusos de hora cheia.

### Verificações

- Suíte comum verde: 852 testes passando, com ruff sem apontamentos.
- Nos fusos de hora cheia, nada mudou: todos os testes anteriores passam sem alteração.
- A chave da API não aparece em nenhum arquivo do repositório.
- Como houve correção no produto, a fase 6 prevê publicar a versão `v0.1.1` (TS-6.3).

### Parecer

✅ **Sucesso, com escopo reduzido.** A fase cumpriu o objetivo com um único cenário: achou um defeito real do produto (DEF-01), fora do que o spec descrevia, e o corrigiu com testes que provam a correção. As outras categorias ficaram fora por custo, e a suíte atual já cobre boa parte delas.

---

## Fase 4 — Teste de mutação (2026-10-08)

**A ideia:** o teste de mutação testa os testes. O script planta um defeito pequeno no código (um **mutante**), roda os testes e confere se algum falha. Se falhar, o mutante foi **detectado**. Se todos passarem, ele **sobreviveu**, e isso indica um ponto que nenhum teste confere.

**Escopo reduzido (DT-06):** só o módulo `app/domain/precipitation.py`, pelo custo de tokens e de tempo num MVP acadêmico, em que o objetivo é aprender a técnica e não esgotá-la.

### Resultado

| Medida | Valor | Meta |
|---|---|---|
| Mutantes gerados | 35 | — |
| Detectados | 34 | — |
| **Escore de mutação** | **97,1%** | 80% |
| Sobreviventes | 1, equivalente (não muda o comportamento) | Cada um coberto ou justificado |
| Testes novos | 0 (nenhum sobrevivente revelou falha da suíte) | — |

### O que foi feito

1. **Criar o script (TS-4.1):** `tests/mutation.py`, sem dependência nova. Ele lê o módulo pela árvore sintática do Python (`ast`) e gera um mutante por ponto:
   - **Comparação:** `<` ↔ `<=`, `>` ↔ `>=`, `==` ↔ `!=`, `is` ↔ `is not`.
   - **Aritmética:** `+` ↔ `-`, `*` ↔ `/`.
   - **Lógica:** `and` ↔ `or`, e `not x` vira `x`.
   - **Constante:** número + 1 e texto vazio.
   - **Retorno:** o valor devolvido vira `None`.

   Para cada mutante, o script grava o módulo alterado, roda os testes de unidade e restaura o original, mesmo com erro.
2. **Rodar e medir (TS-4.2):** `python -m tests.mutation app/domain/precipitation.py tests/unit`. São 35 mutantes, cerca de 2 s cada, cerca de 1 min ao todo.
3. **Analisar o sobrevivente (TS-4.3):** ver abaixo.

### Por que este módulo

O `precipitation.py` tem 70 linhas e concentra o que a mutação mais testa: os limites das faixas de intensidade (RN-041), o arredondamento do volume (RN-037), o percentual (RN-036) e os valores ausentes ou negativos (RN-047). O `time.py` acabou de ser corrigido na fase 3, e a mutação vale mais num módulo que ainda não foi mexido.

### O sobrevivente

| Mutante | Onde | Decisão |
|---|---|---|
| `Decimal(text.replace(",", "."))` → `Decimal(text.replace(",", ""))` | `rain_label`, linha 47 | **Equivalente.** O código só confere se o volume arredondado é maior que zero. Tirar a vírgula ("0,21" → "021") multiplica o número por 100 sem mudar o sinal. Conferido com 200 mil valores aleatórios e os casos de borda (0,004, 0,005, negativos): o resultado é sempre o mesmo. Nenhum teste pode matar esse mutante |

### O que ficou de fora e por quê

| Fora | Por quê |
|---|---|
| Os outros 7 módulos de `app/domain/` | Custo (DT-06). O script já roda em qualquer um deles: basta trocar o caminho |
| `static/js/logic/` | Cada mutante do JS roda os testes de lógica no Chrome (cerca de 80 s). Com centenas de mutantes, seriam horas. A fase 2 já fez 10 mutantes manuais no JS, e todos foram detectados |
| Partes literais de f-strings (como " mm/h") | O script só muta as expressões dentro delas. Os textos fixos já são conferidos por igualdade exata nos testes |

### O que se aprendeu

- **A fase 2 aparece no escore.** O limite 2,51 entrou nos testes na fase 2. Com o arquivo de teste anterior, o mutante `2.5 → 3.5` sobrevive (conferido), e o escore cairia para 94,3%. O `7.5 → 8.5` já era pego pelo caso 8,0. Uma revisão bem feita sobe o escore de mutação.
- **Nem todo sobrevivente é falha do teste.** O mutante equivalente mostra que 100% nem sempre é possível. Por isso a análise de cada sobrevivente é parte da técnica, e não só o número.
- **Mutação mede o que a cobertura não mede.** A cobertura diz que a linha 47 roda. A mutação diz que cada operador e cada constante dela é conferido por algum teste.
- **O papel da IA:** escreveu o script com `ast`, escolheu o módulo, rodou a medição e provou a equivalência do sobrevivente com uma conferência automática.

### Verificações

- Suíte comum verde: 852 testes (o script não é um teste, e o pytest não o coleta). O ruff não aponta nada.
- O módulo foi restaurado depois de cada mutante: o `git status` não mostra mudança em `app/`.
- Nenhum defeito novo do produto: a fase 5 continua com 1 registro (DEF-01, corrigido).

### Parecer

✅ **Sucesso, com escopo reduzido.** O escore de 97,1% passa a meta de 80% com folga, e o único sobrevivente é equivalente e está justificado. O script fica pronto para medir os outros módulos se o projeto evoluir.

---

## Fase 6 — Relatório final (2026-10-08)

**A ideia:** fechar a etapa com os números finais, comparar com o ponto de partida e conferir os critérios de saída do plano.

### Resumo da etapa

A etapa de Testes começou com 839 testes verdes e terminou com 852. Nesse caminho, a IA:
- **mediu a cobertura** e fechou as últimas lacunas (fase 1);
- **revisou os testes** e corrigiu 31 pontos fracos (fase 2);
- **explorou um cenário fora do spec** e achou um defeito real (fase 3);
- **plantou defeitos no código** para medir a força dos testes (fase 4).

O produto ganhou uma correção (DEF-01), publicada na versão `v0.1.1`.

### Linha de base × fim da etapa

| Medida | Linha de base (v0.1.0, 2026-10-06) | Fim (v0.1.1, 2026-10-08) |
|---|---|---|
| Testes na suíte comum | 839 | **852** |
| Unidade e API (`pytest -m "not e2e"`) | 503 | **512** |
| Ponta a ponta e lógica JS (`pytest -m e2e`) | 336 | **340** |
| Cobertura do Python (linhas e ramos) | não medida (na fase 1: 99,7% das linhas e 5 ramos incompletos) | **100% e 0 ramos incompletos** (622 linhas) |
| Cobertura do JavaScript (linhas) | não medida (na fase 1: 99,9%) | **100%** (1.598 linhas, 8 parciais justificadas) |
| Escore de mutação (`precipitation.py`) | não medido | **97,1%** (34 de 35; o sobrevivente é equivalente) |
| Defeitos plantados detectados (fase 2) | 1 de 19 | **19 de 19** |
| Defeitos do produto conhecidos | 0 | 1 achado e corrigido (DEF-01) |
| Fumaça com o provedor real | 4 de 4 | 3 de 4 (DEF-02, falha do provedor) |

### Critérios de saída (plano, seção 4)

| Critério | Resultado |
|---|---|
| Cobertura ≥ 90% no Python e ≥ 85% no JavaScript | ✅ 100% e 100% |
| Mutação ≥ 80% no módulo escolhido (DT-06), com cada sobrevivente coberto ou justificado | ✅ 97,1%, e o sobrevivente é equivalente |
| Achados confirmados da revisão corrigidos | ✅ 31 de 31 |
| Nenhum defeito do produto em aberto sem decisão registrada | ✅ DEF-01 corrigido. DEF-02 é do provedor, com a decisão registrada |
| Relatório publicado e suíte comum verde | ✅ Este relatório, e 852 testes verdes |

### Defeitos

| ID | O que foi | Classificação | Decisão |
|---|---|---|---|
| DEF-01 | Hora da previsão errada em fusos com 30 ou 45 minutos ("00:00" em vez de "00:45" no Nepal) | Produto | Corrigido na fase 3, com testes de prova, e publicado na `v0.1.1` |
| DEF-02 | Na fumaça real, `/api/weather` devolveu `provider_timeout` | Ambiente (provedor) | O endpoint `timeline/1day` do OpenWeatherMap não respondeu nem em 60 s, em duas cidades, enquanto os outros respondiam em menos de 1 s. O backend agiu como o spec manda (RN-012). Sem mudança no código |

**O DEF-02 em detalhe:** a fumaça rodou duas vezes, e nas duas o log apontou a mesma chamada: `onecall/timeline/1day provider_timeout`. Duas chamadas diretas ao endpoint, fora do backend, também ficaram sem resposta (60 s em Uberlândia, 30 s em Tóquio). Na mesma hora, `current` respondia em 0,5 s. As outras 3 rotas da fumaça (busca, geocodificação reversa e tile do mapa) passaram. Em 2026-10-06, a mesma fumaça tinha passado inteira. O episódio mostrou uma evolução possível, registrada no README: quando só a previsão diária falha, mostrar os outros blocos em vez de derrubar a consulta inteira.

### Limitações da etapa

| Limitação | Efeito |
|---|---|
| Fases 3 e 4 com escopo reduzido (DT-06) | Fase 3: só a categoria de fusos exóticos. Fase 4: só `precipitation.py`, sem o JavaScript. O motivo foi o custo de tokens e de tempo num MVP acadêmico, em que o objetivo é aprender a técnica e não esgotá-la |
| Só o Chrome (L-01) | Diferenças em outros navegadores não são detectadas |
| Mapa base simulado (L-02) | A aparência real do mapa não é verificada |
| Provedor real só na fumaça | A fumaça depende da disponibilidade do provedor no momento, como mostrou o DEF-02 |
| Sem testes manuais (DT-01) | Toda verificação foi automatizada ou feita pela IA |

### O que a IA fez em cada fase

| Fase | Papel da IA |
|---|---|
| 1 — Cobertura | Escolheu a ferramenta (ADR-014), escreveu o plugin de cobertura do Chrome, classificou cada lacuna e escreveu os 7 testes que faltavam |
| 2 — Revisão | 5 agentes revisaram a suíte em paralelo, um por nível. A IA conferiu os 31 achados no código, corrigiu todos e provou cada correção com 19 defeitos plantados |
| 3 — Exploratório | Escolheu fusos que estressam a regra, explorou por script, achou o DEF-01 e propôs a correção mínima, compatível com os fusos de hora cheia |
| 4 — Mutação | Escreveu o script de mutação com `ast`, mediu o módulo e provou a equivalência do sobrevivente |
| 5 — Defeitos | Registrou o DEF-01 e o DEF-02 com causa, classificação e decisão. No DEF-02, isolou o endpoint culpado sem expor a chave |
| 6 — Relatório | Rodou a suíte final e a fumaça, consolidou os números e conferiu os critérios de saída. Também achou e corrigiu um erro de contagem da fase 1 |

### O que se aprendeu na etapa

- **Cada técnica responde a uma pergunta diferente.**
  - **Cobertura:** "o código rodou?".
  - **Revisão:** "alguém conferiu o resultado?".
  - **Exploratório:** "e o que ninguém especificou?".
  - **Mutação:** "os testes pegam um defeito?".

  A suíte tinha 100% de cobertura e mesmo assim deixava passar 18 de 19 defeitos plantados e um defeito real do produto.
- **A IA acelera, mas precisa de prova.** Em vários momentos, a afirmação da IA estava errada: o formato "0 mm/h", o mutante `7.5 → 8.5` que já era pego e a contagem de linhas parciais. Os defeitos plantados e as conferências automáticas foram o que separou o fato do palpite.
- **Escopo reduzido com justificativa é uma decisão de engenharia.** Um exemplo bem escolhido por técnica foi suficiente para aprender e para achar um defeito real.

### Verificações

- Suíte comum verde: 852 testes passando (512 + 340), com ruff sem apontamentos.
- Cobertura medida no fim: 100% no Python (linhas e ramos) e 100% das linhas no JavaScript.
- A chave da API não aparece em nenhum arquivo do repositório nem na saída da fumaça.
- README atualizado com os números finais e a versão `v0.1.1`.

### Parecer final da etapa

✅ **Sucesso.** Todos os critérios de saída foram atendidos, com as reduções de escopo registradas na DT-06. A etapa deixou uma suíte mais forte (31 pontos fracos corrigidos), um produto mais correto (DEF-01) e ferramentas reutilizáveis: o plugin de cobertura do JavaScript e o script de mutação. A única falha em aberto (DEF-02) é do provedor e está documentada, com uma evolução possível para o produto.
