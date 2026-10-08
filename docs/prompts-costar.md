# Prompts CO-STAR

## 2026-09-29 — Etapa: Setup

- **[C] Contexto:** Estou iniciando do zero um MVP para a pós-graduação: uma aplicação web frontend que consome a API do OpenWeatherMap e exibe temperatura, umidade e previsão por cidade, com campo de busca. A pasta openweather-dashboard ainda está vazia. Vou definir a stack na etapa de arquitetura.
- **[O] Objetivo:** Prepare a estrutura inicial do projeto, sem escrever código da aplicação:
  1. Execute git init e crie um .gitignore que inclua .env e node_modules
  2. Crie um CLAUDE.md curto com descrição, regras (API key só via .env, explicar decisões antes de implementar, passos pequenos) e stack "a definir"
  3. Crie a pasta docs/ com requisitos.md, arquitetura.md e prompts-costar.md vazios, só com título
  4. Crie o comando .claude/commands/costar.md, que reescreve meu pedido em CO-STAR, registra em docs/prompts-costar.md com data e etapa do SDLC e depois executa
- **[S] Estilo:** Didático e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Liste os arquivos que serão criados e explique em uma frase a função de cada um. Peça minha confirmação antes de criá-los.

## 2026-09-29 — Etapa: Setup

- **[C] Contexto:** A estrutura inicial do MVP está criada (git init, .gitignore, CLAUDE.md, docs/ e o comando /costar), mas ainda não há nenhum commit. O CLAUDE.md não define um padrão para as mensagens de commit.
- **[O] Objetivo:** Acrescente ao CLAUDE.md uma instrução para que todo commit siga Conventional Commits e para que, quando não for possível definir com segurança o tipo, o escopo ou se há breaking change, você proponha a mensagem e peça minha validação antes de commitar.
- **[S] Estilo:** Didático e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Resuma em poucas linhas a regra adicionada e sugira uma mensagem para o primeiro commit.

## 2026-09-29 — Etapa: Setup

- **[C] Contexto:** O MVP está na fase de setup. Já existem Git, .gitignore, CLAUDE.md (com Conventional Commits), docs/ e o comando /costar. Ainda não defini stack, licença e autoria, e não há código da aplicação.
- **[O] Objetivo:** Crie um README.md com base no que já está definido, marcando o que ainda não foi decidido, com no mínimo:
  1. Título e breve descrição
  2. Instruções detalhadas de configuração do ambiente e execução local
  3. Exemplos de uso da aplicação
  4. Lista de tecnologias utilizadas
  5. Limitações e próximos passos (o que foi implementado e o que poderia evoluir)
  6. Créditos e licença
  7. Release
  8. Outras seções consideradas padrão em um README
- **[S] Estilo:** Didático e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Crie o README.md na raiz e resuma o conteúdo de cada seção, apontando as pendências que ainda preciso preencher.

## 2026-09-29 — Etapa: Setup

- **[C] Contexto:** A estrutura inicial do MVP está pronta (.gitignore, CLAUDE.md, README.md, docs/ e o comando /costar), mas ainda não há nenhum commit. O CLAUDE.md exige Conventional Commits, e o Git local não tem autor configurado.
- **[O] Objetivo:**
  1. Configure o autor do Git somente neste repositório (Thiago Martins de Oliveira, oliveira.thiago@discente.ufg.br)
  2. Faça o primeiro commit com todos os arquivos, usando a descrição "criação da estrutura inicial do projeto" adaptada ao padrão Conventional Commits
  3. Como essa descrição não tem tipo nem está no imperativo, proponha a mensagem adaptada e peça minha validação antes de commitar
- **[S] Estilo:** Didático e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Mostre a mensagem de commit proposta para eu validar e, depois do commit, informe o hash e o autor registrado.

## 2026-09-29 — Etapa: Setup

- **[C] Contexto:** O primeiro commit existe localmente na branch `master`. O repositório remoto https://github.com/tmoliveira1584/openweather-dashboard foi criado vazio no GitHub.
- **[O] Objetivo:**
  1. Verifique se o repositório remoto está vazio, para evitar conflito de histórico
  2. Proponha renomear a branch principal de `master` para `main` (padrão do GitHub) e só renomeie depois da minha validação
  3. Adicione o remoto `origin` e envie a branch `main`, deixando-a ligada a `origin/main`
- **[S] Estilo:** Didático e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Confirme o push e informe a branch padrão no GitHub e o estado de sincronização entre local e remoto.

## 2026-09-30 — Etapa: Setup

- **[C] Contexto:** O commit `0caa502` (registro dos prompts do primeiro commit e da sincronização) foi feito localmente, e a branch `main` está um commit à frente de `origin/main`.
- **[O] Objetivo:** Envie o commit ao GitHub com `git push` e confirme que local e remoto ficaram sincronizados.
- **[S] Estilo:** Didático e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Confirme o push e o estado de sincronização e liste as pendências que ainda estão em aberto.

## 2026-09-30 — Etapa: Setup

- **[C] Contexto:** O repositório remoto já existe no GitHub, mas o passo "Clonar o repositório" do README ainda mostra `<url-do-repositorio>` marcado como "⚠️ A definir".
- **[O] Objetivo:** Troque o marcador do comando `git clone` no README pelo endereço real https://github.com/tmoliveira1584/openweather-dashboard.git e remova o aviso de pendência.
- **[S] Estilo:** Didático e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Confirme a alteração no README.

## 2026-09-30 — Etapa: Setup

- **[C] Contexto:** Há alterações locais no README (endereço do repositório) e em docs/prompts-costar.md (novos registros). O CLAUDE.md exige Conventional Commits. A pasta `.claude/commands/` deve continuar versionada.
- **[O] Objetivo:**
  1. Faça um commit com as alterações do README e de docs/prompts-costar.md, seguindo Conventional Commits
  2. Envie o commit ao GitHub com `git push`
- **[S] Estilo:** Didático e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe a mensagem e o hash do commit, confirme o push e mostre o estado de sincronização entre local e remoto.

## 2026-10-03 — Etapa: Requisitos

- **[C] Contexto:**
  - **Produto:** o MVP está na fase de requisitos. É uma página única que reproduz o layout de um print de referência e consome a OpenWeatherMap One Call API 3.0 (clima atual, previsão por minuto, por hora, por dia e alertas), a Geocoding API (busca direta e reversa), o serviço de ícones e a camada de precipitação do mapa.
  - **API:** escolhi a 3.0 em vez da 4.0 por simplicidade: uma única chamada por cidade, sem paginação e com melhor aproveitamento da cota gratuita. O fornecedor recomenda a 4.0 para novas integrações, e isso deve ficar registrado como risco.
  - **Cidade inicial:** vem da localização do navegador. Se a permissão for negada, o recurso não existir ou não houver resposta em 10 s, usa Uberlândia (lat -18.9186, lon -48.2772) e mostra um aviso.
  - **Idioma:** interface toda em pt-BR, com horário em 24h.
  - **Mapeamento tela → dados:**
    - Header: título, alternância °C/°F, cidade atual e busca
    - Abas: Today + 7 dias, como a API entrega (`daily[].temp.max`, ícone)
    - Card principal: `current.temp`, descrição, `feels_like`, `dt`, contagem de `alerts` e imagem por grupo de condição
    - 6 cards: vento com direção em rosa de 8 pontos, umidade, visibilidade, pressão, índice UV e ponto de orvalho
    - Previsão por hora: curva de temperatura das próximas 24 h, cards com ícone, `pop` e temperatura, e etiquetas de `rain.1h`
    - Previsão por minuto: barras de `minutely[].precipitation`, com marcos Agora, +15, +30, +45 e +60 min e legenda de 5 faixas
    - Mapa: marcador da cidade, camada de chuva e mapa base com atribuição
  - **Regras gerais:**
    - Horário local da cidade e visibilidade em km
    - °C/°F convertido localmente, sem nova chamada, com o vento acompanhando (m/s ↔ mph)
    - No máximo uma chamada por cidade a cada 10 min (cache em memória)
    - A aba Today mostra `current`. As demais mostram o resumo de `daily` (máxima/mínima, descrição, sensação, data, visibilidade "—"), enquanto as previsões por hora e por minuto continuam no momento atual
    - Cores das barras de precipitação: 0 cinza, (0; 0,5] verde, (0,5; 2,5] verde-escuro, (2,5; 7,5] amarelo, > 7,5 vermelho
    - O badge de alertas mostra só a contagem
  - **Situação atual:** a stack será definida na etapa de arquitetura. Hoje `docs/requisitos.md` contém só o título.
