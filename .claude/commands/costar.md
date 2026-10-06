---
description: Reescreve o pedido em CO-STAR, registra em docs/prompts-costar.md e executa
argument-hint: <seu pedido em linguagem livre>
---

Pedido do usuário:

$ARGUMENTS

Valores padrão, usados quando o pedido não indicar outro:
- Style: didático e organizado
- Tone: objetivo
- Audience: aluno de pós-graduação aprendendo IA Generativa no SDLC

Siga estes passos, na ordem:

1. **Reescreva o pedido em CO-STAR**, usando o contexto do projeto (CLAUDE.md e docs/).
   O prompt é meu, não seu: complete o que eu não detalhei, mas escreva como se eu tivesse escrito.
   - Use a primeira pessoa no contexto ("Estou…", "Decidi…", "Na minha máquina…") e ordens diretas
     no objetivo e na resposta ("Crie…", "Proponha…", "Aguarde a minha validação…", "Confirme…").
   - Escreva um pedido natural e independente, não um relato da conversa: em vez de "Pedi na conversa
     um diagrama…", escreva "Crie um diagrama…"; em vez de "Já aprovei a mensagem X", escreva "Use a mensagem X".
   - Nunca use "o usuário", "o autor", "validado pelo usuário" ou construções do seu ponto de vista.
   - Registrar o prompt e commitar esse registro são etapas do processo (passo 4), não do meu pedido:
     nunca inclua no prompt itens como "Registre este prompt", "faça o commit dele" ou
     "incluindo este registro".
   - **[C] Contexto:** situação atual do projeto relevante para o pedido
   - **[O] Objetivo:** o que deve ser feito, em itens claros e verificáveis
   - **[S] Estilo:** como a resposta deve ser estruturada
   - **[T] Tom:** tom da resposta
   - **[A] Público:** aluno de pós-graduação aprendendo IA Generativa no SDLC (padrão)
   - **[R] Resposta:** formato esperado da entrega

2. **Identifique a etapa do SDLC**: Setup, Requisitos, Arquitetura, Implementação,
   Testes, Deploy ou Documentação. Se não der para identificar com segurança, pergunte.

3. **Mostre o prompt CO-STAR e a etapa ao usuário** e peça confirmação antes de continuar.

4. **Registre** ao final de `docs/prompts-costar.md`, neste formato:

   ```
   ## AAAA-MM-DD — Etapa: <etapa>

   - **[C] Contexto:** ...
   - **[O] Objetivo:** ...
   - **[S] Estilo:** ...
   - **[T] Tom:** ...
   - **[A] Público:** ...
   - **[R] Resposta:** ...

   ```

   Use a data de hoje. Nunca inclua a API key ou outros segredos no registro.

5. **Execute** o prompt CO-STAR, respeitando as regras do CLAUDE.md
   (explicar decisões antes de implementar, passos pequenos).
