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

## 2026-09-30 — Etapa: Documentação

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
