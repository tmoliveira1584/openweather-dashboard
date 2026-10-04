# OpenWeather Dashboard

MVP acadêmico (pós-graduação): dashboard web de página única que consome a OpenWeatherMap
One Call API 3.0 e mostra condições atuais, previsão diária, hora a hora, por minuto e mapa
de chuva da cidade do usuário (localização do navegador) ou de uma cidade buscada.

## Stack
A definir na etapa de arquitetura (ver `docs/arquitetura.md`).

## Regras
- A API key do OpenWeatherMap fica **somente** no `.env`. Nunca escreva a chave em código, commits, docs ou prompts.
- Antes de implementar, explique a decisão (o quê, por quê, alternativas) e aguarde confirmação.
- Trabalhe em passos pequenos e verificáveis, um de cada vez.
- Siga os princípios de `docs/constitution.md` e implemente conforme `docs/spec.md`, citando os IDs (RF, RN, RNF, CA).

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
- `docs/arquitetura.md`: stack e decisões de arquitetura
- `docs/prompts-costar.md`: histórico de prompts CO-STAR (use `/costar`)
