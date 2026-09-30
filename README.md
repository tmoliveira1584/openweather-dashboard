# OpenWeather Dashboard

Aplicação web frontend que consome a API do [OpenWeatherMap](https://openweathermap.org/api) e exibe **temperatura**, **umidade** e **previsão do tempo** de uma cidade, escolhida por um campo de busca.

MVP acadêmico da pós-graduação, desenvolvido com apoio de IA Generativa em todas as etapas do SDLC.

> **Status:** 🚧 Em setup. A estrutura do repositório está pronta, mas o código da aplicação ainda não foi escrito.
>
> Neste README, **⚠️ A definir** marca o que ainda não foi decidido.

---

## Sumário

- [Funcionalidades](#funcionalidades)
- [Tecnologias utilizadas](#tecnologias-utilizadas)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Pré-requisitos](#pré-requisitos)
- [Configuração do ambiente e execução local](#configuração-do-ambiente-e-execução-local)
- [Exemplos de uso](#exemplos-de-uso)
- [Processo de desenvolvimento com IA](#processo-de-desenvolvimento-com-ia)
- [Como contribuir](#como-contribuir)
- [Limitações e próximos passos](#limitações-e-próximos-passos)
- [Releases](#releases)
- [Créditos](#créditos)

---

## Funcionalidades

Escopo previsto para o MVP (será detalhado em [docs/requisitos.md](docs/requisitos.md)):

- [ ] Buscar uma cidade pelo nome
- [ ] Mostrar a temperatura atual
- [ ] Mostrar a umidade atual
- [ ] Mostrar a previsão dos próximos dias
- [ ] Avisar quando a cidade não for encontrada ou a API falhar

## Tecnologias utilizadas

| Camada | Tecnologia | Status |
|---|---|---|
| Fonte de dados | [OpenWeatherMap API](https://openweathermap.org/api) | ✅ Definido |
| Versionamento | Git + [Conventional Commits](https://www.conventionalcommits.org/pt-br/) | ✅ Definido |
| Assistente de desenvolvimento | [Claude Code](https://claude.com/claude-code) + prompts CO-STAR | ✅ Definido |
| Linguagem / framework frontend | ⚠️ A definir | Etapa de arquitetura |
| Build / bundler | ⚠️ A definir | Etapa de arquitetura |
| Estilização | ⚠️ A definir | Etapa de arquitetura |
| Testes | ⚠️ A definir | Etapa de arquitetura |
| Hospedagem / deploy | ⚠️ A definir | Etapa de deploy |

As decisões e justificativas vão ficar em [docs/arquitetura.md](docs/arquitetura.md).

## Estrutura do projeto

Estado atual:

```
openweather-dashboard/
├── .claude/
│   └── commands/
│       └── costar.md        # Comando /costar: reescreve pedidos em CO-STAR, registra e executa
├── docs/
│   ├── requisitos.md        # Requisitos do MVP
│   ├── arquitetura.md       # Stack e decisões de arquitetura
│   └── prompts-costar.md    # Histórico de prompts por etapa do SDLC
├── .gitignore               # Deixa .env, node_modules e artefatos de build fora do Git
├── CLAUDE.md                # Contexto e regras para o Claude Code
└── README.md                # Este arquivo
```

A pasta do código-fonte (por exemplo, `src/`): ⚠️ A definir junto com a stack.

## Pré-requisitos

- [Git](https://git-scm.com/)
- Uma conta gratuita no [OpenWeatherMap](https://home.openweathermap.org/users/sign_up) com uma **API key**
- Runtime e gerenciador de pacotes (por exemplo, Node.js + npm): ⚠️ A definir junto com a stack

## Configuração do ambiente e execução local

### 1. Clonar o repositório

```bash
git clone https://github.com/tmoliveira1584/openweather-dashboard.git
cd openweather-dashboard
```

### 2. Obter a API key do OpenWeatherMap

1. Crie uma conta em <https://home.openweathermap.org/users/sign_up>.
2. Abra **API keys** no seu perfil e copie a chave (ou gere uma nova).
3. Uma chave nova pode levar algumas horas para começar a funcionar.

### 3. Configurar as variáveis de ambiente

A API key fica **somente** no arquivo `.env`, que o Git ignora. Nunca coloque a chave no código, em commits ou em prompts.

```bash
cp .env.example .env    # ⚠️ O .env.example será criado quando a stack for definida
```

| Variável | Descrição | Exemplo |
|---|---|---|
| ⚠️ A definir (o prefixo depende da stack, por exemplo `VITE_`) | API key do OpenWeatherMap | `sua_chave_aqui` |

### 4. Instalar as dependências

```bash
# ⚠️ A definir junto com a stack (por exemplo, npm install)
```

### 5. Rodar localmente

```bash
# ⚠️ A definir junto com a stack (por exemplo, npm run dev)
```

Depois, abra o endereço mostrado no terminal (⚠️ a porta será definida junto com a stack).

### 6. Rodar os testes

```bash
# ⚠️ A definir junto com a stack
```

## Exemplos de uso

> ⚠️ A interface ainda não existe. O fluxo abaixo é o previsto. Capturas de tela serão adicionadas depois da implementação.

1. Abra a aplicação no navegador.
2. Digite o nome de uma cidade no campo de busca, por exemplo `Curitiba` ou `São Paulo`.
3. Pressione **Enter** ou clique em **Buscar**.
4. Veja a temperatura e a umidade atuais e a previsão dos próximos dias.
5. Se a cidade não existir, a aplicação mostra uma mensagem de erro.

Endpoints do OpenWeatherMap candidatos (a confirmar na etapa de requisitos):

| Dado | Endpoint |
|---|---|
| Tempo atual | `GET https://api.openweathermap.org/data/2.5/weather?q={cidade}&units=metric&lang=pt_br&appid={API_KEY}` |
| Previsão de 5 dias / 3 horas | `GET https://api.openweathermap.org/data/2.5/forecast?q={cidade}&units=metric&lang=pt_br&appid={API_KEY}` |

## Processo de desenvolvimento com IA

O projeto mostra como a IA Generativa pode ajudar em cada etapa do SDLC:

- **[CLAUDE.md](CLAUDE.md):** regras que o assistente segue em toda sessão (API key só via `.env`, explicar decisões antes de implementar, passos pequenos, Conventional Commits).
- **Comando `/costar <pedido>`:** reescreve um pedido livre no framework **CO-STAR** (Context, Objective, Style, Tone, Audience, Response), registra o prompt e depois o executa.
- **[docs/prompts-costar.md](docs/prompts-costar.md):** histórico dos prompts com data e etapa do SDLC (Setup, Requisitos, Arquitetura, Implementação, Testes, Deploy, Documentação).

## Como contribuir

1. Crie uma branch a partir da principal.
2. Faça mudanças pequenas e verificáveis.
3. Escreva os commits seguindo [Conventional Commits](https://www.conventionalcommits.org/pt-br/), por exemplo:
   ```
   feat(busca): adicionar campo de busca por cidade
   docs: atualizar instruções de execução no README
   ```
4. Abra um Pull Request descrevendo o que mudou e por quê.

## Limitações e próximos passos

### Limitações conhecidas

- **Projeto em setup:** nenhuma funcionalidade foi implementada ainda.
- **Exposição da API key:** numa aplicação só frontend, a chave vai junto no código entregue ao navegador e pode ser vista por qualquer usuário. O `.env` apenas a mantém fora do Git. Para um MVP acadêmico isso é aceitável, mas não para produção.
- **Limites do plano gratuito** do OpenWeatherMap: há limite de chamadas por minuto e por mês.
- **Escopo reduzido:** busca por nome de cidade, sem geolocalização, favoritos ou histórico.

### Próximos passos no MVP

- [ ] Levantar os requisitos em [docs/requisitos.md](docs/requisitos.md)
- [ ] Definir a stack e a arquitetura em [docs/arquitetura.md](docs/arquitetura.md)
- [ ] Criar o `.env.example` e atualizar as instruções de execução
- [ ] Implementar a busca e a exibição de temperatura, umidade e previsão
- [ ] Tratar erros (cidade inexistente, falha de rede, chave inválida)
- [ ] Escrever testes e publicar a primeira release

### Evoluções possíveis

- Backend ou função serverless intermediária (proxy) para esconder a API key
- Cache das respostas para reduzir chamadas à API
- Localização atual do usuário (Geolocation API)
- Cidades favoritas e histórico de buscas
- Alternar entre °C e °F
- Gráficos de previsão
- PWA com suporte offline
- Acessibilidade (WCAG) e internacionalização
- CI/CD com testes automatizados e deploy contínuo

## Releases

As versões seguem [Versionamento Semântico](https://semver.org/lang/pt-BR/) (`MAJOR.MINOR.PATCH`). As mudanças serão registradas neste README (ou num `CHANGELOG.md` futuro) a partir das mensagens de commit.

| Versão | Data | Etapa | Descrição |
|---|---|---|---|
| *Não lançada* | 2026-09-29 | Setup | Estrutura inicial: Git, `.gitignore`, `CLAUDE.md`, `docs/`, comando `/costar` e README |
| `v0.1.0` (prevista) | ⚠️ A definir | Implementação | Primeira versão funcional do MVP: busca, temperatura, umidade e previsão |

## Créditos

- **Autor:** Thiago Martins de Oliveira
- **Instituição / disciplina:** Universidade Federal de Goiás / Especialização em Engenharia de Software: Automação e Inovação com IA Generativa
- **Dados meteorológicos:** [OpenWeatherMap](https://openweathermap.org/), usados conforme os [termos de serviço](https://openweather.co.uk/storage/app/media/Terms/Openweather_terms_and_conditions_of_sale.pdf) e a licença de dados ([CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)) do provedor
- **Assistência de desenvolvimento:** [Claude Code](https://claude.com/claude-code) (Anthropic)
