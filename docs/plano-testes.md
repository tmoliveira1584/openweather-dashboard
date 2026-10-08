# Plano de testes — OpenWeather Dashboard (MVP)

Plano da etapa de Testes do SDLC, que começa depois da implementação e da versão `v0.1.0`. Os testes da implementação comprovam os requisitos. Nesta etapa, eles passam a ser **medidos, revisados e reforçados**, com a IA conduzindo cada fase.

- **Precedência:** [constitution.md](constitution.md) > [spec.md](spec.md) > [arquitetura.md](arquitetura.md) > este arquivo. A estratégia de testes da implementação continua na seção 9 da arquitetura. Este plano não a repete: ele aponta para ela.
- **Retomada:** toda sessão da etapa de Testes começa pelo bloco "Onde paramos" abaixo, como o [tasks.md](tasks.md) fez na implementação.
- **Resultados:** ao fim de cada fase, antes do commit dela, o resultado entra numa seção nova do [relatorio-testes.md](relatorio-testes.md): números de antes e depois, o que foi feito, o que se aprendeu, as verificações e o parecer.

## Onde paramos

> Atualize este bloco ao concluir cada tarefa, antes de passar para a próxima. Ele vai para o Git no commit do fim da fase.

| Item | Valor |
|---|---|
| Fase atual | 4 — Teste de mutação (concluída) · próxima: 6 — Relatório final |
| Próxima tarefa | TS-6.1 |
| Concluídas, ainda sem commit | — |
| Último commit da etapa | Fase 4: `test(testes): medir a mutação do módulo de precipitação na fase 4` |
| Defeitos registrados | 1 (DEF-01, corrigido) |

## 1. Objetivo

Avaliar e melhorar a qualidade dos testes do MVP usando a IA Generativa em cada atividade: medir o que os testes executam, revisar a qualidade deles, buscar falhas fora do spec, provar que os testes detectam defeitos e consolidar os resultados num relatório para a entrega acadêmica.

## 2. Escopo

**Dentro do escopo**
- Código do backend (`app/`) e do frontend (`static/js/`).
- Os testes de `tests/` e os auxiliares deles (provedor, tiles e relógio simulados).
- Testes novos que surgirem das fases, sempre automatizados.

**Fora do escopo**
- **Testes manuais.** Toda verificação é automatizada ou feita pela IA. O intuito é aprender o uso da IA, não executar roteiros à mão.
- **Outros navegadores.** Só o Chrome instalado é testado (L-01).
- **O provedor real**, além da fumaça `pytest -m live`, que roda sob demanda e gasta a cota (cerca de 11 chamadas).
- **Carga, estresse e segurança ofensiva.** O MVP roda só em `127.0.0.1`, sem deploy.

## 3. Ponto de partida: os testes que já existem

Resultado de 2026-10-06, na versão `v0.1.0` (detalhes no README, seção "Rodar os testes"):

| Nível | Pasta | Testes | O que cobre |
|---|---|---|---|
| Unidade (Python) | `tests/unit/` | 303 | Regras de `app/domain/`, schemas, configuração, log e rastreabilidade dos requisitos |
| API | `tests/api/` | 200 (+4 `live`) | Rotas, validação, tradução de erros do provedor, chave nunca exposta, log sem coordenadas, `no-store` e acesso sem login |
| Lógica JavaScript | `tests/e2e/test_js_logic.py` | 100 | `state.js`, `cache.js`, `messages.js` e `static/js/logic/` |
| Ponta a ponta (Chrome) | `tests/e2e/` | 236 | As 7 features, os 44 CAs, teclado, 360 px, desempenho, privacidade, concorrência e passagem do tempo |

- **Total:** 839 testes na suíte comum, mais 4 de fumaça com o provedor real.
- **Rastreabilidade:** `tests/unit/test_traceability.py` garante que cada um dos 217 IDs (RF, RN, RNF, CA e P) tem pelo menos um teste (P-027).
- **Sem internet nem cota:** o provedor, as tiles do mapa e o relógio do navegador são simulados (arquitetura, seção 9.1).

**O que ainda não se sabe:** quanto do código esses testes executam e se eles detectariam um defeito introduzido no código. As fases abaixo respondem a essas perguntas.

