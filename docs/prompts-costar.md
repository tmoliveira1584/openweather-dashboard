# Prompts CO-STAR

## 2026-09-29 — Etapa: Setup

- **[C] Contexto:** Estou iniciando do zero um MVP para a pós-graduação: uma aplicação web frontend que consome a API do OpenWeatherMap e exibe temperatura, umidade e previsão por cidade, com campo de busca. A pasta openweather-dashboard ainda está vazia. A stack ainda será definida na etapa de arquitetura.
- **[O] Objetivo:** Preparar a estrutura inicial do projeto, sem escrever código da aplicação:
  1. git init e um .gitignore que inclua .env e node_modules
  2. CLAUDE.md curto com descrição, regras (API key só via .env, explicar decisões antes de implementar, passos pequenos) e stack "a definir"
  3. Pasta docs/ com requisitos.md, arquitetura.md e prompts-costar.md vazios, só com título
  4. Comando .claude/commands/costar.md que reescreve meu pedido em CO-STAR, registra em docs/prompts-costar.md com data e etapa do SDLC, e depois executa
  5. Registre este prompt como a primeira entrada de docs/prompts-costar.md (etapa: Setup)
- **[S] Estilo:** Didático e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Liste os arquivos criados e explique em uma frase a função de cada um. Peça minha confirmação antes de criar os arquivos.

## 2026-09-29 — Etapa: Setup

- **[C] Contexto:** Estrutura inicial do MVP criada (git init, .gitignore, CLAUDE.md, docs/ e comando /costar), ainda sem nenhum commit. O CLAUDE.md não define um padrão para mensagens de commit.
- **[O] Objetivo:** Acrescentar ao CLAUDE.md uma instrução para que todo commit siga Conventional Commits e, quando não for possível definir as variáveis da mensagem (tipo, escopo, breaking change), o assistente peça validação do usuário antes de commitar.
- **[S] Estilo:** Didático e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Resumo curto da regra adicionada e sugestão de mensagem para o primeiro commit.

## 2026-09-29 — Etapa: Setup

- **[C] Contexto:** MVP da pós-graduação em fase de setup. Já existem Git, .gitignore, CLAUDE.md (com Conventional Commits), docs/ e o comando /costar. Stack, licença e autoria ainda não foram definidas, e não há código da aplicação.
- **[O] Objetivo:** Criar um README.md com base no que já foi definido, marcando o que ainda não foi decidido, contendo no mínimo:
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
- **[R] Resposta:** Arquivo README.md criado na raiz e resumo do conteúdo de cada seção, com as pendências a preencher.

## 2026-09-29 — Etapa: Setup

- **[C] Contexto:** Estrutura inicial do MVP pronta (.gitignore, CLAUDE.md, README.md, docs/ e comando /costar), ainda sem nenhum commit. O CLAUDE.md exige Conventional Commits e o Git local não tem autor configurado.
- **[O] Objetivo:**
  1. Configurar o autor do Git somente neste repositório (Thiago Martins de Oliveira, oliveira.thiago@discente.ufg.br)
  2. Fazer o primeiro commit com todos os arquivos, usando a descrição "criação da estrutura inicial do projeto" adaptada ao padrão Conventional Commits
  3. Pedir validação do usuário para a mensagem, já que a descrição original não tem tipo nem está no imperativo
- **[S] Estilo:** Didático e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Mensagem de commit validada (`chore: criar estrutura inicial do projeto`), hash do commit e autor registrado.

## 2026-09-29 — Etapa: Setup

- **[C] Contexto:** O primeiro commit existe localmente na branch `master`. O repositório remoto https://github.com/tmoliveira1584/openweather-dashboard foi criado vazio no GitHub.
- **[O] Objetivo:**
  1. Verificar se o repositório remoto está vazio, para evitar conflito de histórico
  2. Renomear a branch principal de `master` para `main` (padrão do GitHub), após validação do usuário
  3. Adicionar o remoto `origin` e enviar a branch `main`, deixando-a ligada a `origin/main`
- **[S] Estilo:** Didático e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Confirmação do push, branch padrão no GitHub e estado de sincronização entre local e remoto.

## 2026-09-30 — Etapa: Setup

