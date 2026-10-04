# Constitution — OpenWeather Dashboard

Princípios permanentes que valem para todo o produto, em qualquer feature, etapa ou decisão de arquitetura.

- Se um requisito do [spec.md](spec.md) contrariar um princípio, **o princípio prevalece** e o requisito deve ser corrigido.
- Um princípio só muda por decisão explícita, registrada em [prompts-costar.md](prompts-costar.md).
- Contexto do produto: [product-brief.md](product-brief.md).

## Segurança

- **P-001** — NUNCA escrever a chave de API em código, commits, documentação, logs ou prompts.
- **P-002** — SEMPRE obter a chave de API da configuração de ambiente mantida fora do controle de versão.
- **P-003** — NUNCA interpretar como código ou marcação um texto recebido de serviço externo.
- **P-004** — NUNCA exibir ao usuário mensagens técnicas brutas, como códigos de erro, rastros de execução ou respostas do provedor.

## Privacidade

- **P-005** — SEMPRE obter a localização do usuário somente pelo pedido de permissão do navegador.
- **P-006** — NUNCA registrar em log a localização do usuário.
- **P-007** — NUNCA armazenar a localização do usuário depois que a página for fechada ou recarregada.
- **P-008** — NUNCA enviar a localização do usuário a serviço que não seja necessário para obter o clima, o nome da cidade ou o mapa.
- **P-009** — SEMPRE manter a busca por cidade disponível quando a localização do usuário não puder ser obtida.

## Consumo do provedor e tratamento de dados

- **P-010** — NUNCA consultar de novo o clima de uma mesma cidade antes de vencer o cache de 10 minutos.
- **P-011** — NUNCA consultar o provedor apenas para mudar a forma de apresentar dados já recebidos.
- **P-012** — SEMPRE descartar a resposta que não corresponda à cidade selecionada no momento em que ela chega.
- **P-013** — SEMPRE exibir "—" quando um dado não vier do provedor, nunca um valor estimado ou inventado.
- **P-014** — SEMPRE calcular conversões a partir do valor original recebido do provedor, nunca de um valor já arredondado.

## Apresentação

- **P-015** — SEMPRE exibir datas e horas no fuso horário local da cidade selecionada.
- **P-016** — SEMPRE exibir os textos da interface em português do Brasil.
- **P-017** — SEMPRE deixar identificável na tela a unidade de medida de cada valor numérico exibido.
- **P-018** — NUNCA usar a cor como único meio de transmitir uma informação.
- **P-019** — SEMPRE exibir as atribuições exigidas pelos provedores de dados e de mapas.

## Resiliência e usabilidade

- **P-020** — SEMPRE indicar visualmente quando um bloco estiver aguardando dados.
- **P-021** — NUNCA deixar a falha de um bloco impedir a exibição dos demais.
- **P-022** — SEMPRE informar ao usuário o que aconteceu e o que ele pode fazer quando uma operação falhar.
- **P-023** — SEMPRE permitir operar todas as funções pelo teclado.
- **P-024** — SEMPRE manter a página utilizável a partir de 360 px de largura, sem rolagem horizontal da página.

## Escopo e processo

- **P-025** — NUNCA exigir cadastro ou login para usar o produto.
- **P-026** — NUNCA incluir detalhes de stack tecnológica nos artefatos de requisitos.
- **P-027** — SEMPRE rastrear cada funcionalidade implementada até um requisito do spec (RF, RN, RNF ou CA).
