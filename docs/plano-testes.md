# Plano de testes — OpenWeather Dashboard (MVP)

Plano da etapa de Testes do SDLC, que começa depois da implementação e da versão `v0.1.0`. Os testes da implementação comprovam os requisitos. Nesta etapa, eles passam a ser **medidos, revisados e reforçados**, com a IA conduzindo cada fase.

- **Precedência:** [constitution.md](constitution.md) > [spec.md](spec.md) > [arquitetura.md](arquitetura.md) > este arquivo. A estratégia de testes da implementação continua na seção 9 da arquitetura. Este plano não a repete: ele aponta para ela.
- **Retomada:** toda sessão da etapa de Testes começa pelo bloco "Onde paramos" abaixo, como o [tasks.md](tasks.md) fez na implementação.

## Onde paramos

> Atualize este bloco ao concluir cada tarefa, antes de passar para a próxima. Ele vai para o Git no commit do fim da fase.

| Item | Valor |
|---|---|
| Fase atual | 1 — Cobertura de código (não iniciada) |
| Próxima tarefa | TS-1.1 |
| Concluídas, ainda sem commit | — |
| Último commit da etapa | — |
| Defeitos registrados | 0 |

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
- Escore de mutação de pelo menos **80%** em `app/domain/` e `static/js/logic/`, com cada mutante sobrevivente coberto por um teste novo ou justificado como equivalente.
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
  - [ ] **TS-1.1** Decidir como medir o Python. O `pytest-cov` é a ferramenta comum, mas acrescentar dependência exige um ADR novo (guardrail 1 da arquitetura). Registrar o ADR ou a alternativa escolhida.
  - [ ] **TS-1.2** Medir o JavaScript pelo próprio Chrome, com a cobertura do protocolo de depuração (CDP) que o Playwright já acessa, sem dependência nova.
  - [ ] **TS-1.3** Listar os trechos sem cobertura, por arquivo, e classificar cada um: falta de teste, código morto ou tratamento defensivo.
  - [ ] **TS-1.4** Escrever os testes que faltam e remover o código morto confirmado.
- **Entregável:** números de cobertura por arquivo, antes e depois, e os testes novos.
- **Conclusão:** metas de cobertura da seção 4 atingidas ou com desvios justificados.

### Fase 2 — Revisão dos testes pela IA

- **Objetivo:** encontrar testes frágeis, asserções fracas e testes que passariam mesmo com o código errado.
- **Uso dos testes existentes:** os testes atuais são o alvo da revisão.
- **Tarefas:**
  - [ ] **TS-2.1** Revisar `tests/` com o `/code-review`, por nível (unidade, API, lógica JS e ponta a ponta).
  - [ ] **TS-2.2** Conferir cada achado e descartar os falsos positivos com o motivo.
  - [ ] **TS-2.3** Corrigir os achados confirmados: esperas por tempo fixo, asserções genéricas, dependência de ordem e duplicações.
- **Entregável:** lista de achados com a decisão de cada um, e as correções.
- **Conclusão:** nenhum achado confirmado em aberto, e a suíte verde.

### Fase 3 — Testes exploratórios automatizados

- **Objetivo:** buscar falhas fora do que o spec descreve, com cenários propostos pela IA.
- **Uso dos testes existentes:** os testes novos entram nos arquivos atuais, com os mesmos auxiliares (`weather_api.py`, `geo_api.py`, `tiles.py`, `clock.py`, `visibility.py` e `FakeProvider`).
- **Tarefas:**
  - [ ] **TS-3.1** Pedir à IA cenários "e se…" por categoria: entradas incomuns (acentos, cidades homônimas, termos enormes), dados extremos ou malformados do provedor, fusos exóticos (ex.: +05:45 e +14:00), falhas de rede no meio da consulta e sequências rápidas de ações.
  - [ ] **TS-3.2** Escolher os cenários com mais risco e transformar cada um em teste automatizado.
  - [ ] **TS-3.3** Cada teste que falhar vira um defeito na fase 5, com a correção e o teste como prova.
- **Entregável:** cenários avaliados e os testes novos.
- **Conclusão:** cenários escolhidos automatizados e defeitos encontrados registrados.

### Fase 4 — Teste de mutação

- **Objetivo:** provar que os testes detectam defeitos, introduzindo pequenas alterações no código (mutantes) e conferindo se algum teste falha.
- **Uso dos testes existentes:** a suíte atual é o "detector" avaliado. Para cada mutante, ela roda de novo.
- **Tarefas:**
  - [ ] **TS-4.1** Criar um script próprio de mutação, sem dependência nova. Ele troca operadores (`>=` por `>`, `+` por `-`, `and` por `or`), constantes e retornos, um de cada vez, roda os testes do módulo e restaura o arquivo.
  - [ ] **TS-4.2** Rodar sobre `app/domain/` (testes de unidade) e `static/js/logic/` (testes de lógica JS) e calcular o escore: mutantes detectados ÷ mutantes gerados.
  - [ ] **TS-4.3** Analisar os sobreviventes: escrever um teste para cada um que revele uma falha da suíte, ou justificá-lo como equivalente (a mudança não altera o comportamento).
- **Entregável:** script, escore antes e depois e a lista de sobreviventes com a decisão de cada um.
- **Conclusão:** meta de mutação da seção 4 atingida ou com desvios justificados.

### Fase 5 — Registro de defeitos (contínua)

- **Objetivo:** documentar cada defeito encontrado em qualquer fase.
- **Uso dos testes existentes:** cada defeito do produto termina com um teste que falhava antes da correção e passa depois, e a suíte completa roda como regressão.
- **Registro:** seção "Defeitos" deste plano, criada com o primeiro defeito encontrado: uma tabela com ID (DEF-xx), data, fase, descrição, causa, classificação (produto, teste ou ambiente), correção ou decisão, teste de prova e status.

### Fase 6 — Relatório final

- **Objetivo:** consolidar os resultados da etapa para a entrega acadêmica.
- **Uso dos testes existentes:** os resultados da suíte de 2026-10-06 são a linha de base, e o relatório compara com o fim da etapa.
- **Tarefas:**
  - [ ] **TS-6.1** Rodar a suíte completa e, uma vez, a fumaça `pytest -m live`.
  - [ ] **TS-6.2** Escrever `docs/relatorio-testes.md`: linha de base, cobertura, revisão, exploratórios, mutação, defeitos, limitações e o que a IA fez em cada fase.
  - [ ] **TS-6.3** Atualizar o README com os novos números e, se houve correção no produto, publicar a versão `v0.1.1` (tag enviada ao GitHub só com confirmação).
- **Entregável:** relatório final e README atualizado.
- **Conclusão:** critérios de saída da seção 4 atendidos.

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