## 4. Critérios de entrada e saída

**Entrada (para começar a etapa e cada fase)**
- Suíte comum verde: `pytest -m "not e2e"`, `pytest -m e2e` e `ruff check . && ruff format --check .`.
- Árvore de trabalho limpa no Git, com a fase anterior commitada.

**Saída (para encerrar a etapa)**
- Cobertura de linhas de pelo menos **90% no Python** e **85% no JavaScript**, com cada trecho abaixo disso coberto por um teste novo ou justificado no relatório.
- Escore de mutação de pelo menos **80%** no módulo escolhido para a fase 4 (escopo reduzido pela DT-06; a meta original valia para todo `app/domain/` e `static/js/logic/`), com cada mutante sobrevivente coberto por um teste novo ou justificado como equivalente.
- Todos os achados confirmados da revisão dos testes corrigidos.
- Nenhum defeito do produto em aberto sem decisão registrada.
- Relatório final publicado e suíte comum verde.

As metas são o ponto de partida. Se a fase 1 mostrar que uma delas não faz sentido, a mudança é registrada em "Decisões" com o motivo.

## 5. Fases da etapa

Cada fase tem objetivo, uso dos testes existentes, tarefas, entregável e critério de conclusão. As fases rodam em ordem, com um commit no fim de cada uma. A fase 5 é contínua: cada defeito é registrado assim que aparece, em qualquer fase.

### Fase 1 — Cobertura de código

