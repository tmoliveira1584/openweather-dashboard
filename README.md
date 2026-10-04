# OpenWeather Dashboard

Dashboard web de página única que consome a API do [OpenWeatherMap](https://openweathermap.org/api) e mostra as **condições atuais**, a **previsão diária**, **hora a hora** e **por minuto** e um **mapa de chuva**. A cidade inicial vem da localização do navegador, e qualquer outra pode ser escolhida no campo de busca.

MVP acadêmico da pós-graduação, desenvolvido com apoio de IA Generativa em todas as etapas do SDLC.

> **Status:** 🚧 Requisitos especificados ([docs/requisitos.md](docs/requisitos.md)). A arquitetura ainda será definida, e o código da aplicação ainda não foi escrito.
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

Escopo do MVP, especificado em [docs/spec.md](docs/spec.md):

- [ ] Localização inicial pelo navegador (Uberlândia, BR, se não estiver disponível), busca de cidade e carregamento dos dados com cache de 10 minutos
- [ ] Condições atuais: temperatura, descrição, sensação térmica, alertas, vento, umidade, visibilidade, pressão, índice UV e ponto de orvalho
- [ ] Previsão diária em abas ("Hoje" + 7 dias)
- [ ] Previsão hora a hora (24 horas) com curva de temperatura e chance de chuva
- [ ] Previsão por minuto da precipitação na próxima hora, com legenda de cores
- [ ] Mapa com a camada de precipitação
- [ ] Alternância °C/°F, com vento em m/s ou mph

## Tecnologias utilizadas

| Camada | Tecnologia | Status |
|---|---|---|
| Fonte de dados | [OpenWeatherMap](https://openweathermap.org/api): One Call API 3.0, Geocoding API e camada de precipitação | ✅ Definido |
| Mapa base | ⚠️ A definir | Etapa de arquitetura |
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
│   ├── requisitos.md        # Índice dos artefatos de requisitos
│   ├── product-brief.md     # Visão do produto, atores, fluxo de uso e glossário geral
│   ├── constitution.md      # Princípios permanentes (P-xxx)
│   ├── spec.md              # Especificação por feature (RF, RN, RNF, CA)
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
- A assinatura **"One Call by Call"** ativa na conta, exigida pela [One Call API 3.0](https://openweathermap.org/api/one-call-3). Ela inclui 1.000 chamadas gratuitas por dia, e as chamadas acima disso são cobradas
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

1. Abra a aplicação no navegador e autorize o acesso à localização. Se você negar, o dashboard mostra Uberlândia, BR.
2. Veja as condições atuais, as abas de dias, a previsão hora a hora, a previsão por minuto e o mapa de chuva.
3. Para outra cidade, digite o nome no campo de busca (por exemplo, `Curitiba` ou `Santa Maria, BR`), pressione **Enter** ou clique na lupa e escolha um item da lista.
4. Clique em uma aba de dia para ver o resumo daquele dia, ou alterne entre **°C** e **°F** no cabeçalho.
5. Se a cidade não existir ou o serviço falhar, a aplicação mostra uma mensagem explicando o que fazer.

Endpoints do OpenWeatherMap usados (detalhes em [docs/spec.md](docs/spec.md)):

| Dado | Endpoint |
|---|---|
| Clima atual e previsões (One Call API 3.0) | `GET https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&units=metric&lang=pt_br&appid={API_KEY}` |
| Busca de cidade (geocodificação direta) | `GET https://api.openweathermap.org/geo/1.0/direct?q={cidade}&limit=5&appid={API_KEY}` |
| Nome da cidade por coordenadas (geocodificação reversa) | `GET https://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={API_KEY}` |
| Ícones | `https://openweathermap.org/img/wn/{icon}@2x.png` |
| Camada de precipitação do mapa | `https://tile.openweathermap.org/map/precipitation_new/{z}/{x}/{y}.png?appid={API_KEY}` |

## Processo de desenvolvimento com IA

O projeto mostra como a IA Generativa pode ajudar em cada etapa do SDLC:

- **[CLAUDE.md](CLAUDE.md):** regras que o assistente segue em toda sessão (API key só via `.env`, explicar decisões antes de implementar, passos pequenos, Conventional Commits).
- **Comando `/costar <pedido>`:** reescreve um pedido livre no framework **CO-STAR** (Context, Objective, Style, Tone, Audience, Response), registra o prompt e depois o executa.
- **[docs/prompts-costar.md](docs/prompts-costar.md):** histórico dos prompts com data e etapa do SDLC (Setup, Requisitos, Arquitetura, Implementação, Testes, Deploy, Documentação).
- **Spec-driven development:** os requisitos ficam em três artefatos, indexados em [docs/requisitos.md](docs/requisitos.md):
  - [product brief](docs/product-brief.md): a visão do produto
  - [constitution](docs/constitution.md): os princípios permanentes
  - [spec](docs/spec.md): requisitos em notação EARS e critérios de aceite Dado/Quando/Então

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

- **Projeto em requisitos:** nenhuma funcionalidade foi implementada ainda.
- **Exposição da API key:** numa aplicação só frontend, a chave vai junto no código entregue ao navegador e pode ser vista por qualquer usuário. O `.env` apenas a mantém fora do Git. Para um MVP acadêmico isso é aceitável, mas não para produção.
- **Limites do plano gratuito** do OpenWeatherMap: a One Call API 3.0 tem 1.000 chamadas gratuitas por dia. O cache de 10 minutos por cidade reduz o consumo.
- **One Call API 3.0:** o fornecedor recomenda a [One Call API 4.0](https://openweathermap.org/api/one-call-4) para novas integrações. A 3.0 foi escolhida por simplicidade, porque exige uma única chamada por cidade.
- **Previsão por minuto:** não está disponível para todas as localidades.
- **Escopo reduzido:** sem favoritos, histórico de buscas, detalhes dos alertas ou preferências lembradas entre visitas.

### Próximos passos no MVP

- [x] Levantar os requisitos em [docs/requisitos.md](docs/requisitos.md)
- [ ] Definir a stack, a arquitetura e o provedor de mapa base em [docs/arquitetura.md](docs/arquitetura.md)
- [ ] Criar o `.env.example` e atualizar as instruções de execução
- [ ] Implementar as 7 features de [docs/spec.md](docs/spec.md)
- [ ] Tratar os erros e casos de borda descritos no spec (cidade inexistente, localização negada, falha de rede, chave inválida etc.)
- [ ] Escrever testes e publicar a primeira release

### Evoluções possíveis

- Backend ou função serverless intermediária (proxy) para esconder a API key
- Migração para a One Call API 4.0
- Cidades favoritas, histórico de buscas e preferências lembradas entre visitas
- Detalhes dos alertas meteorológicos
- PWA com suporte offline
- Acessibilidade (WCAG) e internacionalização
- CI/CD com testes automatizados e deploy contínuo

## Releases

As versões seguem [Versionamento Semântico](https://semver.org/lang/pt-BR/) (`MAJOR.MINOR.PATCH`). As mudanças serão registradas neste README (ou num `CHANGELOG.md` futuro) a partir das mensagens de commit.

| Versão | Data | Etapa | Descrição |
|---|---|---|---|
| *Não lançada* | 2026-09-29 | Setup | Estrutura inicial: Git, `.gitignore`, `CLAUDE.md`, `docs/`, comando `/costar` e README |
| *Não lançada* | 2026-10-03 | Requisitos | Product brief, constitution e spec do MVP |
| `v0.1.0` (prevista) | ⚠️ A definir | Implementação | Primeira versão funcional do MVP, conforme [docs/spec.md](docs/spec.md) |

## Créditos

- **Autor:** Thiago Martins de Oliveira
- **Instituição / disciplina:** Universidade Federal de Goiás / Especialização em Engenharia de Software: Automação e Inovação com IA Generativa
- **Dados meteorológicos:** [OpenWeatherMap](https://openweathermap.org/), usados conforme os [termos de serviço](https://openweather.co.uk/storage/app/media/Terms/Openweather_terms_and_conditions_of_sale.pdf) e a licença de dados ([CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)) do provedor
- **Assistência de desenvolvimento:** [Claude Code](https://claude.com/claude-code) (Anthropic)