- **[O] Objetivo:**
  1. Crie `docs/product-brief.md` com: explicação do produto, razão de existir, atores, diagrama Mermaid do fluxo de uso, glossário geral e disclaimer de finalidade didática.
  2. Crie `docs/constitution.md` com princípios permanentes e transversais (P-001, P-002…), cada um em uma linha, no imperativo, no formato SEMPRE/NUNCA e sem justificativa longa.
  3. Crie `docs/spec.md` com uma seção por feature, sem código de feature: Localização inicial e busca de cidade; Condições atuais; Previsão diária; Previsão hora a hora; Previsão por minuto; Mapa de precipitação; Alternância de unidades.
     - Cada feature deve conter: Problema; Atores (Ator, Descrição, O que pode fazer, O que não pode fazer); Escopo (incluso / não incluso); Histórias de usuário ("Como <ator>, quero <ação>, para <resultado>"); Requisitos funcionais em notação EARS; Regras de negócio (a lógica por trás dos RFs); Comportamento em erro e casos de borda (Cenário, Comportamento esperado, Mensagem ao usuário); Requisitos não-funcionais (ID, Categoria, Requisito); Dependências e premissas; Critérios de aceite em Given/When/Then (3 a 8 por feature); Glossário específico.
     - Numere RF, RN, RNF e CA em sequência no documento inteiro.
  4. Monte a tabela de erros com um roteiro próprio do produto (só leitura, sem login, dependente de API externa): entrada inválida; localização do navegador; credencial e cota; serviço externo indisponível, lento ou sem conexão; resposta incompleta; valores-limite; ações repetidas e concorrentes; cache e tempo; recursos visuais; volume e tela. Não encaixe à força cenários que não se aplicam.
  5. Não inclua nenhum detalhe de stack tecnológica.
  6. Transforme `docs/requisitos.md` em índice dos três artefatos.
  7. Varra todo o diretório do projeto (CLAUDE.md, README, docs/, .claude/, .gitignore) e atualize o que deixar de ser verdade com estas decisões.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Entregue os três artefatos em Markdown e o índice em `docs/requisitos.md`. Liste os arquivos alterados na varredura, com o motivo de cada mudança, e resuma as quantidades (features, RF, RN, RNF, CA, princípios).

## 2026-10-04 — Etapa: Requisitos