- **Objetivo:** medir quanto do código a suíte executa e achar trechos nunca exercitados.
- **Uso dos testes existentes:** a suíte atual é o que roda durante a medição. A cobertura mede esses 839 testes.
- **Tarefas:**
  - [x] **TS-1.1** Decidir como medir o Python. O `pytest-cov` é a ferramenta comum, mas acrescentar dependência exige um ADR novo (guardrail 1 da arquitetura). Registrar o ADR ou a alternativa escolhida. → `coverage==7.16.2` ([ADR-014](arquitetura.md#adr-014--cobertura-do-python-com-coveragepy)).
  - [x] **TS-1.2** Medir o JavaScript pelo próprio Chrome, com a cobertura do protocolo de depuração (CDP) que o Playwright já acessa, sem dependência nova. → plugin `tests/js_coverage.py`, opção `--js-coverage`.
  - [x] **TS-1.3** Listar os trechos sem cobertura, por arquivo, e classificar cada um: falta de teste, código morto ou tratamento defensivo.
  - [x] **TS-1.4** Escrever os testes que faltam e remover o código morto confirmado.
- **Entregável:** números de cobertura por arquivo, antes e depois, e os testes novos.
- **Conclusão:** metas de cobertura da seção 4 atingidas ou com desvios justificados.

- **Resultado:** [relatorio-testes.md](relatorio-testes.md#fase-1--cobertura-de-código-2026-10-07).

### Fase 2 — Revisão dos testes pela IA

- **Objetivo:** encontrar testes frágeis, asserções fracas e testes que passariam mesmo com o código errado.
- **Uso dos testes existentes:** os testes atuais são o alvo da revisão.
- **Tarefas:**
  - [x] **TS-2.1** Revisar `tests/` com o `/code-review`, por nível (unidade, API, lógica JS e ponta a ponta). → O `/code-review` cobre só o diff. A suíte inteira foi revisada por 5 agentes em paralelo (DT-05).
  - [x] **TS-2.2** Conferir cada achado e descartar os falsos positivos com o motivo. → 31 achados, todos confirmados no código. Os candidatos que os próprios revisores descartaram ficaram registrados com o motivo.
  - [x] **TS-2.3** Corrigir os achados confirmados: esperas por tempo fixo, asserções genéricas, dependência de ordem e duplicações. → 31 corrigidos. 19 mutantes manuais provam as correções.
- **Entregável:** lista de achados com a decisão de cada um, e as correções.
- **Conclusão:** nenhum achado confirmado em aberto, e a suíte verde.

- **Resultado:** [relatorio-testes.md](relatorio-testes.md#fase-2--revisão-dos-testes-pela-ia-2026-10-07).

### Fase 3 — Testes exploratórios automatizados

> **Escopo reduzido (DT-06):** só a categoria de fusos exóticos, com +14:00 (Kiribati) e +05:45 (Nepal). As outras categorias ficaram fora, com o motivo no relatório.

- **Objetivo:** buscar falhas fora do que o spec descreve, com cenários propostos pela IA.
- **Uso dos testes existentes:** os testes novos entram nos arquivos atuais, com os mesmos auxiliares (`weather_api.py`, `geo_api.py`, `tiles.py`, `clock.py`, `visibility.py` e `FakeProvider`).
- **Tarefas:**
  - [x] **TS-3.1** Pedir à IA cenários "e se…" por categoria: entradas incomuns (acentos, cidades homônimas, termos enormes), dados extremos ou malformados do provedor, fusos exóticos (ex.: +05:45 e +14:00), falhas de rede no meio da consulta e sequências rápidas de ações.
  - [x] **TS-3.2** Escolher os cenários com mais risco e transformar cada um em teste automatizado.
  - [x] **TS-3.3** Cada teste que falhar vira um defeito na fase 5, com a correção e o teste como prova.
- **Entregável:** cenários avaliados e os testes novos.
- **Conclusão:** cenários escolhidos automatizados e defeitos encontrados registrados.

- **Resultado:** [relatorio-testes.md](relatorio-testes.md#fase-3--testes-exploratórios-automatizados-2026-10-08).

### Fase 4 — Teste de mutação

> **Escopo reduzido (DT-06):** o script roda sobre um único módulo de `app/domain/`. O JavaScript fica fora, com o motivo no relatório.

- **Objetivo:** provar que os testes detectam defeitos, introduzindo pequenas alterações no código (mutantes) e conferindo se algum teste falha.
- **Uso dos testes existentes:** a suíte atual é o "detector" avaliado. Para cada mutante, ela roda de novo.
- **Tarefas:**
  - [x] **TS-4.1** Criar um script próprio de mutação, sem dependência nova. Ele troca operadores (`>=` por `>`, `+` por `-`, `and` por `or`), constantes e retornos, um de cada vez, roda os testes do módulo e restaura o arquivo.
  - [x] **TS-4.2** Rodar sobre `app/domain/` (testes de unidade) e `static/js/logic/` (testes de lógica JS) e calcular o escore: mutantes detectados ÷ mutantes gerados. → Pela DT-06, só `app/domain/precipitation.py`: 34 de 35 (97,1%).
  - [x] **TS-4.3** Analisar os sobreviventes: escrever um teste para cada um que revele uma falha da suíte, ou justificá-lo como equivalente (a mudança não altera o comportamento).
- **Entregável:** script, escore antes e depois e a lista de sobreviventes com a decisão de cada um.
- **Conclusão:** meta de mutação da seção 4 atingida ou com desvios justificados.

- **Resultado:** [relatorio-testes.md](relatorio-testes.md#fase-4--teste-de-mutação-2026-10-08). Script: `tests/mutation.py` (`python -m tests.mutation app/domain/precipitation.py tests/unit`).

### Fase 5 — Registro de defeitos (contínua)

- **Objetivo:** documentar cada defeito encontrado em qualquer fase.
- **Uso dos testes existentes:** cada defeito do produto termina com um teste que falhava antes da correção e passa depois, e a suíte completa roda como regressão.
- **Registro:** seção "Defeitos" deste plano, criada com o primeiro defeito encontrado: uma tabela com ID (DEF-xx), data, fase, descrição, causa, classificação (produto, teste ou ambiente), correção ou decisão, teste de prova e status.

### Fase 6 — Relatório final

- **Objetivo:** consolidar os resultados da etapa para a entrega acadêmica.
- **Uso dos testes existentes:** os resultados da suíte de 2026-10-06 são a linha de base, e o relatório compara com o fim da etapa.
- **Tarefas:**
  - [ ] **TS-6.1** Rodar a suíte completa e, uma vez, a fumaça `pytest -m live`.
  - [ ] **TS-6.2** Consolidar o [relatorio-testes.md](relatorio-testes.md), que já traz uma seção por fase: resumo da etapa, comparação entre a linha de base e o fim, defeitos, limitações e o que a IA fez em cada fase.
  - [ ] **TS-6.3** Atualizar o README com os novos números e, se houve correção no produto, publicar a versão `v0.1.1` (tag enviada ao GitHub só com confirmação).
- **Entregável:** relatório final e README atualizado.
- **Conclusão:** critérios de saída da seção 4 atendidos.

### Defeitos

| ID | Data | Fase | Descrição | Causa | Classificação | Correção ou decisão | Teste de prova | Status |
|---|---|---|---|---|---|---|---|---|
| DEF-01 | 2026-10-08 | 3 | Num fuso com 45 ou 30 minutos (Nepal +05:45, Índia +05:30), a previsão hora a hora mostra "00:00" para a hora que começa às 00:45 locais (P-015) | `hour_label` montava `HH:00` e descartava os minutos do fuso: o spec (RN-035) só previa fusos de hora cheia | Produto | `hour_label` passa a mostrar o início da hora no fuso da cidade (`HH:MM`), igual a `HH:00` nos fusos de hora cheia. RN-035 e arquitetura (seção 7.5) atualizadas | `test_p_015_exotic_timezone_…[nepal_+05_45]` e `test_rn_035_hour_label` (casos +05:45, +05:30 e −03:30): falhavam antes e passam depois | Corrigido |

## 6. Limitações aceitas

| ID | Limitação | Efeito nos testes |
|---|---|---|
| L-01 | Só o Chrome instalado é testado ([tasks.md](tasks.md)) | Diferenças em Edge, Firefox, Safari e celular não são detectadas |
| L-02 | O mapa base do CARTO exige chave e mostra só a marca d'água ([tasks.md](tasks.md)) | Os testes usam tiles simuladas. A aparência real do mapa não é verificada |
| — | Os testes não usam o provedor real, salvo a fumaça `live` | Mudanças no formato da One Call 4.0 só aparecem na fumaça ou em uso |

## 7. Decisões

| ID | Data | Decisão |
|---|---|---|
| DT-01 | 2026-10-07 | A etapa de Testes tem um plano próprio, fora do [tasks.md](tasks.md), que continua sendo o plano da implementação. Sem testes manuais: tudo é automatizado ou feito pela IA |
| DT-02 | 2026-10-07 | Um commit por fase, no fim dela, com o tipo `test` ou `docs` e o escopo `testes`. Os prompts da etapa são registrados no [prompts-costar.md](prompts-costar.md) com a etapa "Testes" |
| DT-03 | 2026-10-07 | Cobertura do Python com `coverage==7.16.2`, só para desenvolvimento ([ADR-014](arquitetura.md#adr-014--cobertura-do-python-com-coveragepy)). Cobertura do JavaScript pelo V8 do Chrome via CDP, sem dependência nova, com as linhas parciais como medida complementar de ramos. As metas da seção 4 foram mantidas |
| DT-04 | 2026-10-07 | O resultado de cada fase é registrado no [relatorio-testes.md](relatorio-testes.md), numa seção didática por fase, criada no fim da fase e incluída no commit dela. A fase 6 consolida esse documento em vez de escrevê-lo do zero |
| DT-05 | 2026-10-07 | O `/code-review` revisa um diff, não uma pasta. Rodado sobre o último commit de `tests/`, não achou defeitos. A revisão da suíte inteira (TS-2.1) foi feita por 5 agentes de IA em paralelo, um por nível (unidade, API, lógica JS e ponta a ponta em duas partes), só com leitura e com a ordem de confirmar cada achado no código do produto. Cada correção de asserção é provada por um mutante manual que passava com o teste antigo e falha com o novo |
| DT-06 | 2026-10-08 | As fases 3 e 4 foram reduzidas a um exemplo cada, pelo custo de tokens e de tempo num MVP acadêmico, em que o objetivo é aprender a técnica e não esgotá-la. Fase 3: só o cenário de fusos exóticos (+14:00 e +05:45). Fase 4: o script de mutação roda sobre um único módulo Python de `app/domain/`, e a meta de 80% vale para ele. O relatório registra o que ficou de fora e por quê. O commit da fase 3 usa o tipo `fix`, e não `test` (DT-02), porque inclui a correção do DEF-01 no produto |
