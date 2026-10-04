# OpenWeather Dashboard

MVP acadêmico (pós-graduação): dashboard web de página única que consome a OpenWeatherMap
One Call API 3.0 e mostra condições atuais, previsão diária, hora a hora, por minuto e mapa
de chuva da cidade do usuário (localização do navegador) ou de uma cidade buscada.

## Stack
- Backend: Python 3.13.5 (ambiente conda `openweather-dashboard`), FastAPI, Uvicorn e httpx. Versões exatas em `requirements.txt` e `requirements-dev.txt`.
- Frontend: HTML, CSS e JavaScript puro, sem build. Leaflet 1.9.4 em `static/vendor/`.
- Testes: pytest + pytest-playwright (Chrome instalado). Lint e formatação: ruff.
- Rodar: `uvicorn app.main:app --host 127.0.0.1 --port 8000 --env-file .env --no-access-log --reload`
- Testar: `pytest -m "not e2e"`, `pytest -m e2e` e `ruff check . && ruff format --check .`

## Regras
- A API key do OpenWeatherMap fica **somente** no `.env`. Nunca escreva a chave em código, commits, docs ou prompts.
- Antes de implementar, explique a decisão (o quê, por quê, alternativas) e aguarde confirmação.
- Trabalhe em passos pequenos e verificáveis, um de cada vez.
- Siga os princípios de `docs/constitution.md` e implemente conforme `docs/spec.md`, citando os IDs (RF, RN, RNF, CA).
- Implemente uma fatia por vez de `docs/arquitetura.md` (seção 10), respeitando contratos, guardrails (seção 8.4) e a definição de pronto (seção 9.4).
- Em toda sessão de implementação, comece por `docs/tasks.md` ("Onde paramos") e continue da próxima tarefa não marcada. Marque a tarefa (`[x]`) e atualize "Onde paramos" no mesmo commit do código.

## Commits
- Todo commit segue [Conventional Commits](https://www.conventionalcommits.org/pt-br/): `<tipo>(<escopo opcional>): <descrição>`.
- Tipos: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `build`, `ci`, `chore`, `perf`. Mudança incompatível: `!` após o tipo ou rodapé `BREAKING CHANGE:`.
- Descrição no imperativo, em português, com no máximo 72 caracteres.
- Se não der para definir com segurança o tipo, o escopo ou se há breaking change, proponha a mensagem e peça validação do usuário antes de commitar.

## Documentação
- `docs/requisitos.md`: índice dos artefatos de requisitos
- `docs/product-brief.md`: visão do produto, atores, fluxo e glossário geral
- `docs/constitution.md`: princípios permanentes (P-xxx), prevalecem sobre o spec
- `docs/spec.md`: especificação por feature (RF, RN, RNF, CA)
- `docs/arquitetura.md`: stack, decisões (ADR), contratos, convenções, testes e fatias de implementação
- `docs/tasks.md`: tarefas por fatia, ponto de retomada entre sessões e fatia em que cada ID é fechado
- `docs/referencia/referencia_visual.png`: print de referência visual (o spec prevalece em textos e formatos)
- `docs/prompts-costar.md`: histórico de prompts CO-STAR (use `/costar`)
