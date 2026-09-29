# OpenWeather Dashboard

MVP acadêmico (pós-graduação): aplicação web frontend que consome a API do
OpenWeatherMap e exibe temperatura, umidade e previsão por cidade, com campo de busca.

## Stack
A definir na etapa de arquitetura (ver `docs/arquitetura.md`).

## Regras
- A API key do OpenWeatherMap fica **somente** no `.env`. Nunca escreva a chave em código, commits, docs ou prompts.
- Antes de implementar, explique a decisão (o quê, por quê, alternativas) e aguarde confirmação.
- Trabalhe em passos pequenos e verificáveis, um de cada vez.

## Commits
- Todo commit segue [Conventional Commits](https://www.conventionalcommits.org/pt-br/): `<tipo>(<escopo opcional>): <descrição>`.
- Tipos: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `build`, `ci`, `chore`, `perf`. Mudança incompatível: `!` após o tipo ou rodapé `BREAKING CHANGE:`.
- Descrição no imperativo, em português, com no máximo 72 caracteres.
- Se não der para definir com segurança o tipo, o escopo ou se há breaking change, proponha a mensagem e peça validação do usuário antes de commitar.

## Documentação
- `docs/requisitos.md`: requisitos do MVP
- `docs/arquitetura.md`: stack e decisões de arquitetura
- `docs/prompts-costar.md`: histórico de prompts CO-STAR (use `/costar`)
