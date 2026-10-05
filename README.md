# OpenWeather Dashboard

Dashboard web de página única que consome a API do [OpenWeatherMap](https://openweathermap.org/api) e mostra as **condições atuais**, a **previsão diária**, **hora a hora** e **por minuto** e um **mapa de chuva**. A cidade inicial vem da localização do navegador, e qualquer outra pode ser escolhida no campo de busca.

MVP acadêmico da pós-graduação, desenvolvido com apoio de IA Generativa em todas as etapas do SDLC.

> **Status:** 🚧 Requisitos ([docs/requisitos.md](docs/requisitos.md)), arquitetura ([docs/arquitetura.md](docs/arquitetura.md)) e plano de tarefas ([docs/tasks.md](docs/tasks.md)) definidos. O código da aplicação ainda não foi escrito, então os comandos abaixo passam a funcionar a partir da fatia 0 de implementação.
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
| Fonte de dados | [OpenWeatherMap](https://openweathermap.org/api): One Call API 4.0, Geocoding API e camada de precipitação | ✅ Definido |
| Backend | [Python](https://www.python.org/) 3.13.5 + [FastAPI](https://fastapi.tiangolo.com/) 0.142.2 + [Uvicorn](https://www.uvicorn.org/) 0.54.0 + [httpx](https://www.python-httpx.org/) 0.28.1 | ✅ Definido |
| Frontend | HTML, CSS e JavaScript puro (módulos ES), sem framework e sem build | ✅ Definido |
| Mapa | [Leaflet](https://leafletjs.com/) 1.9.4 + mapa base [CARTO Voyager](https://carto.com/basemaps) (dados © [OpenStreetMap](https://www.openstreetmap.org/copyright)) | ✅ Definido |
| Gráficos | SVG próprio, sem biblioteca | ✅ Definido |
| Testes | [pytest](https://docs.pytest.org/) 9.1.1 + [pytest-playwright](https://playwright.dev/python/) 0.9.0 (Chrome instalado) | ✅ Definido |
| Qualidade de código | [Ruff](https://docs.astral.sh/ruff/) 0.16.10 | ✅ Definido |
| Ambiente | [Anaconda](https://www.anaconda.com/) / conda (canal conda-forge) + pip | ✅ Definido |
| Versionamento | Git + [Conventional Commits](https://www.conventionalcommits.org/pt-br/) | ✅ Definido |
| Assistente de desenvolvimento | [Claude Code](https://claude.com/claude-code) + prompts CO-STAR | ✅ Definido |
| Hospedagem / deploy | Não se aplica: o MVP roda só localmente, em `127.0.0.1` | ✅ Definido |

As versões exatas de todas as dependências estão em [requirements.txt](requirements.txt), [requirements-dev.txt](requirements-dev.txt) e [environment.yml](environment.yml). As decisões e justificativas estão em [docs/arquitetura.md](docs/arquitetura.md).

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
│   ├── arquitetura.md       # Stack, decisões (ADR), contratos, convenções, testes e fatias
│   ├── tasks.md             # Tarefas por fatia, ponto de retomada e progresso da implementação
│   ├── prompts-costar.md    # Histórico de prompts por etapa do SDLC
│   └── referencia/
│       └── referencia_visual.png  # Print de referência visual do layout
├── .env.example             # Modelo do .env (sem a chave real)
├── .gitignore               # Deixa .env, caches do Python e resultados de teste fora do Git
├── environment.yml          # Ambiente conda: Python 3.13.5 + pip
├── requirements.txt         # Dependências de execução, com versões exatas
├── requirements-dev.txt     # Dependências de teste e qualidade, com versões exatas
├── CLAUDE.md                # Contexto e regras para o Claude Code
└── README.md                # Este arquivo
```

O código vai ficar em `app/` (backend Python), `static/` (frontend) e `tests/`, conforme a seção 5 de [docs/arquitetura.md](docs/arquitetura.md).

## Pré-requisitos

- [Git](https://git-scm.com/)
- Uma conta gratuita no [OpenWeatherMap](https://home.openweathermap.org/users/sign_up) com uma **API key**
- A assinatura **"One Call by Call"** da [One Call API 4.0](https://openweathermap.org/api/one-call-4) ativa na conta. Ela inclui 1.000 chamadas gratuitas por dia, e as chamadas acima disso são cobradas. Para não haver cobrança, configure o limite diário de chamadas em 1.000 na aba "Billing plans" da conta. A liberação de uma assinatura nova pode levar algum tempo
- [Anaconda](https://www.anaconda.com/download) ou Miniconda (para o ambiente com Python 3.13.5). Sem conda, serve o [Python 3.13](https://www.python.org/downloads/) com `venv`
- [Google Chrome](https://www.google.com/chrome/), usado pelos testes de ponta a ponta

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

A API key fica **somente** no arquivo `.env`, que o Git ignora. Nunca coloque a chave no código, em commits ou em prompts. Ela é lida pelo servidor Python e **nunca é enviada ao navegador**.

```bash
copy .env.example .env    # Anaconda Prompt / cmd. No Git Bash: cp .env.example .env
```

Depois, edite o `.env` e preencha a chave.

| Variável | Descrição | Exemplo |
|---|---|---|
| `OPENWEATHER_API_KEY` | API key do OpenWeatherMap | `sua_chave_aqui` |

### 4. Criar o ambiente e instalar as dependências

No **Anaconda Prompt** (ou no PowerShell depois de rodar `conda init powershell` uma vez):

```bash
conda env create -f environment.yml     # cria o ambiente openweather-dashboard (uma vez)
conda activate openweather-dashboard
```

Sem conda: `python -m venv .venv`, ative o ambiente e rode `pip install -r requirements-dev.txt`.

Depois de mudar os requirements: `conda env update -f environment.yml --prune`.

### 5. Rodar localmente

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --env-file .env --no-access-log --reload
```

Depois, abra <http://127.0.0.1:8000>. A documentação automática da API fica em <http://127.0.0.1:8000/docs>.

### 6. Rodar os testes

```bash
pytest -m "not e2e"                       # unidade e API (rápidos, sem internet)
pytest -m e2e                             # ponta a ponta no Chrome instalado
pytest -m live                            # fumaça com o provedor real (usa a cota)
ruff check . && ruff format --check .     # lint e formatação
```

## Exemplos de uso

> ⚠️ A interface ainda não existe. O fluxo abaixo é o previsto. Capturas de tela serão adicionadas depois da implementação.

1. Abra a aplicação no navegador e autorize o acesso à localização. Se você negar, o dashboard mostra Uberlândia, BR.
2. Veja as condições atuais, as abas de dias, a previsão hora a hora, a previsão por minuto e o mapa de chuva.
3. Para outra cidade, digite o nome no campo de busca (por exemplo, `Curitiba` ou `Santa Maria, BR`), pressione **Enter** ou clique na lupa e escolha um item da lista.
4. Clique em uma aba de dia para ver o resumo daquele dia, ou alterne entre **°C** e **°F** no cabeçalho.
5. Se a cidade não existir ou o serviço falhar, a aplicação mostra uma mensagem explicando o que fazer.

O navegador chama só as rotas do servidor local (`/api/weather`, `/api/geo/search`, `/api/geo/reverse` e `/api/tiles/precipitation/...`, detalhadas na seção 6 de [docs/arquitetura.md](docs/arquitetura.md)). O servidor acrescenta a chave e chama os endpoints do OpenWeatherMap abaixo (detalhes em [docs/spec.md](docs/spec.md)):

| Dado | Endpoint |
|---|---|
| Clima atual (One Call API 4.0) | `GET https://api.openweathermap.org/data/4.0/onecall/current?lat={lat}&lon={lon}&units=metric&lang=pt_br&appid={API_KEY}` |
| Previsão por minuto | `GET https://api.openweathermap.org/data/4.0/onecall/timeline/1min?lat={lat}&lon={lon}&units=metric&lang=pt_br&appid={API_KEY}` |
| Previsão por hora (2 páginas de 20 horas) | `GET https://api.openweathermap.org/data/4.0/onecall/timeline/1h?lat={lat}&lon={lon}&start={início}&units=metric&lang=pt_br&appid={API_KEY}` |
| Previsão diária | `GET https://api.openweathermap.org/data/4.0/onecall/timeline/1day?lat={lat}&lon={lon}&units=metric&lang=pt_br&appid={API_KEY}` |
| Vigência de cada alerta | `GET https://api.openweathermap.org/data/4.0/onecall/alert/{id}?appid={API_KEY}` |
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
- **[Arquitetura](docs/arquitetura.md):** decisões registradas (ADR), contratos, convenções, guardrails, estratégia de testes e plano de implementação em fatias, para que o código gerado pela IA seja correto e replicável.
- **[Tarefas](docs/tasks.md):** cada fatia quebrada em tarefas com checkbox, a fatia em que cada um dos 217 IDs (RF, RN, RNF, CA e princípios) é fechado e o bloco "Onde paramos", que diz a cada nova sessão de onde continuar. Cada tarefa é marcada assim que é concluída, e a fatia inteira vai para um único commit, junto com o código.

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

- **Projeto em arquitetura:** nenhuma funcionalidade foi implementada ainda.
- **Execução só local:** o servidor atende apenas em `127.0.0.1`. Não há deploy.
- **Limites do plano gratuito** do OpenWeatherMap: a One Call API 4.0 tem 1.000 chamadas gratuitas por dia, e cada consulta de clima usa 5 (dados atuais, por minuto, 2 páginas por hora e diária), mais 1 por alerta da cidade. O cache de 10 minutos por cidade reduz o consumo.
- **One Call API 4.0:** a 3.0, escolhida no início do projeto, foi descontinuada pelo fornecedor e não aceita novas assinaturas. O projeto usa a 4.0, lançada em junho de 2026 (decisão D-09 em [docs/tasks.md](docs/tasks.md) e ADR-013 em [docs/arquitetura.md](docs/arquitetura.md)).
- **Previsão por minuto:** não está disponível para todas as localidades.
- **Testado só no Google Chrome:** os testes automatizados rodam só no Chrome instalado. Edge, Firefox e Safari não são testados, nem em computador nem em celular (limitação L-01 de [docs/tasks.md](docs/tasks.md)).
- **Escopo reduzido:** sem favoritos, histórico de buscas, detalhes dos alertas ou preferências lembradas entre visitas.

### Próximos passos no MVP

- [x] Levantar os requisitos em [docs/requisitos.md](docs/requisitos.md)
- [x] Definir a stack, a arquitetura e o provedor de mapa base em [docs/arquitetura.md](docs/arquitetura.md)
- [x] Criar o `.env.example` e atualizar as instruções de execução
- [x] Planejar a implementação em tarefas por fatia em [docs/tasks.md](docs/tasks.md)
- [ ] Implementar as 7 features de [docs/spec.md](docs/spec.md), seguindo as tarefas de [docs/tasks.md](docs/tasks.md)
- [ ] Tratar os erros e casos de borda descritos no spec (cidade inexistente, localização negada, falha de rede, chave inválida etc.)
- [ ] Escrever testes e publicar a primeira release

### Evoluções possíveis

- Deploy em nuvem (o proxy local já mantém a API key fora do navegador)
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
| *Não lançada* | 2026-10-04 | Arquitetura | Documento de arquitetura, manifestos de dependências com versões exatas, `.env.example` e print de referência |
| `v0.1.0` (prevista) | ⚠️ A definir | Implementação | Primeira versão funcional do MVP, conforme [docs/spec.md](docs/spec.md) |

## Créditos

- **Autor:** Thiago Martins de Oliveira
- **Instituição / disciplina:** Universidade Federal de Goiás / Especialização em Engenharia de Software: Automação e Inovação com IA Generativa
- **Dados meteorológicos:** [OpenWeatherMap](https://openweathermap.org/), usados conforme os [termos de serviço](https://openweather.co.uk/storage/app/media/Terms/Openweather_terms_and_conditions_of_sale.pdf) e a licença de dados ([CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)) do provedor
- **Mapa:** [Leaflet](https://leafletjs.com/) (licença BSD-2-Clause) e mapa base © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright) © [CARTO](https://carto.com/attributions)
- **Assistência de desenvolvimento:** [Claude Code](https://claude.com/claude-code) (Anthropic)