- **[C] Contexto:** O commit `0caa502` (registro dos prompts do primeiro commit e da sincronização) foi feito localmente e a branch `main` está um commit à frente de `origin/main`.
- **[O] Objetivo:** Enviar o commit ao GitHub com `git push` e confirmar que local e remoto ficaram sincronizados.
- **[S] Estilo:** Didático e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Confirmação do push e do estado de sincronização, com as pendências que ainda estão em aberto.

## 2026-09-30 — Etapa: Setup

- **[C] Contexto:** O repositório remoto já existe no GitHub, mas o passo "Clonar o repositório" do README ainda mostra `<url-do-repositorio>` marcado como "⚠️ A definir".
- **[O] Objetivo:** Trocar o marcador do comando `git clone` no README pelo endereço real https://github.com/tmoliveira1584/openweather-dashboard.git e remover o aviso de pendência.
- **[S] Estilo:** Didático e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Confirmação da alteração no README.

## 2026-09-30 — Etapa: Setup

- **[C] Contexto:** Há alterações locais no README (endereço do repositório) e em docs/prompts-costar.md (novos registros). O CLAUDE.md exige Conventional Commits. Ficou decidido manter `.claude/commands/` versionado.
- **[O] Objetivo:**
  1. Fazer um commit com as alterações do README e de docs/prompts-costar.md, seguindo Conventional Commits
  2. Enviar o commit ao GitHub com `git push`
- **[S] Estilo:** Didático e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Mensagem e hash do commit, confirmação do push e estado de sincronização entre local e remoto.

## 2026-10-03 — Etapa: Requisitos

- **[C] Contexto:** MVP acadêmico em fase de requisitos. É uma página única que reproduz o layout de um print de referência e consome a OpenWeatherMap One Call API 3.0 (clima atual, previsão por minuto, por hora, por dia e alertas), a Geocoding API (busca direta e reversa), o serviço de ícones e a camada de precipitação do mapa. A 3.0 foi escolhida em vez da 4.0 por simplicidade: uma única chamada por cidade, sem paginação e com melhor aproveitamento da cota gratuita. O fornecedor recomenda a 4.0 para novas integrações, o que fica registrado como risco. A cidade inicial vem da localização do navegador; se a permissão for negada, o recurso não existir ou não houver resposta em 10 s, usa Uberlândia (lat -18.9186, lon -48.2772) e mostra um aviso. Interface toda em pt-BR, com horário em 24h. Mapeamento tela → dados: header (título, alternância °C/°F, cidade atual, busca); abas Today + 7 dias, como a API entrega (`daily[].temp.max`, ícone); card principal (`current.temp`, descrição, `feels_like`, `dt`, contagem de `alerts`, imagem por grupo de condição); 6 cards (vento com direção em rosa de 8 pontos, umidade, visibilidade, pressão, índice UV, ponto de orvalho); previsão por hora (curva de temperatura das próximas 24 h, cards com ícone, `pop` e temperatura, etiquetas de `rain.1h`); previsão por minuto (barras de `minutely[].precipitation` com marcos Agora, +15, +30, +45 e +60 min e legenda de 5 faixas); mapa com marcador da cidade, camada de chuva e mapa base com atribuição. Regras gerais: horário local da cidade; visibilidade em km; °C/°F convertido localmente, sem nova chamada, com o vento acompanhando (m/s ↔ mph); no máximo uma chamada por cidade a cada 10 min (cache em memória); aba Today mostra `current` e as demais mostram o resumo de `daily` (máxima/mínima, descrição, sensação, data; visibilidade "—"), enquanto as previsões por hora e por minuto continuam no momento atual; cores das barras de precipitação: 0 cinza, (0; 0,5] verde, (0,5; 2,5] verde-escuro, (2,5; 7,5] amarelo, > 7,5 vermelho. O badge de alertas mostra só a contagem. A stack será definida na etapa de arquitetura. Hoje `docs/requisitos.md` contém só o título.
- **[O] Objetivo:**
  1. Criar `docs/product-brief.md` com: explicação do produto, razão de existir, atores, diagrama Mermaid do fluxo de uso, glossário geral e disclaimer de finalidade didática.
  2. Criar `docs/constitution.md` com princípios permanentes e transversais (P-001, P-002…), cada um em uma linha, no imperativo, no formato SEMPRE/NUNCA e sem justificativa longa.
  3. Criar `docs/spec.md` com uma seção por feature, sem código de feature: Localização inicial e busca de cidade; Condições atuais; Previsão diária; Previsão hora a hora; Previsão por minuto; Mapa de precipitação; Alternância de unidades. Cada feature contém: Problema; Atores (Ator, Descrição, O que pode fazer, O que não pode fazer); Escopo (incluso / não incluso); Histórias de usuário ("Como <ator>, quero <ação>, para <resultado>"); Requisitos funcionais em notação EARS; Regras de negócio (a lógica por trás dos RFs); Comportamento em erro e casos de borda (Cenário, Comportamento esperado, Mensagem ao usuário); Requisitos não-funcionais (ID, Categoria, Requisito); Dependências e premissas; Critérios de aceite em Given/When/Then (3 a 8 por feature); Glossário específico. RF, RN, RNF e CA numerados em sequência no documento inteiro.
  4. Montar a tabela de erros com um roteiro próprio do produto (só leitura, sem login, dependente de API externa): entrada inválida; localização do navegador; credencial e cota; serviço externo indisponível, lento ou sem conexão; resposta incompleta; valores-limite; ações repetidas e concorrentes; cache e tempo; recursos visuais; volume e tela. Não encaixar à força cenários que não se aplicam.
  5. Não incluir nenhum detalhe de stack tecnológica.
  6. Transformar `docs/requisitos.md` em índice dos três artefatos.
  7. Varrer todo o diretório do projeto (CLAUDE.md, README, docs/, .claude/, .gitignore) e atualizar o que deixar de ser verdade com estas decisões.
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Os três artefatos em Markdown, o índice em `docs/requisitos.md`, a lista de arquivos alterados na varredura com o motivo de cada mudança e um resumo de quantidades (features, RF, RN, RNF, CA, princípios).

