# Requisitos

Índice dos artefatos de requisitos do MVP, no formato de spec-driven development. Leia na ordem abaixo.

| Ordem | Artefato | Conteúdo |
|---|---|---|
| 1 | [product-brief.md](product-brief.md) | O que é o produto, por que existe, atores, fluxo de uso (Mermaid), glossário geral e aviso de finalidade didática |
| 2 | [constitution.md](constitution.md) | Princípios permanentes P-001 a P-027, no formato SEMPRE/NUNCA. Prevalecem sobre o spec |
| 3 | [spec.md](spec.md) | Glossário consolidado e especificação das 7 features: problema, atores, escopo, histórias, RF (EARS), RN, erros e casos de borda, RNF, dependências e premissas e critérios de aceite |

## Features do MVP

1. Localização inicial, busca de cidade e carregamento dos dados
2. Condições atuais
3. Previsão diária
4. Previsão hora a hora
5. Previsão por minuto
6. Mapa de precipitação
7. Alternância de unidades

## Decisões tomadas nesta etapa

| Decisão | Escolha |
|---|---|
| API de clima | One Call API 4.0: uma consulta de clima por cidade, feita com 5 chamadas (dados atuais, por minuto, 2 páginas por hora e diária), mais 1 por alerta. A 3.0, escolhida no início, foi descontinuada e não aceita novas assinaturas (ADR-013 da arquitetura) |
| Cidade inicial | Localização do navegador. Se não estiver disponível em 10 s, Uberlândia, BR |
| Dias de previsão | "Hoje" + 7. A API entrega até 10 dias por página, e o produto usa os 8 primeiros a partir de hoje |
| Idioma | Interface toda em português do Brasil, com horário em 24 horas |
| Unidades | °C com m/s ou °F com mph, convertidos sem nova consulta |
| Cache | Uma consulta por cidade a cada 10 minutos, só em memória |

A stack tecnológica não faz parte desta etapa. Ela está definida em [arquitetura.md](arquitetura.md). O plano de implementação, com a fatia em que cada ID é atendido, está em [tasks.md](tasks.md).

O histórico dos prompts desta etapa está em [prompts-costar.md](prompts-costar.md).