- **[C] Contexto:** A etapa de requisitos está concluída, mas ainda não foi commitada: há os artefatos novos (`docs/product-brief.md`, `docs/constitution.md` e `docs/spec.md`, com glossário consolidado) e as alterações em `docs/requisitos.md` (agora índice), CLAUDE.md, README e `docs/prompts-costar.md`. A branch `main` local está sincronizada com `origin/main` (https://github.com/tmoliveira1584/openweather-dashboard). O CLAUDE.md exige Conventional Commits.
- **[O] Objetivo:**
  1. Proponha a mensagem de commit seguindo Conventional Commits e aguarde a minha validação antes de commitar
  2. Depois que eu validar, faça um único commit com todas as alterações da etapa de requisitos
  3. Envie o commit ao GitHub com `git push` e confirme a sincronização entre local e remoto
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Mostre a mensagem de commit proposta para eu validar. Depois do commit, informe o hash, confirme o push e mostre o estado de sincronização.

## 2026-10-04 — Etapa: Arquitetura

- **[C] Contexto:**
  - A etapa de requisitos está concluída e commitada (`a63e0c3`): product brief, constitution (P-001 a P-027) e spec com 7 features (RF-001 a RF-058, RN-001 a RN-059, RNF-001 a RNF-029, CA-001 a CA-044).
  - Agora entramos na fase de arquitetura. Hoje `docs/arquitetura.md` tem só o título, e o provedor de mapa base continua pendente.
  - Não tenho experiência com definição de arquitetura de software. Meu objetivo é aprender a usar IA no ciclo do SDLC, não me tornar arquiteto.
  - A aplicação vai rodar só localmente, sem instalar nenhum software novo. Na minha máquina já estão instalados Node.js 22 com npm 10, Git, VS Code e Google Chrome. O Python não está instalado.
- **[O] Objetivo:**
  1. Proponha uma arquitetura eficiente, mas simples de entender e de implementar, que rode localmente apenas com o que já está instalado
  2. Explique brevemente cada componente, por que você o escolheu e quais alternativas descartou
  3. Garanta que a proposta atenda a todo o escopo dos documentos (7 features do spec e princípios da constitution), com uma matriz de cobertura
  4. Defina o provedor de mapa base
  5. Não escreva ainda o `docs/arquitetura.md`
- **[S] Estilo:** Didático e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Apresente a proposta de arquitetura com visão geral em diagrama, componentes com função e justificativa, alternativas descartadas, estrutura de pastas, estratégia de testes, matriz de cobertura do escopo e riscos. Ao final, liste os pontos que preciso validar antes de registrarmos tudo em `docs/arquitetura.md`.

## 2026-10-04 — Etapa: Arquitetura

- **[C] Contexto:**
  - A arquitetura do MVP está definida.
  - **Backend:** Python 3.13 (em um ambiente conda do Anaconda que já tenho instalado), com FastAPI, Uvicorn, httpx e python-dotenv, no padrão BFF. O proxy guarda a chave só no servidor e devolve regras de negócio e textos prontos nas duas escalas.
  - **Frontend:** HTML, CSS e JavaScript puro, sem build, com Leaflet 1.9.4 copiado para o projeto, mapa base CARTO Voyager e gráficos em SVG próprio. O cache fica no navegador (P-007).
  - **Testes:** pytest e pytest-playwright, usando o Chrome instalado.
  - **Convenções:** identificadores em inglês, interface e comentários em pt-BR.
  - **Print de referência:** está em `docs/referencia/referencia_visual.png`. Ele é referência visual, e o spec prevalece em textos e formatos.
  - **Situação atual:** hoje `docs/arquitetura.md` tem só o título, e o README e o CLAUDE.md ainda mostram a stack como "a definir".
- **[O] Objetivo:**
  1. Escreva `docs/arquitetura.md` com essa arquitetura, incluindo as seções que garantem:
     - **Replicação:** versões, decisões registradas, guardrails e relógio injetável
     - **Geração correta de código, sem lacunas:** contratos, modelo de dados, view model, estado, regras de dependência, mensagens e erros, decisões de detalhe e tokens visuais
     - **Geração eficiente:** fatias de implementação, definição de pronto, estratégia de testes, convenções e guia rápido
  2. Registre as versões exatas em `requirements.txt`, `requirements-dev.txt` e `environment.yml`, conferidas contra o Python 3.13
  3. Vasculhe o projeto (CLAUDE.md, README, docs/, .gitignore, .claude/) e atualize o que deixou de ser verdade
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Resuma tudo o que foi criado e alterado, com o motivo de cada mudança, para eu validar antes do commit.

## 2026-10-04 — Etapa: Arquitetura

- **[C] Contexto:** O `docs/arquitetura.md` já está escrito, mas a seção 2.2 traz um diagrama de sequência que cobre só a troca de cidade.
- **[O] Objetivo:**
  1. Crie um diagrama de sequência Mermaid que descreva o fluxo completo da aplicação, componente a componente, cobrindo:
     - a entrega da página pelo FastAPI e a inscrição dos blocos no estado
     - o pedido de localização com prazo de 10 s, com geocodificação reversa ou a cidade padrão
     - a consulta ao cache e a chamada do backend ao OpenWeatherMap com a chave, que devolve o view model
     - o descarte de respostas antigas, o desenho dos blocos e o carregamento das tiles do mapa
     - as interações do usuário: escala, aba, busca e retorno à página
  2. Substitua o diagrama da seção 2.2 por esse diagrama, para mantermos uma única fonte do fluxo técnico
  3. Acrescente uma legenda de leitura e a regra de que o diagrama muda junto com contratos e fluxos
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Confirme a troca da seção 2.2, com o novo título e a legenda.

## 2026-10-04 — Etapa: Arquitetura

- **[C] Contexto:**
  - A etapa de arquitetura está concluída, mas os arquivos dela ainda não foram commitados:
    - Novos: `docs/arquitetura.md` (com o diagrama de sequência completo), `requirements.txt`, `requirements-dev.txt`, `environment.yml`, `.env.example` e o print `docs/referencia/referencia_visual.png`
    - Alterados: CLAUDE.md, README, `.gitignore`, `docs/spec.md`, `docs/product-brief.md`, `docs/requisitos.md` e os registros de prompt
  - A branch `main` local está sincronizada com `origin/main`.
- **[O] Objetivo:**
  1. Faça um único commit com todas as alterações da etapa de arquitetura, usando a mensagem `docs(arquitetura): definir arquitetura, stack e versões do MVP`
  2. Envie o commit ao GitHub com `git push` e confirme a sincronização entre local e remoto
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe o hash do commit e a lista de arquivos incluídos, confirme o push e mostre o estado de sincronização.

## 2026-10-04 — Etapa: Documentação

- **[C] Contexto:** Os registros de `docs/prompts-costar.md` estão escritos do ponto de vista do assistente, com construções como "validado pelo usuário" e "pedi na conversa". O objetivo do registro é guardar o que eu solicito. A reescrita em CO-STAR serve só para acelerar o meu trabalho: eu descrevo o necessário e o prompt é documentado de forma completa, mas na minha voz, como se eu tivesse escrito.
- **[O] Objetivo:**
  1. Revise todos os registros de `docs/prompts-costar.md` para a primeira pessoa, com ordens diretas no objetivo e na resposta
  2. Transforme o que aconteceu na conversa em pedidos naturais e independentes (ex.: "Crie um diagrama…" em vez de "Pedi na conversa um diagrama…"), para que um prompt flua naturalmente para o outro
  3. Inclua essa regra em `.claude/commands/costar.md`, para que todo registro futuro já siga esse padrão
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe apenas que as alterações foram feitas, para eu validar.

## 2026-10-04 — Etapa: Documentação

- **[C] Contexto:** Há alterações locais em `docs/prompts-costar.md` (registros reescritos na minha voz) e em `.claude/commands/costar.md` (regra de escrita dos registros). A branch `main` local está sincronizada com `origin/main`. O CLAUDE.md exige Conventional Commits.
- **[O] Objetivo:**
  1. Faça um commit com essas alterações, usando a mensagem `docs(prompts): reescrever registros na voz do autor e ajustar /costar`
  2. Envie o commit ao GitHub com `git push` e confirme a sincronização entre local e remoto
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe o hash do commit e os arquivos incluídos, confirme o push e mostre o estado de sincronização.

## 2026-10-04 — Etapa: Implementação

- **[C] Contexto:** Concluí os requisitos (product brief, constitution e spec) e a arquitetura, e estou entrando na fase de implementação. A seção 10 de `docs/arquitetura.md` define 14 fatias, mas cita os IDs por faixa e deixa o detalhamento em tarefas para um `docs/tasks.md` futuro. Quero que qualquer sessão futura de geração de código saiba exatamente de onde continuar. Os testes vão rodar só no Google Chrome instalado: não vou testar em outros navegadores.
- **[O] Objetivo:**
  1. Avalie todos os documentos do projeto e aponte o que falta para que o plano de implementação cubra 100% dos requisitos
  2. Crie o `docs/tasks.md`, versionado no Git (fora do `.gitignore`, porque é um artefato do processo), com:
     - tarefas em checkbox por fatia, pequenas o bastante para caber numa sessão, terminando cada fatia na definição de pronto
     - um bloco "Onde paramos", com a fatia atual, a próxima tarefa e o último commit
     - uma tabela de progresso por fatia
     - a regra de marcar a tarefa no mesmo commit do código que a conclui
  3. Divida a fatia 6 em 6a (estado, cache e chamadas ao backend), 6b (cabeçalho, busca e seletor de escala) e 6c (localização inicial e cidade padrão)
  4. Atribua cada um dos 217 IDs (RF, RN, RNF e CA do spec, mais P-001 a P-027) a uma única fatia, a que o fecha, e confira por script que nenhum fica de fora ou repetido
  5. Registre como limitação L-01 que os testes são feitos só no Chrome, no `docs/tasks.md`, na arquitetura e no README, mantendo o RNF-006 no spec como meta
  6. Faça o CLAUDE.md, a arquitetura (seções 1, 9.4, 10 e 13), o README e o `docs/requisitos.md` apontarem para o `docs/tasks.md`
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Resuma o trabalho: arquivos criados e alterados, estrutura do `docs/tasks.md` e decisões registradas. Proponha a mensagem de commit e aguarde a minha validação antes de commitar.

## 2026-10-04 — Etapa: Implementação

- **[C] Contexto:** Há alterações locais ainda não commitadas do planejamento da implementação:
  - Novo: `docs/tasks.md`
  - Alterados: CLAUDE.md, README, `docs/arquitetura.md`, `docs/requisitos.md` e `docs/prompts-costar.md`
  - A branch `main` local está sincronizada com `origin/main`. O CLAUDE.md exige Conventional Commits.
- **[O] Objetivo:**
  1. Faça um único commit com essas alterações, usando a mensagem `docs(tasks): planejar implementação em tarefas por fatia`, com um corpo que resuma o tasks.md e a limitação L-01 e cite o P-027
  2. Envie o commit ao GitHub com `git push` e confirme a sincronização entre local e remoto
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe o hash do commit e os arquivos incluídos, confirme o push e mostre o estado de sincronização.

## 2026-10-05 — Etapa: Implementação

- **[C] Contexto:**
  - Concluí o setup, os requisitos, a arquitetura e o planejamento. Agora vou começar a implementação do MVP pela fatia 0 (Setup) de `docs/tasks.md`. O bloco "Onde paramos" mostra a fatia 0 ainda não iniciada, com a próxima tarefa T-0.1 e 0 de 217 IDs fechados.
  - A fatia 0 vai da tarefa T-0.1 até a T-0.9. Ela segue as seções 1, 5.1, 7.6, 9.1, 9.2 e 11 de `docs/arquitetura.md` e fecha o P-002.
  - Por enquanto o repositório só tem a documentação, o `environment.yml`, o `requirements.txt`, o `requirements-dev.txt` e o `.env.example`. Ainda não existe código nem `.env`.
  - A T-0.8 precisa do `.env` com a minha chave e da assinatura "One Call by Call" ativa. Ela gasta cerca de 6 consultas da cota.
- **[O] Objetivo:**
  1. Leia o CLAUDE.md, o bloco "Onde paramos" e as seções da arquitetura citadas na fatia 0
  2. Implemente as tarefas T-0.1 a T-0.8 na ordem, uma de cada vez. Antes de cada uma, explique o que vai fazer, por quê e quais alternativas existem, e espere a minha confirmação
  3. Escreva os testes primeiro e o código depois. Os testes seguem o padrão `test_<id>_<comportamento>` da seção 9.3, como o teste de configuração da T-0.3 (P-002)
  4. Antes da T-0.8, confirme que o `.env` existe, sem ler nem exibir a chave. Se ele não existir, pare e me avise. Nunca escreva a chave em código, fixtures, logs ou commits (P-001), e confira isso com `git grep`
  5. Na T-0.9, cumpra a definição de pronto da seção 9.4: rode `pytest -m "not e2e"`, `pytest -m e2e` e o ruff, confira os guardrails da seção 8.4 e verifique que a aplicação sobe com `uvicorn`
  6. Marque T-0.1 a T-0.9 com `[x]` e atualize "Onde paramos" e "Progresso" em `docs/tasks.md`, no mesmo commit do código
  7. Proponha a mensagem de commit, com o P-002 no corpo. Sugestão: `build: configurar ambiente, app mínimo e fixtures reais`. Espere a minha validação antes de commitar e antes de enviar ao GitHub
- **[S] Estilo:** Didático e organizado, uma tarefa por vez
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Para cada tarefa, apresente a decisão antes de codificar. Depois, liste os arquivos criados, os comandos executados e o resultado dos testes. No fim da fatia, mostre o checklist da definição de pronto, os IDs fechados e a mensagem de commit proposta.

## 2026-10-05 — Etapa: Arquitetura

- **[C] Contexto:**
  - Estou na T-0.8 da fatia 0, a captura das fixtures reais. As tarefas T-0.1 a T-0.7 estão concluídas e ainda sem commit.
  - Todo o projeto foi especificado para a One Call API 3.0, mas ela foi descontinuada pelo fornecedor e não aparece mais para novas assinaturas. Assinei o plano "One Call by Call" da One Call API 4.0, que é um produto separado, e minha chave recebe 401 na 3.0.
  - A arquitetura já registrava a 3.0 como descontinuada, mas a tratava como "risco aceito" sem verificar se ainda era possível assiná-la.
  - A 4.0 separa os dados em endpoints próprios (atual, por minuto, por hora, diária e detalhe de alerta). Ela também pagina as previsões, devolve os alertas como IDs e traz a chave dentro dos links `next`/`prev`.
- **[O] Objetivo:**
  1. Leia a documentação oficial da One Call API 4.0 e o guia de migração da 3.0 para a 4.0
  2. Migre o projeto para a 4.0, varrendo todas as fases afetadas pela decisão errada: spec, arquitetura, `requisitos.md`, README, CLAUDE.md, `.env.example` e `tasks.md`
  3. Registre a decisão num ADR novo, explicando o contexto, a decisão, as consequências e as alternativas descartadas. A decisão deve cobrir:
     - as chamadas por consulta de clima e a paginação;
     - a política de falha parcial;
     - a contagem de alertas;
     - o tratamento dos links com a chave;
     - o impacto na cota.
  4. Ajuste no spec as regras que dependiam do formato da 3.0, como consulta única, alertas por dia, visibilidade da previsão diária, minutos da próxima hora e limite de dias. Mantenha os IDs existentes
  5. Reescreva as tarefas afetadas em todas as fatias e registre a decisão na tabela "Decisões e limitações" do `tasks.md`, sem mudar as tarefas já concluídas
  6. Atualize o README das fixtures e o teste de guarda para as capturas da 4.0, sem guardar a chave nem os links de paginação
  7. Não abra nem altere o `.env`, nem o histórico de prompts
  8. Liste os pontos que a documentação da 4.0 não esclarece, para conferir na captura da T-0.8
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Resuma o desenho adotado para a 4.0 e o que mudou em cada documento. Destaque as mudanças no spec que dependem da minha validação e o que ficou de fora. Liste os pontos a conferir na T-0.8 e aguarde a minha confirmação antes de rodar a captura.

## 2026-10-05 — Etapa: Implementação

- **[C] Contexto:** Concluí a fatia 0 e fiz dois commits locais: `a794730` (`docs: migrar especificação e arquitetura para a One Call API 4.0`) e `880fa41` (`build: configurar ambiente, app mínimo e fixtures reais`). A branch `main` local está 2 commits à frente de `origin/main`. O CLAUDE.md exige Conventional Commits.
- **[O] Objetivo:** Envie os commits ao GitHub com `git push` e confirme a sincronização entre local e remoto.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe os hashes enviados, confirme o push e mostre o estado de sincronização.

## 2026-10-05 — Etapa: Implementação

- **[C] Contexto:** Concluí a fatia 0 e estou seguindo com a implementação do MVP. O passo a passo está nos documentos do projeto.
- **[O] Objetivo:**
  1. Leia os documentos do projeto, identifique de onde paramos e continue a partir daí.
  2. Implemente a fatia 1 inteira, sem parar para pedir confirmação a cada tarefa. Só me pergunte se surgir alguma dúvida.
- **[S] Estilo:** Didático e resumido
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** No fim da fatia, apresente o que foi feito e proponha a mensagem de commit. Aguarde a minha validação antes de commitar.

## 2026-10-05 — Etapa: Implementação

- **[C] Contexto:** Concluí a fatia 1 e fiz o commit dela localmente.
- **[O] Objetivo:** Envie os commits ao GitHub e confirme a sincronização entre local e remoto.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe os hashes enviados e confirme a sincronização.

## 2026-10-05 — Etapa: Implementação

- **[C] Contexto:** Concluí as fatias 0 e 1 e estou seguindo com a implementação do MVP. Os documentos do projeto trazem o passo a passo: onde paramos, o que construir em cada fatia e como registrar cada entrega.
- **[O] Objetivo:**
  1. Leia os documentos do projeto, identifique de onde paramos e continue a partir daí.
  2. Implemente a fatia 2 inteira, sem parar para pedir confirmação a cada tarefa. Só me pergunte se surgir alguma dúvida.
- **[S] Estilo:** Didático e resumido
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** No fim da fatia, apresente o que foi feito e proponha a mensagem de commit. Aguarde a minha validação antes de commitar.

## 2026-10-05 — Etapa: Implementação

- **[C] Contexto:** Concluí a fatia 2 e fiz o commit dela localmente.
- **[O] Objetivo:** Envie os commits ao GitHub e confirme a sincronização entre local e remoto.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe os hashes enviados e confirme a sincronização.

## 2026-10-05 — Etapa: Implementação

- **[C] Contexto:** Concluí as fatias 0, 1 e 2 e estou seguindo com a implementação do MVP. Os documentos do projeto trazem o passo a passo: onde paramos, o que construir em cada fatia e como registrar cada entrega.
- **[O] Objetivo:**
  1. Leia os documentos do projeto, identifique de onde paramos e continue a partir daí.
  2. Implemente a fatia 3 inteira, sem parar para pedir confirmação a cada tarefa. Só me pergunte se surgir alguma dúvida.
- **[S] Estilo:** Didático e resumido
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** No fim da fatia, apresente o que foi feito e proponha a mensagem de commit. Aguarde a minha validação antes de commitar.

## 2026-10-06 — Etapa: Implementação

- **[C] Contexto:** Concluí a fatia 3 e fiz o commit dela localmente.
- **[O] Objetivo:** Envie os commits ao GitHub e confirme a sincronização entre local e remoto.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe os hashes enviados e confirme a sincronização.

## 2026-10-06 — Etapa: Implementação

- **[C] Contexto:** Concluí as fatias 0 a 3 e estou seguindo com a implementação do MVP. Os documentos do projeto trazem o passo a passo: onde paramos, o que construir em cada fatia e como registrar cada entrega.
- **[O] Objetivo:**
  1. Leia os documentos do projeto, identifique de onde paramos e continue a partir daí.
  2. Implemente a fatia 4 inteira, sem parar para pedir confirmação a cada tarefa. Só me pergunte se surgir alguma dúvida.
- **[S] Estilo:** Didático e resumido
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** No fim da fatia, apresente o que foi feito e proponha a mensagem de commit. Aguarde a minha validação antes de commitar.

## 2026-10-06 — Etapa: Implementação

- **[C] Contexto:** Concluí a fatia 4 e validei a mensagem de commit proposta.
- **[O] Objetivo:** Faça o commit da fatia 4 com a mensagem `feat(api): consultar o provedor e expor as rotas /api`.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe o hash do commit e os arquivos incluídos.

## 2026-10-06 — Etapa: Implementação

- **[C] Contexto:** Concluí a fatia 4 e fiz o commit dela localmente.
- **[O] Objetivo:** Envie os commits ao GitHub e confirme a sincronização entre local e remoto.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe os hashes enviados e confirme a sincronização.

## 2026-10-06 — Etapa: Implementação

- **[C] Contexto:** Concluí as fatias 0 a 4 e estou seguindo com a implementação do MVP. Os documentos do projeto trazem o passo a passo: onde paramos, o que construir em cada fatia e como registrar cada entrega.
- **[O] Objetivo:**
  1. Leia os documentos do projeto, identifique de onde paramos e continue a partir daí.
  2. Implemente a fatia 5 inteira, sem parar para pedir confirmação a cada tarefa. Só me pergunte se surgir alguma dúvida.
- **[S] Estilo:** Didático e resumido
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** No fim da fatia, apresente o que foi feito e proponha a mensagem de commit. Aguarde a minha validação antes de commitar.

## 2026-10-06 — Etapa: Implementação

- **[C] Contexto:** Concluí a fatia 5 e validei a mensagem de commit proposta.
- **[O] Objetivo:** Faça o commit da fatia 5 com a mensagem `feat(ui): montar o esqueleto da tela com layout responsivo`.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe o hash do commit e os arquivos incluídos.

## 2026-10-06 — Etapa: Implementação

- **[C] Contexto:** Concluí a fatia 5 e fiz o commit dela localmente.
- **[O] Objetivo:** Envie os commits ao GitHub e confirme a sincronização entre local e remoto.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe os hashes enviados e confirme a sincronização.

## 2026-10-06 — Etapa: Implementação

- **[C] Contexto:** Concluí as fatias 0 a 5 e estou seguindo com a implementação do MVP. Os documentos do projeto trazem o passo a passo: onde paramos, o que construir em cada fatia e como registrar cada entrega.
- **[O] Objetivo:**
  1. Leia os documentos do projeto, identifique de onde paramos e continue a partir daí.
  2. Implemente a fatia 6a inteira, sem parar para pedir confirmação a cada tarefa. Só me pergunte se surgir alguma dúvida.
- **[S] Estilo:** Didático e resumido
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** No fim da fatia, apresente o que foi feito e proponha a mensagem de commit. Aguarde a minha validação antes de commitar.

## 2026-10-06 — Etapa: Implementação

- **[C] Contexto:** Concluí a fatia 6a e validei a mensagem de commit proposta.
- **[O] Objetivo:** Faça o commit da fatia 6a com a mensagem `feat(ui): carregar o clima com cache e estados de carregamento e erro`.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe o hash do commit e os arquivos incluídos.

## 2026-10-06 — Etapa: Implementação

- **[C] Contexto:** Concluí a fatia 6a e fiz o commit dela localmente.
- **[O] Objetivo:** Envie os commits ao GitHub e confirme a sincronização entre local e remoto.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe os hashes enviados e confirme a sincronização.

## 2026-10-06 — Etapa: Implementação

- **[C] Contexto:** Concluí as fatias 0 a 6a e estou seguindo com a implementação do MVP. Os documentos do projeto trazem o passo a passo: onde paramos, o que construir em cada fatia e como registrar cada entrega.
- **[O] Objetivo:**
  1. Leia os documentos do projeto, identifique de onde paramos e continue a partir daí.
  2. Implemente a fatia 6b inteira, sem parar para pedir confirmação a cada tarefa. Só me pergunte se surgir alguma dúvida.
- **[S] Estilo:** Didático e resumido
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** No fim da fatia, apresente o que foi feito e proponha a mensagem de commit. Aguarde a minha validação antes de commitar.

## 2026-10-06 — Etapa: Implementação

- **[C] Contexto:** Concluí a fatia 6b e validei a mensagem de commit proposta.
- **[O] Objetivo:** Faça o commit da fatia 6b com a mensagem `feat(ui): buscar cidades e alternar a escala no cabeçalho`.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe o hash do commit e os arquivos incluídos.

## 2026-10-06 — Etapa: Implementação

- **[C] Contexto:** Concluí a fatia 6b e fiz o commit dela localmente.
- **[O] Objetivo:** Envie os commits ao GitHub e confirme a sincronização entre local e remoto.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe os hashes enviados e confirme a sincronização.

## 2026-10-06 — Etapa: Implementação

- **[C] Contexto:** Concluí as fatias 0 a 6b e estou seguindo com a implementação do MVP. Os documentos do projeto trazem o passo a passo: onde paramos, o que construir em cada fatia e como registrar cada entrega.
- **[O] Objetivo:**
  1. Leia os documentos do projeto, identifique de onde paramos e continue a partir daí.
  2. Implemente a fatia 6c inteira, sem parar para pedir confirmação a cada tarefa. Só me pergunte se surgir alguma dúvida.
- **[S] Estilo:** Didático e resumido
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** No fim da fatia, apresente o que foi feito e proponha a mensagem de commit. Aguarde a minha validação antes de commitar.

## 2026-10-06 — Etapa: Implementação

- **[C] Contexto:** Concluí a fatia 6c e validei a mensagem de commit proposta.
- **[O] Objetivo:** Faça o commit da fatia 6c com a mensagem `feat(ui): iniciar pela localização do usuário ou pela cidade padrão`.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe o hash do commit e os arquivos incluídos.

## 2026-10-06 — Etapa: Implementação

- **[C] Contexto:** Concluí a fatia 6c e fiz o commit dela localmente.
- **[O] Objetivo:** Envie os commits ao GitHub e confirme a sincronização entre local e remoto.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe os hashes enviados e confirme a sincronização.

## 2026-10-06 — Etapa: Implementação

- **[C] Contexto:** Concluí as fatias 0 a 6c e estou seguindo com a implementação do MVP. Os documentos do projeto trazem o passo a passo: onde paramos, o que construir em cada fatia e como registrar cada entrega.
- **[O] Objetivo:**
  1. Leia os documentos do projeto, identifique de onde paramos e continue a partir daí.
  2. Implemente a fatia 7 inteira, sem parar para pedir confirmação a cada tarefa. Só me pergunte se surgir alguma dúvida.
- **[S] Estilo:** Didático e resumido
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** No fim da fatia, apresente o que foi feito e proponha a mensagem de commit. Aguarde a minha validação antes de commitar.

## 2026-10-06 — Etapa: Implementação

- **[C] Contexto:** Concluí a fatia 7 e validei a mensagem de commit proposta.
- **[O] Objetivo:** Faça o commit da fatia 7 com a mensagem `feat(ui): exibir as condições atuais com ilustrações e indicadores`.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe o hash do commit e os arquivos incluídos.

## 2026-10-06 — Etapa: Implementação

- **[C] Contexto:** Concluí a fatia 7 e fiz o commit dela localmente.
- **[O] Objetivo:** Envie os commits ao GitHub e confirme a sincronização entre local e remoto.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe os hashes enviados e confirme a sincronização.

## 2026-10-06 — Etapa: Implementação

- **[C] Contexto:** Concluí as fatias 0 a 7 e estou seguindo com a implementação do MVP. Os documentos do projeto trazem o passo a passo: onde paramos, o que construir em cada fatia e como registrar cada entrega.
- **[O] Objetivo:**
  1. Leia os documentos do projeto, identifique de onde paramos e continue a partir daí.
  2. Implemente a fatia 8 inteira, sem parar para pedir confirmação a cada tarefa. Só me pergunte se surgir alguma dúvida.
- **[S] Estilo:** Didático e resumido
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** No fim da fatia, apresente o que foi feito e proponha a mensagem de commit. Aguarde a minha validação antes de commitar.

## 2026-10-06 — Etapa: Implementação

- **[C] Contexto:** Concluí a fatia 8 e validei a mensagem de commit proposta.
- **[O] Objetivo:** Faça o commit da fatia 8 com a mensagem `feat(ui): exibir a previsão diária em abas com o resumo de cada dia`.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe o hash do commit e os arquivos incluídos.

## 2026-10-06 — Etapa: Implementação

- **[C] Contexto:** Concluí a fatia 8 e fiz o commit dela localmente.
- **[O] Objetivo:** Envie os commits ao GitHub e confirme a sincronização entre local e remoto.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe os hashes enviados e confirme a sincronização.

## 2026-10-06 — Etapa: Implementação

- **[C] Contexto:** Concluí as fatias 0 a 8 e estou seguindo com a implementação do MVP. Os documentos do projeto trazem o passo a passo: onde paramos, o que construir em cada fatia e como registrar cada entrega.
- **[O] Objetivo:**
  1. Leia os documentos do projeto, identifique de onde paramos e continue a partir daí.
  2. Implemente a fatia 9 inteira, sem parar para pedir confirmação a cada tarefa. Só me pergunte se surgir alguma dúvida.
- **[S] Estilo:** Didático e resumido
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** No fim da fatia, apresente o que foi feito e proponha a mensagem de commit. Aguarde a minha validação antes de commitar.

## 2026-10-06 — Etapa: Implementação

- **[C] Contexto:** Concluí a fatia 9 e validei a mensagem de commit proposta.
- **[O] Objetivo:** Faça o commit da fatia 9 com a mensagem `feat(ui): exibir a previsão hora a hora com curva, etiquetas e cards`.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe o hash do commit e os arquivos incluídos.

## 2026-10-06 — Etapa: Implementação

- **[C] Contexto:** Concluí a fatia 9 e fiz o commit dela localmente.
- **[O] Objetivo:** Envie os commits ao GitHub e confirme a sincronização entre local e remoto.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe os hashes enviados e confirme a sincronização.

## 2026-10-06 — Etapa: Implementação

- **[C] Contexto:** Concluí as fatias 0 a 9 e estou seguindo com a implementação do MVP. Os documentos do projeto trazem o passo a passo: onde paramos, o que construir em cada fatia e como registrar cada entrega.
- **[O] Objetivo:**
  1. Leia os documentos do projeto, identifique de onde paramos e continue a partir daí.
  2. Implemente a fatia 10 inteira, sem parar para pedir confirmação a cada tarefa. Só me pergunte se surgir alguma dúvida.
- **[S] Estilo:** Didático e resumido
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** No fim da fatia, apresente o que foi feito e proponha a mensagem de commit. Aguarde a minha validação antes de commitar.

## 2026-10-06 — Etapa: Implementação

- **[C] Contexto:** Concluí a fatia 10 e validei a mensagem de commit proposta.
- **[O] Objetivo:** Faça o commit da fatia 10 com a mensagem `feat(ui): exibir a previsão por minuto com barras, marcos e resumo`.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe o hash do commit e os arquivos incluídos.

## 2026-10-06 — Etapa: Implementação

- **[C] Contexto:** Concluí a fatia 10 e fiz o commit dela localmente.
- **[O] Objetivo:** Envie os commits ao GitHub e confirme a sincronização entre local e remoto.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe os hashes enviados e confirme a sincronização.

## 2026-10-06 — Etapa: Implementação

- **[C] Contexto:** Concluí as fatias 0 a 10 e estou seguindo com a implementação do MVP. Os documentos do projeto trazem o passo a passo: onde paramos, o que construir em cada fatia e como registrar cada entrega.
- **[O] Objetivo:**
  1. Leia os documentos do projeto, identifique de onde paramos e continue a partir daí.
  2. Implemente a fatia 11 inteira, sem parar para pedir confirmação a cada tarefa. Só me pergunte se surgir alguma dúvida.
- **[S] Estilo:** Didático e resumido
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** No fim da fatia, apresente o que foi feito e proponha a mensagem de commit. Aguarde a minha validação antes de commitar.

## 2026-10-06 — Etapa: Implementação

- **[C] Contexto:** Concluí a fatia 11 e validei a mensagem de commit proposta.
- **[O] Objetivo:** Faça o commit da fatia 11 com a mensagem `feat(ui): exibir o mapa de precipitação com marcador e camada de chuva`.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe o hash do commit e os arquivos incluídos.

## 2026-10-06 — Etapa: Implementação

- **[C] Contexto:** Concluí a fatia 11 e fiz o commit dela localmente.
- **[O] Objetivo:** Envie os commits ao GitHub e confirme a sincronização entre local e remoto.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe os hashes enviados e confirme a sincronização.

## 2026-10-06 — Etapa: Implementação

- **[C] Contexto:** Concluí as fatias 0 a 11 e estou seguindo com a implementação do MVP. Os documentos do projeto trazem o passo a passo: onde paramos, o que construir em cada fatia e como registrar cada entrega.
- **[O] Objetivo:**
  1. Leia os documentos do projeto, identifique de onde paramos e continue a partir daí.
  2. Implemente a fatia 12 inteira, sem parar para pedir confirmação a cada tarefa. Só me pergunte se surgir alguma dúvida.
- **[S] Estilo:** Didático e resumido
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** No fim da fatia, apresente o que foi feito e proponha a mensagem de commit. Aguarde a minha validação antes de commitar.

## 2026-10-06 — Etapa: Implementação

- **[C] Contexto:** Concluí a fatia 12 e validei a mensagem de commit proposta.
- **[O] Objetivo:** Faça o commit da fatia 12 com a mensagem `feat(ui): atualizar dados ao voltar à página e acompanhar o relógio`.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe o hash do commit e os arquivos incluídos.

## 2026-10-06 — Etapa: Implementação

- **[C] Contexto:** Concluí a fatia 12 e fiz o commit dela localmente.
- **[O] Objetivo:** Envie os commits ao GitHub e confirme a sincronização entre local e remoto.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe os hashes enviados e confirme a sincronização.

## 2026-10-06 — Etapa: Implementação

- **[C] Contexto:** Concluí as fatias 0 a 12 e estou seguindo com a implementação do MVP. Os documentos do projeto trazem o passo a passo: onde paramos, o que construir em cada fatia e como registrar cada entrega.
- **[O] Objetivo:**
  1. Leia os documentos do projeto, identifique de onde paramos e continue a partir daí.
  2. Implemente a fatia 13 inteira, sem parar para pedir confirmação a cada tarefa. Só me pergunte se surgir alguma dúvida.
- **[S] Estilo:** Didático e resumido
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** No fim da fatia, apresente o que foi feito e proponha a mensagem de commit. Aguarde a minha validação antes de commitar.

## 2026-10-06 — Etapa: Implementação

- **[C] Contexto:** Concluí a fatia 13 e validei a mensagem de commit proposta.
- **[O] Objetivo:** Faça o commit da fatia 13 com a mensagem `chore(release): fechar o MVP com rastreabilidade e versão 0.1.0`.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe o hash do commit e os arquivos incluídos.

## 2026-10-06 — Etapa: Implementação

- **[C] Contexto:** Concluí a fatia 13 e fiz o commit dela localmente.
- **[O] Objetivo:** Envie os commits ao GitHub e confirme a sincronização entre local e remoto.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe os hashes enviados e confirme a sincronização.

## 2026-10-07 — Etapa: Testes

- **[C] Contexto:** Concluí a implementação do MVP e publiquei a versão v0.1.0. Estou começando a etapa de Testes do SDLC, com foco em aprender o uso da IA nela, sem testes manuais e aceitando as limitações do projeto, como testar só no Chrome.
- **[O] Objetivo:**
  1. Crie um plano de testes nos documentos do projeto, com o objetivo, o escopo, o ponto de partida dos testes que já existem, as fases da etapa (cobertura, revisão dos testes, testes exploratórios, mutação, registro de defeitos e relatório final), os critérios de entrada e saída, as limitações aceitas e um bloco de onde paramos.
  2. Detalhe em cada fase como os testes já construídos são usados.
  3. Referencie o plano nos demais documentos do projeto.
- **[S] Estilo:** Didático e resumido
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Apresente o plano criado e proponha a mensagem de commit. Aguarde a minha validação antes de commitar.

## 2026-10-07 — Etapa: Testes

- **[C] Contexto:** Criei o plano de testes e fiz o commit dele localmente.
- **[O] Objetivo:** Envie os commits ao GitHub e confirme a sincronização entre local e remoto.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe os hashes enviados e confirme a sincronização.

## 2026-10-07 — Etapa: Testes

- **[C] Contexto:** Criei o plano de testes e estou começando a executá-lo. O plano traz o passo a passo: onde paramos, as fases da etapa e como registrar cada entrega.
- **[O] Objetivo:**
  1. Leia os documentos do projeto, identifique de onde paramos e entenda o que precisa ser feito na próxima fase.
  2. Resuma para mim o que será feito e aguarde o meu retorno antes de começar.
  3. Execute a fase inteira.
- **[S] Estilo:** Didático e resumido
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Mostre os resultados de maneira simples e didática, com um parecer sobre o sucesso ou não da fase. Proponha a mensagem de commit e aguarde a minha validação antes de commitar.

## 2026-10-07 — Etapa: Testes

- **[C] Contexto:** Concluí a fase 1 do plano de testes e quero acompanhar de forma didática o que cada fase entrega.
- **[O] Objetivo:**
  1. Crie um documento de resultados da etapa de Testes e registre nele o resultado da fase 1, no mesmo formato da apresentação que você me fez: o que foi feito, os números de antes e depois, o que se aprendeu, as verificações e um parecer sobre a fase.
  2. Faça desse documento parte da rotina: ao fim de cada fase, acrescente a seção dela.
- **[S] Estilo:** Didático e resumido
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe onde o documento ficou e como ele entra na rotina das fases.

## 2026-10-07 — Etapa: Testes

- **[C] Contexto:** Concluí a fase 1 do plano de testes e registrei o resultado dela no relatório de testes.
- **[O] Objetivo:** Faça o commit da fase 1 com a mensagem `test(testes): medir a cobertura e fechar as lacunas da fase 1`.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe o hash do commit e os arquivos incluídos.

## 2026-10-07 — Etapa: Testes

- **[C] Contexto:** Concluí a fase 1 do plano de testes e fiz o commit dela localmente.
- **[O] Objetivo:** Envie os commits ao GitHub e confirme a sincronização entre local e remoto.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe os hashes enviados e confirme a sincronização.

## 2026-10-07 — Etapa: Testes

- **[C] Contexto:** Concluí a fase 1 do plano de testes e estou seguindo com a etapa de Testes. O plano traz o passo a passo: onde paramos, as fases da etapa e como registrar cada entrega.
- **[O] Objetivo:**
  1. Leia os documentos do projeto, identifique de onde paramos e entenda o que precisa ser feito na próxima fase.
  2. Execute a fase inteira, sem parar para pedir confirmação a cada tarefa. Só me pergunte se surgir alguma dúvida.
- **[S] Estilo:** Didático e resumido
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Apresente o resumo da fase de maneira simples e didática, com um parecer sobre o sucesso ou não da fase.

## 2026-10-07 — Etapa: Testes

- **[C] Contexto:** Concluí a fase 2 do plano de testes e registrei o resultado dela no relatório de testes.
- **[O] Objetivo:** Faça o commit da fase 2 com a mensagem `test(testes): revisar os testes com a IA e corrigir os achados da fase 2`.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe o hash do commit e os arquivos incluídos.

## 2026-10-07 — Etapa: Testes

- **[C] Contexto:** Concluí a fase 2 do plano de testes e fiz o commit dela localmente.
- **[O] Objetivo:** Envie os commits ao GitHub e confirme a sincronização entre local e remoto.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe os hashes enviados e confirme a sincronização.

## 2026-10-08 — Etapa: Testes

- **[C] Contexto:** Concluí a fase 2 do plano de testes. As fases 3 e 4, como estão no plano, consomem muitos tokens e muito tempo, e decidi simplificá-las: o custo de tokens e de tempo num MVP acadêmico, em que o objetivo é aprender a técnica e não esgotá-la, não compensa a execução completa.
- **[O] Objetivo:**
  1. Leia os documentos do projeto, identifique de onde paramos e entenda o que precisa ser feito na próxima fase.
  2. Reduza a fase 3 a um único cenário exploratório, o de fuso horário exótico, e a fase 4 a um único módulo. Registre a decisão no plano, com essa justificativa, e explique no relatório o que ficou de fora e por quê.
  3. Execute a fase 3 inteira, sem parar para pedir confirmação a cada tarefa. Só me pergunte se surgir alguma dúvida.
- **[S] Estilo:** Didático e resumido
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Apresente o resumo da fase de maneira simples e didática, com um parecer sobre o sucesso ou não da fase.

## 2026-10-08 — Etapa: Testes

- **[C] Contexto:** Concluí a fase 3 do plano de testes, com o escopo reduzido ao cenário de fuso horário exótico, e registrei o resultado dela no relatório de testes.
- **[O] Objetivo:** Faça o commit da fase 3 com a mensagem `fix(testes): explorar fusos exóticos e corrigir a hora no fuso +05:45`.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe o hash do commit e os arquivos incluídos.

## 2026-10-08 — Etapa: Testes

- **[C] Contexto:** Concluí a fase 3 do plano de testes e fiz o commit dela localmente.
- **[O] Objetivo:** Envie os commits ao GitHub e confirme a sincronização entre local e remoto.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe os hashes enviados e confirme a sincronização.

## 2026-10-08 — Etapa: Testes

- **[C] Contexto:** Concluí a fase 3 do plano de testes, com o escopo reduzido. A fase 4 também foi reduzida a um único módulo, pelo custo de tokens e de tempo num MVP acadêmico.
- **[O] Objetivo:**
  1. Leia os documentos do projeto, identifique de onde paramos e entenda o que precisa ser feito na próxima fase.
  2. Execute a fase 4 inteira, sem parar para pedir confirmação a cada tarefa. Só me pergunte se surgir alguma dúvida.
- **[S] Estilo:** Didático e resumido
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Apresente o resumo da fase de maneira simples e didática, com um parecer sobre o sucesso ou não da fase.

## 2026-10-08 — Etapa: Testes

- **[C] Contexto:** Concluí a fase 4 do plano de testes, com o escopo reduzido a um único módulo, e registrei o resultado dela no relatório de testes.
- **[O] Objetivo:** Faça o commit da fase 4 com a mensagem `test(testes): medir a mutação do módulo de precipitação na fase 4`.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe o hash do commit e os arquivos incluídos.

## 2026-10-08 — Etapa: Testes

- **[C] Contexto:** Concluí a fase 4 do plano de testes e fiz o commit dela localmente.
- **[O] Objetivo:** Envie os commits ao GitHub e confirme a sincronização entre local e remoto.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe os hashes enviados e confirme a sincronização.

## 2026-10-08 — Etapa: Testes

- **[C] Contexto:** Concluí as fases 1 a 4 do plano de testes, com as fases 3 e 4 em escopo reduzido, e a fase 3 corrigiu um defeito do produto. Falta a fase 6, o relatório final.
- **[O] Objetivo:**
  1. Leia os documentos do projeto, identifique de onde paramos e entenda o que precisa ser feito na fase 6.
  2. Execute a fase 6 inteira, sem parar para pedir confirmação a cada tarefa. Rode uma vez a fumaça com o provedor real e meça de novo a cobertura, para o relatório trazer os números finais.
  3. Publique a versão v0.1.1, com a tag enviada ao GitHub.
- **[S] Estilo:** Didático e resumido
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Apresente o resumo da etapa de Testes de maneira simples e didática, com um parecer final sobre ela.

## 2026-10-08 — Etapa: Testes

- **[C] Contexto:** Concluí a fase 6 do plano de testes, que fecha a etapa de Testes, e registrei o resultado final no relatório de testes.
- **[O] Objetivo:** Faça o commit da fase 6 com a mensagem `docs(testes): consolidar o relatório final e publicar a versão 0.1.1` e crie nele a tag `v0.1.1`.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe o hash do commit, os arquivos incluídos e a tag criada.

## 2026-10-08 — Etapa: Testes

- **[C] Contexto:** Concluí a fase 6 do plano de testes, fiz o commit dela localmente e criei a tag `v0.1.1`.
- **[O] Objetivo:** Envie os commits e a tag `v0.1.1` ao GitHub e confirme a sincronização entre local e remoto.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe os hashes e a tag enviados e confirme a sincronização.

## 2026-10-08 — Etapa: Documentação

- **[C] Contexto:** Concluí a etapa de Testes e agora quero confirmar que a documentação do código segue estes critérios: docstring em funções e classes públicas, comentários apenas em trechos não óbvios, contratos de entrada e saída explícitos e mensagens de erro claras.
- **[O] Objetivo:**
  1. Revise o código do backend e do frontend com esses critérios e aponte as lacunas.
  2. Corrija as lacunas só na documentação do código, sem mudar o comportamento.
  3. Proponha a mensagem de commit e aguarde minha validação antes de commitar.
- **[S] Estilo:** Didático e resumido
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Apresente uma tabela com a situação de cada critério e liste o que foi corrigido.

## 2026-10-08 — Etapa: Documentação

- **[C] Contexto:** Concluí a revisão da documentação do código e fiz o commit dela localmente.
- **[O] Objetivo:** Envie os commits ao GitHub e confirme a sincronização entre local e remoto.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe os hashes enviados e confirme a sincronização.

## 2026-10-08 — Etapa: Documentação

- **[C] Contexto:** Estou fechando a documentação do projeto e quero que o README contemple, no mínimo: o que o projeto resolve, como instalar e executar, como rodar testes, quais limites existem e como a IA foi usada no processo.
- **[O] Objetivo:**
  1. Revise o README com esses itens e complete o que faltar.
  2. Na parte de IA, responda:
     - onde a IA acelerou o desenvolvimento, em todo o ciclo do SDLC;
     - onde a revisão humana foi decisiva: ao final de cada etapa, eu revisei a sua saída e os artefatos gerados;
     - quais prompts foram usados, apontando para o registro;
     - quais riscos foram mitigados, com um argumento que inclua a amplitude dos testes.
  3. Proponha a mensagem de commit e aguarde minha validação antes de commitar.
- **[S] Estilo:** Didático e resumido
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Apresente uma tabela com a situação de cada item antes e depois e um resumo do que mudou no README.

## 2026-10-08 — Etapa: Documentação

- **[C] Contexto:** Concluí a revisão do README e fiz o commit dela localmente.
- **[O] Objetivo:** Envie os commits ao GitHub e confirme a sincronização entre local e remoto.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe os hashes enviados e confirme a sincronização.

## 2026-10-08 — Etapa: Documentação

- **[C] Contexto:** Avaliei a reprodutibilidade do projeto numa máquina limpa e ainda não fiz esse teste. Quero que o README deixe claras as limitações dessa verificação.
- **[O] Objetivo:**
  1. Adicione ao README uma seção sobre as limitações dos testes de reprodutibilidade: o que o repositório garante, o que não foi verificado e como reduzir cada risco.
  2. Proponha a mensagem de commit e aguarde minha validação antes de commitar.
- **[S] Estilo:** Didático e resumido
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Mostre onde a seção entrou e resuma o que ela diz.

## 2026-10-08 — Etapa: Documentação

- **[C] Contexto:** Adicionei ao README as limitações de reprodutibilidade e fiz o commit localmente.
- **[O] Objetivo:** Envie os commits ao GitHub e confirme a sincronização entre local e remoto.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Informe os hashes enviados e confirme a sincronização.