## 2026-10-04 — Etapa: Requisitos

- **[C] Contexto:** A etapa de requisitos foi concluída. Os artefatos novos (`docs/product-brief.md`, `docs/constitution.md` e `docs/spec.md`, com glossário consolidado) e as alterações em `docs/requisitos.md` (agora índice), CLAUDE.md, README e `docs/prompts-costar.md` ainda não foram commitados. A branch `main` local está sincronizada com `origin/main` (https://github.com/tmoliveira1584/openweather-dashboard). O CLAUDE.md exige Conventional Commits.
- **[O] Objetivo:**
  1. Propor a mensagem de commit seguindo Conventional Commits e aguardar a validação do usuário antes de commitar
  2. Depois da validação, fazer um único commit com todas as alterações da etapa de requisitos
  3. Enviar o commit ao GitHub com `git push` e confirmar a sincronização entre local e remoto
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Mensagem de commit proposta para validação; depois de aprovada, hash do commit, confirmação do push e estado de sincronização.

## 2026-10-04 — Etapa: Arquitetura

- **[C] Contexto:** A etapa de requisitos foi concluída e commitada (`a63e0c3`): product brief, constitution (P-001 a P-027) e spec com 7 features (RF-001 a RF-058, RN-001 a RN-059, RNF-001 a RNF-029, CA-001 a CA-044). `docs/arquitetura.md` tem só o título, e o provedor de mapa base continua pendente. O autor não tem experiência com arquitetura de software: o foco é aprender a usar IA no SDLC, não se tornar arquiteto. A aplicação vai rodar só localmente, sem instalar nenhum software novo. O ambiente já tem Node.js 22 com npm 10, Git, VS Code e Google Chrome. O Python não está instalado.
- **[O] Objetivo:**
  1. Propor uma arquitetura eficiente, simples de entender e de implementar, que rode localmente apenas com o que já está instalado
  2. Explicar brevemente cada componente, por que foi escolhido e quais alternativas foram descartadas
  3. Garantir que a proposta cubra todo o escopo dos documentos (7 features do spec e princípios da constitution), com uma matriz de cobertura
  4. Definir o provedor de mapa base
  5. Registrar este prompt em `docs/prompts-costar.md`
  6. Não escrever ainda o `docs/arquitetura.md`
- **[S] Estilo:** Didático e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Proposta de arquitetura na conversa: visão geral em diagrama, componentes com função e justificativa, alternativas descartadas, estrutura de pastas, estratégia de testes, matriz de cobertura do escopo, riscos e pontos para o usuário validar antes de registrar em `docs/arquitetura.md`.

## 2026-10-04 — Etapa: Arquitetura

- **[C] Contexto:** A arquitetura foi discutida e fechada na conversa. Backend em Python 3.13 (ambiente conda do Anaconda já instalado) com FastAPI, Uvicorn, httpx e python-dotenv, no padrão BFF: proxy com a chave só no servidor, regras de negócio e textos prontos nas duas escalas. Frontend em HTML, CSS e JavaScript puro, sem build, com Leaflet 1.9.4 copiado para o projeto, mapa base CARTO Voyager e gráficos em SVG próprio. Cache no navegador (P-007). Testes com pytest e pytest-playwright usando o Chrome instalado. Identificadores em inglês, interface e comentários em pt-BR. O print `docs/referencia/referencia_visual.png` é referência visual, e o spec prevalece em textos e formatos. Hoje `docs/arquitetura.md` tem só o título, e o README e o CLAUDE.md ainda mostram a stack como "a definir".
- **[O] Objetivo:**
  1. Escrever `docs/arquitetura.md` com a arquitetura definida, incluindo as seções que garantem replicação (versões, decisões registradas, guardrails, relógio injetável), geração correta sem lacunas (contratos, modelo de dados, view model, estado, regras de dependência, mensagens e erros, decisões de detalhe, tokens visuais) e geração eficiente (fatias de implementação, definição de pronto, estratégia de testes, convenções, guia rápido)
  2. Registrar as versões exatas em `requirements.txt`, `requirements-dev.txt` e `environment.yml`, conferidas contra o Python 3.13
  3. Varrer o projeto (CLAUDE.md, README, docs/, .gitignore, .claude/) e atualizar o que deixou de ser verdade
  4. Registrar este prompt
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Resumo de tudo o que foi criado e alterado, com o motivo de cada mudança, para validação antes do commit.

## 2026-10-04 — Etapa: Arquitetura

- **[C] Contexto:** O `docs/arquitetura.md` já foi escrito. A seção 2.2 traz um diagrama de sequência que cobre só a troca de cidade. Na conversa foi criado um diagrama de sequência Mermaid mais completo, que descreve o fluxo da aplicação como concebido: a página é entregue pelo FastAPI, os blocos se inscrevem no estado, a localização é pedida com prazo de 10 s (com geocodificação reversa ou a cidade padrão), o cache é consultado, o backend chama o OpenWeatherMap com a chave e devolve o view model, respostas antigas são descartadas, os blocos são desenhados, as tiles do mapa são carregadas, e o usuário interage (escala, aba, busca, retorno à página).
- **[O] Objetivo:**
  1. Substituir o diagrama da seção 2.2 de `docs/arquitetura.md` pelo diagrama de sequência completo, para manter uma única fonte do fluxo técnico
  2. Acrescentar uma legenda de leitura e a regra de que o diagrama muda junto com contratos e fluxos
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Confirmação da troca da seção 2.2, com o novo título e a legenda.

## 2026-10-04 — Etapa: Arquitetura

- **[C] Contexto:** A etapa de arquitetura foi concluída e validada pelo usuário. Ainda não foram commitados: `docs/arquitetura.md` (com o diagrama de sequência completo), `requirements.txt`, `requirements-dev.txt`, `environment.yml`, `.env.example`, o print `docs/referencia/referencia_visual.png`, as atualizações de CLAUDE.md, README, `.gitignore`, `docs/spec.md`, `docs/product-brief.md` e `docs/requisitos.md`, e os registros de prompt. A mensagem de commit `docs(arquitetura): definir arquitetura, stack e versões do MVP` já foi aprovada pelo usuário. A branch `main` local está sincronizada com `origin/main`.
- **[O] Objetivo:**
  1. Fazer um único commit com todas as alterações da etapa de arquitetura, usando a mensagem aprovada
  2. Enviar o commit ao GitHub com `git push` e confirmar a sincronização entre local e remoto
- **[S] Estilo:** Técnico e organizado
- **[T] Tom:** Objetivo
- **[A] Público:** Aluno de pós-graduação aprendendo IA Generativa no SDLC.
- **[R] Resposta:** Hash do commit, lista de arquivos incluídos, confirmação do push e estado de sincronização.
