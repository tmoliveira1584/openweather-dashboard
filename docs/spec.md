# Spec — OpenWeather Dashboard (MVP)

Especificação funcional do MVP, organizada por feature. Contexto do produto em [product-brief.md](product-brief.md). Princípios obrigatórios em [constitution.md](constitution.md) (referenciados como P-xxx). Este documento não trata de stack tecnológica (P-026).

## Como ler este documento

### Numeração

- RF (requisito funcional), RN (regra de negócio), RNF (requisito não-funcional) e CA (critério de aceite) seguem **uma única sequência no documento inteiro**. Assim, cada ID aponta para um item só.
- **RF** descreve o que o sistema faz. **RN** descreve a lógica, os valores e os limites por trás do RF.

### Notação EARS dos requisitos funcionais

| Padrão | Forma | Quando usar |
|---|---|---|
| Ubíquo | O SISTEMA DEVE … | Comportamento sempre válido |
| Evento | QUANDO <gatilho>, O SISTEMA DEVE … | Reação a uma ação ou acontecimento |
| Estado | ENQUANTO <estado>, O SISTEMA DEVE … | Comportamento durante uma condição |
| Indesejado | SE <condição indesejada>, ENTÃO O SISTEMA DEVE … | Falhas e exceções |
| Opcional | ONDE <característica presente>, O SISTEMA DEVE … | Comportamento que depende de algo existir |

### Critérios de aceite

Escritos em Given/When/Then, na forma em português **Dado / Quando / Então**.

### Roteiro de erros e casos de borda

Cada feature cobre as categorias que se aplicam a ela. O número entre parênteses no início de cada cenário indica a categoria:

| # | Categoria | O que verificar |
|---|---|---|
| 1 | Entrada inválida | Termo vazio, curto, longo, com caracteres especiais, sem resultado ou ambíguo |
| 2 | Localização do navegador | Permissão negada, recurso indisponível, sem resposta, resposta tardia |
| 3 | Credencial e cota | Acesso recusado pelo provedor, limite de consultas excedido |
| 4 | Serviço externo | Provedor fora do ar, lento ou sem conexão |
| 5 | Resposta incompleta | Bloco ou campo ausente, valor fora do formato |
| 6 | Valores-limite | Fronteiras de faixas, zero, negativos, máximos |
| 7 | Ações repetidas e concorrentes | Clique duplo, repetição da mesma ação, respostas fora de ordem, ação durante carregamento |
| 8 | Cache e tempo | Cache vencido, página em segundo plano, virada de dia, fuso diferente do usuário, saída e retorno à página |
| 9 | Recursos visuais | Ícone, imagem ou mapa que não carrega |
| 10 | Volume e tela | Muitos itens, textos longos, telas estreitas |

Itens do roteiro genérico de sistemas transacionais não se aplicam a este produto e foram omitidos de propósito: permissão por perfil, concorrência de edição, sessão expirada e dados legados. O produto é só de leitura, não tem login (P-025) e não guarda dados entre visitas.

### Visão geral da tela

| Bloco da tela | Feature |
|---|---|
| Cabeçalho: cidade atual e busca | 1. Localização inicial, busca de cidade e carregamento dos dados |
| Card principal e seis indicadores, aba "Hoje" | 2. Condições atuais |
| Faixa de abas de dias e resumo do dia selecionado | 3. Previsão diária |
| Bloco "Previsão hora a hora" | 4. Previsão hora a hora |
| Painel "Previsão por minuto — precipitação" | 5. Previsão por minuto |
| Mapa com marcador e camada de chuva | 6. Mapa de precipitação |
| Seletor °C/°F do cabeçalho | 7. Alternância de unidades |

### Serviços externos

| Serviço | Endereço |
|---|---|
| Dados atuais (One Call API 4.0) | `https://api.openweathermap.org/data/4.0/onecall/current?lat={lat}&lon={lon}&units=metric&lang=pt_br&appid={API_KEY}` |
| Previsão por minuto (One Call API 4.0) | `https://api.openweathermap.org/data/4.0/onecall/timeline/1min?lat={lat}&lon={lon}&units=metric&lang=pt_br&appid={API_KEY}` (até 60 minutos) |
| Previsão por hora (One Call API 4.0) | `https://api.openweathermap.org/data/4.0/onecall/timeline/1h?lat={lat}&lon={lon}&start={início}&units=metric&lang=pt_br&appid={API_KEY}` (até 20 horas por página) |
| Previsão diária (One Call API 4.0) | `https://api.openweathermap.org/data/4.0/onecall/timeline/1day?lat={lat}&lon={lon}&units=metric&lang=pt_br&appid={API_KEY}` (até 10 dias por página) |
| Busca de cidade (geocodificação direta) | `https://api.openweathermap.org/geo/1.0/direct?q={cidade}&limit=5&appid={API_KEY}` |
| Nome por coordenadas (geocodificação reversa) | `https://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={API_KEY}` |
| Ícones de condição | `https://openweathermap.org/img/wn/{icon}@2x.png` |
| Camada de precipitação do mapa | `https://tile.openweathermap.org/map/precipitation_new/{z}/{x}/{y}.png?appid={API_KEY}` |
| Mapa base | Definido em [arquitetura.md](arquitetura.md) (ADR-006) |

`{API_KEY}` é um marcador. A chave real fica só na configuração de ambiente (P-001, P-002).

A One Call API 3.0, usada na primeira versão deste spec, foi descontinuada pelo fornecedor e não aceita novas assinaturas. Por isso os dados do clima vêm da One Call API 4.0, que separa os dados atuais e cada previsão em endereços próprios. A forma de combinar essas chamadas está em [arquitetura.md](arquitetura.md) (ADR-013).

---

## Glossário

Termos usados ao longo deste spec, em ordem alfabética. A coluna **Features** indica as seções em que o termo aparece. Os termos gerais do produto (cidade selecionada, cache, cota, previsão diária etc.) estão no glossário do [product-brief.md](product-brief.md).

| Termo | Definição | Features |
|---|---|---|
| Aba de dia | Botão da faixa superior que representa um dia da previsão. | 3, 7 |
| Atribuição | Crédito obrigatório aos provedores do mapa e dos dados, exibido sobre o mapa. | 6 |
| Aviso de localização | Mensagem informativa exibida quando a cidade padrão é usada no lugar da localização. | 1 |
| Barra | Representação gráfica da intensidade de um minuto. | 5, 6 |
| Calmo | Vento com velocidade menor que 0,5 m/s, exibido sem velocidade e sem direção. | 2, 7 |
| Camada de precipitação | Imagem semitransparente que mostra onde está chovendo agora. | 6 |
| Card principal | Bloco de destaque com temperatura, descrição, sensação térmica, hora e selo de alertas. | 2, 3, 4, 7 |
| Chance de precipitação | Probabilidade de chover naquela hora, em percentual. | 4, 7 |
| Chave de cache | Identificador dos dados guardados: as coordenadas arredondadas a 2 casas decimais. | 1 |
| Cidades homônimas | Cidades diferentes com o mesmo nome, diferenciadas pelo estado e pelo país. | 1 |
| Código de condição | Número que o provedor usa para classificar o tempo (ex.: 501 = chuva moderada). | 2 |
| Consulta de clima | Obtenção, de uma só vez, de todos os dados meteorológicos de uma cidade: atuais, por minuto, por hora e diários. Com o provedor atual, envolve 5 chamadas, mais 1 por alerta da cidade, e cada uma conta na cota. | 1, 7 |
| Conversão local | Cálculo feito sobre dados já recebidos, sem nova consulta ao provedor. | 7 |
| Curva de temperatura | Linha que mostra a variação da temperatura ao longo da janela. | 4 |
| Escala ativa | Escala de temperatura escolhida no momento (°C ou °F), que também define a unidade do vento. | 2, 4, 5, 7 |
| Estado de erro | Aparência de um bloco quando seus dados não puderam ser obtidos: mensagem e botão "Tentar novamente". | 1, 2 |
| Etiqueta de chuva | Marcação sobre a curva com o volume de chuva de uma hora. | 4 |
| Faixa de abas | Linha com todas as abas de dias, com rolagem horizontal quando necessário. | 3 |
| Faixa de intensidade | Intervalo de intensidade associado a uma cor da legenda. | 5 |
| Grupo de condição | Agrupamento de códigos de condição usado para escolher a imagem ilustrativa. | 2 |
| Índice UV | Escala da intensidade da radiação ultravioleta do sol. | 2, 3, 7 |
| Intensidade de precipitação | Quantidade de chuva por unidade de tempo, em milímetros por hora (mm/h). | 5 |
| Janela de 24 horas | Período exibido no bloco: da hora atual da cidade até 23 horas depois. | 4 |
| Lista de resultados | Até 5 cidades devolvidas pela busca, mostradas abaixo do campo. | 1 |
| Mapa base | Mapa geográfico (ruas, cidades, relevo) sobre o qual ficam as demais informações. | 6 |
| Marcador | Símbolo no mapa que indica a posição da cidade selecionada. | 6 |
| Marco | Rótulo de referência de tempo no eixo das barras (Agora, 15, 30, 45 e 60 min). | 5 |
| Máxima e mínima | Maior e menor temperatura previstas para o dia. | 3, 7 |
| mph | Milhas por hora, unidade de velocidade do vento usada com a escala °F. | 7 |
| Nível de zoom | Grau de aproximação do mapa. Valores maiores mostram áreas menores com mais detalhe. | 6 |
| Ponto de orvalho | Temperatura em que o ar fica saturado e o vapor começa a condensar. | 2, 3, 7 |
| Prazo de localização | Tempo máximo de espera pela localização do navegador antes de usar a cidade padrão (10 s). | 1 |
| Pressão atmosférica | Força do ar sobre a superfície, medida em hectopascais (hPa). | 2 |
| Resumo da próxima hora | Frase que descreve em texto a precipitação prevista para os próximos 60 minutos. | 5 |
| Rosa de 8 pontos | Divisão das direções em N, NE, L, SE, S, SO, O e NO. | 2 |
| Seletor de escala | Controle do cabeçalho com as opções °C e °F. | 7 |
| Selo de alertas | Indicador com a quantidade de alertas meteorológicos ativos. | 2, 3 |
| Sensação térmica | Temperatura percebida pelo corpo, considerando vento e umidade. | 2, 3, 7 |
| Sensação térmica diurna | Sensação térmica prevista para o período do dia (não a da noite). | 3 |
| Tempo limite | Tempo máximo de espera por uma resposta do provedor antes de considerar falha (15 s). | 1 |
| Termo de busca | Texto digitado pelo usuário para procurar uma cidade. | 1 |
| Umidade relativa | Percentual de vapor d'água no ar em relação ao máximo possível naquela temperatura. | 2 |
| Validade do cache | Tempo em que dados guardados podem ser reaproveitados sem nova consulta (10 minutos). | 1 |
| Valor original | Valor exatamente como veio do provedor, antes de qualquer conversão ou arredondamento. | 7 |
| Vigência do alerta | Intervalo entre o início e o fim de um alerta meteorológico. | 2, 3 |
| Visibilidade | Distância máxima em que objetos podem ser vistos com nitidez. | 2, 3, 7 |
| Volume de chuva | Quantidade de chuva prevista para a hora, em milímetros por hora (mm/h). | 4, 7 |

---

## 1. Localização inicial, busca de cidade e carregamento dos dados

### Problema

O usuário quer ver o clima de onde está sem configurar nada e quer consultar qualquer outra cidade pelo nome, distinguindo cidades com o mesmo nome. Cada troca de cidade dispara a obtenção dos dados meteorológicos. Essa obtenção precisa economizar a cota do provedor e tolerar falhas.

### Atores

| Ator | Descrição | O que pode fazer | O que não pode fazer |
|---|---|---|---|
| Usuário | Pessoa que acessa o dashboard | Autorizar ou negar a localização; buscar uma cidade pelo nome; escolher uma cidade da lista; tentar de novo após uma falha | Informar coordenadas manualmente; salvar cidades favoritas; ver histórico de buscas; forçar nova consulta antes de 10 minutos |
| Navegador | Intermediário entre o usuário e o recurso de localização do dispositivo | Pedir permissão ao usuário; informar as coordenadas; informar recusa ou indisponibilidade | Informar a localização sem autorização do usuário |
| OpenWeatherMap | Provedor de geocodificação e de dados meteorológicos | Devolver até 5 cidades para um nome; devolver o nome de uma cidade a partir de coordenadas; devolver os dados meteorológicos | Receber dados do usuário além do termo de busca e das coordenadas (P-008) |

### Escopo

**Incluso**
- Pedido de localização ao navegador quando a página abre.
- Cidade padrão com aviso quando a localização não estiver disponível.
- Nome da cidade obtido a partir das coordenadas (geocodificação reversa).
- Campo de busca acionado pela tecla Enter ou pelo ícone de lupa.
- Lista de até 5 cidades com nome, estado e país.
- Seleção direta quando a busca devolve uma única cidade.
- Cidade selecionada exibida no cabeçalho.
- Uma consulta de clima por cidade, com cache de 10 minutos.
- Nova consulta ao voltar à página com dados vencidos.
- Mensagens de erro com a opção "Tentar novamente".

**Não incluso**
- Sugestões enquanto o usuário digita (autocompletar).
- Botão para voltar à localização do usuário depois de buscar outra cidade.
- Favoritos, histórico de buscas ou cidade lembrada entre visitas.
- Busca por CEP, endereço ou coordenadas.
- Atualização periódica automática enquanto a página está visível.

### Histórias de usuário

- Como usuário, quero ver o clima da minha localização ao abrir a página, para não precisar digitar nada.
- Como usuário, quero ver uma cidade padrão quando não autorizo a localização, para usar o dashboard mesmo assim.
- Como usuário, quero buscar uma cidade pelo nome, para consultar o tempo de outro lugar.
- Como usuário, quero distinguir cidades com o mesmo nome pelo estado e pelo país, para escolher a cidade certa.
- Como usuário, quero ser avisado com clareza quando os dados não puderem ser carregados, para saber se devo tentar de novo.

### Requisitos funcionais

| ID | Requisito (EARS) |
|---|---|
| RF-001 | QUANDO a página for aberta, O SISTEMA DEVE pedir ao navegador a localização do dispositivo. |
| RF-002 | QUANDO o navegador informar as coordenadas, O SISTEMA DEVE torná-las a cidade selecionada e obter o nome da cidade por geocodificação reversa. |
| RF-003 | SE a localização for negada, estiver indisponível ou não for informada no prazo, ENTÃO O SISTEMA DEVE selecionar a cidade padrão e exibir o aviso de localização. |
| RF-004 | QUANDO uma cidade for selecionada, O SISTEMA DEVE obter os dados meteorológicos dela em uma única consulta de clima, exceto se houver dados válidos no cache. |
| RF-005 | ENQUANTO os dados da cidade selecionada estiverem sendo obtidos, O SISTEMA DEVE exibir um indicador de carregamento nos blocos de dados. |
| RF-006 | QUANDO o usuário confirmar a busca com um termo válido, pela tecla Enter ou pelo ícone de lupa, O SISTEMA DEVE consultar a geocodificação direta e exibir a lista de cidades encontradas. |
| RF-007 | QUANDO a busca devolver uma única cidade, O SISTEMA DEVE selecioná-la sem exibir a lista. |
| RF-008 | QUANDO o usuário escolher uma cidade da lista, O SISTEMA DEVE selecioná-la, fechar a lista e limpar o campo de busca. |
| RF-009 | O SISTEMA DEVE exibir cada item da lista com o nome da cidade, o estado (quando houver) e o país. |
| RF-010 | O SISTEMA DEVE exibir no cabeçalho o nome da cidade selecionada seguido do código do país. |
| RF-011 | QUANDO o usuário pressionar Esc ou clicar fora da lista, O SISTEMA DEVE fechar a lista sem alterar a cidade selecionada. |
| RF-012 | SE a busca não encontrar nenhuma cidade, ENTÃO O SISTEMA DEVE informar o resultado vazio e manter a cidade selecionada. |
| RF-013 | SE a consulta de dados meteorológicos falhar, ENTÃO O SISTEMA DEVE exibir nos blocos de dados uma mensagem de erro com a opção "Tentar novamente". |
| RF-014 | QUANDO a página voltar a ficar visível e os dados exibidos tiverem mais de 10 minutos, O SISTEMA DEVE obter novamente os dados da cidade selecionada. |
| RF-015 | ENQUANTO uma busca ou uma consulta estiver em andamento, O SISTEMA DEVE ignorar novos pedidos idênticos a ela. |

### Regras de negócio

| ID | Regra |
|---|---|
| RN-001 | A cidade padrão é Uberlândia, BR (lat -18.9186, lon -48.2772). |
| RN-002 | O navegador tem 10 s para informar a localização, contados a partir do pedido. O aviso de localização pode ser fechado pelo usuário e some quando outra cidade é escolhida. |
| RN-003 | Se a localização chegar depois do prazo e o usuário ainda não tiver escolhido outra cidade, ela substitui a cidade padrão. Se o usuário já tiver escolhido outra cidade, a localização é descartada. |
| RN-004 | Um termo de busca é válido quando, sem os espaços do início e do fim, tem de 2 a 100 caracteres. Qualquer caractere é aceito e tratado como texto, sem interpretação (P-003). |
| RN-005 | A lista mostra no máximo 5 cidades, na ordem de relevância devolvida pelo provedor. O termo pode incluir estado e país separados por vírgula para refinar a busca (ex.: "Santa Maria, BR"). |
| RN-006 | O nome exibido é o nome em português informado pelo provedor. Se ele não existir, usa-se o nome padrão do provedor. |
| RN-007 | O cabeçalho usa o formato "<nome>, <código do país com 2 letras>". Exemplo: "Uberlândia, BR". |
| RN-008 | Cada item da lista usa o formato "<nome>, <estado>, <país>" ou, sem estado, "<nome>, <país>". Exemplo: "Uberlândia, Minas Gerais, BR". |
| RN-009 | Se a geocodificação reversa não devolver um nome, o cabeçalho exibe "Sua localização". |
| RN-010 | Cache: a chave são as coordenadas arredondadas a 2 casas decimais (cerca de 1 km). A validade é de 10 minutos a partir do recebimento da resposta. O cache existe só em memória e some ao recarregar a página (P-010). |
| RN-011 | Respostas com erro nunca são guardadas no cache. |
| RN-012 | Uma consulta ao provedor que passe de 15 s sem resposta é considerada falha por lentidão. Depois de 3 s sem resposta, o indicador de carregamento passa a exibir "Ainda carregando…". |
| RN-013 | Ao trocar de cidade, o cabeçalho mostra a nova cidade imediatamente e os blocos de dados mostram carregamento. Os dados da cidade anterior deixam de ser exibidos. "Tentar novamente" refaz apenas a consulta que falhou. |

### Comportamento em erro e casos de borda

| Cenário | Comportamento esperado | Mensagem ao usuário |
|---|---|---|
| (1) Busca confirmada com o campo vazio ou só com espaços | Nenhuma consulta. Foco permanece no campo. | "Digite o nome de uma cidade." |
| (1) Termo com 1 caractere | Nenhuma consulta. Foco permanece no campo. | "Digite pelo menos 2 caracteres." |
| (1) Termo com mais de 100 caracteres | O campo não aceita caracteres além do 100º. | Nenhuma (o campo para de aceitar caracteres) |
| (1) Termo com marcação ou símbolos (ex.: `<b>Rio</b>`) | O termo é enviado como texto. O resultado é exibido como texto, sem interpretação (P-003). | Conforme o resultado da busca |
| (1) Cidade inexistente | A lista não abre. A cidade selecionada e seus dados continuam na tela. | "Nenhuma cidade encontrada para "<termo>". Verifique a grafia." |
| (1) Mais de 5 cidades com o mesmo nome | A lista mostra as 5 primeiras, com estado e país, e uma dica no rodapé. | "Mostrando as 5 primeiras cidades. Inclua o estado ou o país para refinar (ex.: Santa Maria, BR)." |
| (2) Usuário nega a permissão de localização | Cidade padrão selecionada. Aviso exibido abaixo do cabeçalho. | "Não foi possível usar sua localização. Mostrando Uberlândia, BR. Use a busca para escolher outra cidade." |
| (2) Navegador sem recurso de localização ou página fora de contexto seguro | Igual à permissão negada. | Mesma mensagem da permissão negada |
| (2) Usuário não responde ao pedido de permissão em 10 s | Cidade padrão selecionada, com aviso (RN-002). | Mesma mensagem da permissão negada |
| (2) Localização chega depois do prazo e o usuário não buscou outra cidade | A localização substitui a cidade padrão e o aviso some (RN-003). | Nenhuma |
| (2) Localização chega depois de o usuário escolher outra cidade | A localização é descartada (RN-003). | Nenhuma |
| (2) Usuário faz uma busca enquanto o pedido de localização está pendente | A busca funciona normalmente. A cidade escolhida prevalece sobre a localização tardia. | Nenhuma |
| (2) Geocodificação reversa sem resultado ou com falha | Os dados meteorológicos são exibidos normalmente. O cabeçalho mostra "Sua localização" (RN-009). | Nenhuma |
| (3) Provedor recusa o acesso (chave inválida ou sem assinatura) | Os blocos de dados mostram estado de erro com "Tentar novamente". A busca continua disponível. Um log técnico registra só o código do erro, sem a chave (P-001). | "O serviço de clima recusou o acesso. Tente novamente mais tarde." |
| (3) Limite de consultas do provedor excedido | Estado de erro nos blocos, com "Tentar novamente". | "Limite de consultas ao serviço de clima atingido. Tente novamente em alguns minutos." |
| (4) Provedor de clima fora do ar | Estado de erro nos blocos, com "Tentar novamente". | "O serviço de clima está indisponível no momento." |
| (4) Provedor lento: mais de 3 s sem resposta | O indicador de carregamento continua, com texto adicional. | "Ainda carregando…" |
| (4) Provedor lento: mais de 15 s sem resposta | A consulta é considerada falha (RN-012). Estado de erro com "Tentar novamente". | "O serviço de clima demorou para responder." |
| (4) Sem conexão com a internet | Estado de erro com "Tentar novamente". | "Sem conexão com a internet. Verifique sua rede e tente novamente." |
| (4) Uma das chamadas da consulta de clima falha (acesso recusado, limite excedido, provedor fora do ar, lento ou sem conexão) | A consulta inteira é tratada como falha, com a mensagem do tipo de falha e "Tentar novamente". Nada vai para o cache (RN-011). | Conforme o tipo de falha, nas mensagens acima |
| (4) Geocodificação direta falha durante a busca | A lista não abre. A cidade selecionada continua na tela. | "Não foi possível buscar cidades agora. Tente novamente." |
| (7) Duplo Enter ou duplo clique na lupa | Uma única busca é feita (RF-015). | Nenhuma |
| (7) Vários cliques em "Tentar novamente" | Uma única consulta fica em andamento (RF-015). | Nenhuma |
| (7) Usuário escolhe a cidade que já está selecionada | Os dados vêm do cache, sem nova consulta e sem carregamento visível. | Nenhuma |
| (7) Usuário escolhe a cidade A e, antes da resposta, a cidade B | A resposta de A é descartada ao chegar. A tela mostra B (P-012). | Nenhuma |
| (8) Usuário volta a uma cidade consultada há menos de 10 minutos | Os dados vêm do cache imediatamente, sem consulta (RN-010). | Nenhuma |
| (8) Usuário volta a uma cidade consultada há mais de 10 minutos | Nova consulta, com carregamento. | Nenhuma |
| (8) Página fica em segundo plano por mais de 10 minutos e o usuário volta | Os dados antigos continuam visíveis enquanto uma nova consulta é feita (RF-014). Depois, a tela é atualizada. | "Atualizando…" |
| (8) Usuário fecha ou recarrega a página no meio de uma busca e volta depois | A página recomeça do início: novo pedido de localização, cache vazio e termo de busca não lembrado (P-007). | Conforme o resultado da localização |
| (10) Nome de cidade longo no cabeçalho | O nome é cortado com "…". O nome completo aparece ao passar o cursor ou ao focar o elemento. | Nenhuma |
| (10) Tela estreita (a partir de 360 px) | O campo de busca ocupa a largura disponível e a lista abre logo abaixo dele, sem rolagem horizontal da página (P-024). | Nenhuma |

### Requisitos não-funcionais

| ID | Categoria | Requisito |
|---|---|---|
| RNF-001 | Desempenho | Com o provedor respondendo normalmente, todos os blocos de dados ficam visíveis em até 3 s depois que a cidade é definida. |
| RNF-002 | Desempenho | Dados servidos do cache aparecem em até 200 ms, sem indicador de carregamento visível. |
| RNF-003 | Custo e cota | No máximo 1 consulta de clima (5 chamadas ao provedor, mais 1 por alerta) por cidade a cada 10 minutos por página aberta, e 1 consulta de geocodificação por busca confirmada (P-010). |
| RNF-004 | Segurança | A chave de API não aparece em nenhum arquivo versionado nem em mensagens exibidas ao usuário (P-001, P-002). |
| RNF-005 | Privacidade | As coordenadas do usuário não são registradas em log nem guardadas no dispositivo depois que a página é fechada (P-006, P-007). |
| RNF-006 | Compatibilidade | O produto funciona nas duas versões mais recentes de Chrome, Edge, Firefox e Safari, em computador e celular. |
| RNF-007 | Acessibilidade | O campo de busca tem o rótulo acessível "Buscar cidade". A lista pode ser operada só pelo teclado: setas para navegar, Enter para escolher e Esc para fechar (P-023). |
| RNF-008 | Usabilidade | As mensagens de erro usam linguagem simples, sem códigos nem termos técnicos, e indicam uma ação possível (P-004, P-022). |

### Dependências e premissas

**Dependências**
- Geocoding API do OpenWeatherMap (direta e reversa).
- One Call API 4.0 do OpenWeatherMap, com a assinatura "One Call by Call" ativa.
- Chave de API válida, configurada no ambiente.
- Recurso de localização do navegador.

**Premissas**
- A One Call API 4.0 continuará disponível durante o projeto. A 3.0 foi descontinuada e não aceita novas assinaturas, por isso não é usada.
- A cota gratuita de 1.000 chamadas por dia é suficiente para o uso acadêmico. Cada consulta de clima usa 5 chamadas, mais 1 por alerta da cidade, o que permite cerca de 200 consultas por dia em cidades sem alertas, já contando o cache de 10 minutos.
- A página será servida em contexto seguro (HTTPS ou endereço local). Os navegadores exigem isso para liberar a localização.
- O provedor informa o nome em português para cidades brasileiras.
- Coordenadas arredondadas a 2 casas decimais representam a mesma cidade para fins de cache.

### Critérios de aceite

1. **CA-001** — **Dado** que o usuário autoriza a localização, **Quando** a página é aberta, **Então** o cabeçalho mostra o nome da cidade onde ele está e os blocos mostram os dados dessa cidade.
2. **CA-002** — **Dado** que o usuário nega a localização, **Quando** a página é aberta, **Então** o dashboard mostra Uberlândia, BR e exibe o aviso "Não foi possível usar sua localização…".
3. **CA-003** — **Dado** que o usuário não responde ao pedido de localização, **Quando** passam 10 s, **Então** o dashboard mostra a cidade padrão com o aviso.
4. **CA-004** — **Dado** que o usuário digitou "Santa Maria", **Quando** confirma a busca, **Então** a lista mostra até 5 cidades, cada uma com nome, estado e país.
5. **CA-005** — **Dado** que a lista de resultados está aberta, **Quando** o usuário escolhe "Curitiba, Paraná, BR", **Então** o cabeçalho mostra "Curitiba, BR" e os blocos são atualizados com os dados de Curitiba.
6. **CA-006** — **Dado** que o usuário digitou "Xyzabc", **Quando** confirma a busca, **Então** aparece "Nenhuma cidade encontrada para "Xyzabc". Verifique a grafia." e a cidade selecionada continua exibida.
7. **CA-007** — **Dado** que os dados de Curitiba foram obtidos há 5 minutos, **Quando** o usuário seleciona Curitiba de novo, **Então** os dados aparecem sem nova consulta ao provedor.
8. **CA-008** — **Dado** que o provedor de clima está fora do ar, **Quando** uma cidade é selecionada, **Então** os blocos mostram "O serviço de clima está indisponível no momento." e o botão "Tentar novamente".

---

## 2. Condições atuais

### Problema

O usuário quer entender rapidamente como está o tempo agora: temperatura, aparência do céu, sensação térmica e indicadores complementares. Também quer saber se há alertas meteorológicos oficiais para a cidade.

### Atores

| Ator | Descrição | O que pode fazer | O que não pode fazer |
|---|---|---|---|
| Usuário | Pessoa que consulta o dashboard | Ver as condições atuais e os seis indicadores; ver a quantidade de alertas ativos | Ver o conteúdo dos alertas; ver o histórico de medições; reorganizar ou ocultar cards |
| OpenWeatherMap | Provedor dos dados meteorológicos e dos ícones | Fornecer as medições atuais, a descrição da condição e a lista de alertas | Receber dados do usuário além das coordenadas (P-008) |

### Escopo

**Incluso**
- Card principal na aba "Hoje": temperatura, descrição, sensação térmica, hora local da medição, selo de alertas e imagem ilustrativa por grupo de condição.
- Seis cards de indicadores: Vento, Umidade, Visibilidade, Pressão, Índice UV e Ponto de orvalho.
- Regras de formatação de números, horas e unidades, reaproveitadas pelas demais features.

**Não incluso**
- Conteúdo dos alertas: texto, emissor e vigência.
- Classificação de risco do índice UV (baixo, alto etc.).
- Nascer e pôr do sol, rajadas de vento e nebulosidade.
- Imagens diferentes para dia e noite.
- Atualização em tempo real das medições.

### Histórias de usuário

- Como usuário, quero ver a temperatura e a descrição do tempo agora, para saber como está lá fora.
- Como usuário, quero ver a sensação térmica, para decidir como me vestir.
- Como usuário, quero ver vento, umidade, visibilidade, pressão, índice UV e ponto de orvalho, para ter uma visão completa das condições.
- Como usuário, quero saber quantos alertas meteorológicos estão ativos, para ficar atento a eventos severos.

### Requisitos funcionais

| ID | Requisito (EARS) |
|---|---|
| RF-016 | ENQUANTO a aba "Hoje" estiver selecionada, O SISTEMA DEVE exibir no card principal a temperatura atual, a descrição do tempo, a sensação térmica e a hora local da medição. |
| RF-017 | O SISTEMA DEVE exibir no card principal uma imagem ilustrativa correspondente ao grupo da condição do tempo. |
| RF-018 | ONDE houver alertas meteorológicos ativos para a cidade, O SISTEMA DEVE exibir no card principal um selo com a quantidade de alertas. |
| RF-019 | SE não houver alertas ativos, ENTÃO O SISTEMA DEVE ocultar o selo de alertas. |
| RF-020 | ENQUANTO a aba "Hoje" estiver selecionada, O SISTEMA DEVE exibir seis cards com os valores atuais de Vento, Umidade, Visibilidade, Pressão, Índice UV e Ponto de orvalho. |
| RF-021 | O SISTEMA DEVE exibir a velocidade do vento acompanhada da direção em ponto cardeal. |
| RF-022 | SE a velocidade do vento for menor que 0,5 m/s, ENTÃO O SISTEMA DEVE exibir "Calmo" no lugar da velocidade e da direção. |
| RF-023 | SE um valor do card principal ou dos cards não vier na resposta do provedor, ENTÃO O SISTEMA DEVE exibir "—" no lugar desse valor (P-013). |

### Regras de negócio

| ID | Regra |
|---|---|
| RN-014 | Temperaturas são arredondadas ao inteiro mais próximo para exibição. No card principal, nas abas e na previsão hora a hora aparecem com "°" (ex.: "20°"), e a escala ativa fica identificada no seletor °C/°F do cabeçalho. No card Ponto de orvalho aparecem com a escala completa (ex.: "19 °C"). |
| RN-015 | Hora local = horário UTC da medição + deslocamento de fuso da cidade informado pelo provedor. O formato é HH:MM em 24 horas (ex.: "08:18") (P-015). |
| RN-016 | A descrição é o texto em português fornecido pelo provedor, com a primeira letra maiúscula (ex.: "Nublado"). A sensação térmica aparece como "Sensação de 20°". |
| RN-017 | O grupo de condição sai do código de condição do provedor: 200–299 Tempestade; 300–399 e 500–599 Chuva; 600–699 Neve; 700–799 Névoa; 800 Céu limpo; 801–804 Nublado. Um código fora dessas faixas usa uma imagem neutra. |
| RN-018 | O selo mostra "1 alerta" ou "N alertas", em que N é o número de alertas distintos na resposta, incluindo os que ainda vão começar. A falta da lista de alertas equivale a 0. Acima de 99, mostra "99+ alertas". |
| RN-019 | Vento: a velocidade é arredondada ao inteiro, na unidade da escala ativa. A direção usa a rosa de 8 pontos, com setores de 45°: N [337,5°; 22,5°), NE [22,5°; 67,5°), L [67,5°; 112,5°), SE [112,5°; 157,5°), S [157,5°; 202,5°), SO [202,5°; 247,5°), O [247,5°; 292,5°), NO [292,5°; 337,5°). Exemplo: "4 m/s L". "Calmo" vale quando a velocidade original é menor que 0,5 m/s, em qualquer escala. |
| RN-020 | Umidade: percentual inteiro (ex.: "94%"). |
| RN-021 | Visibilidade: metros ÷ 1.000, exibida em km com até 1 casa decimal e sem casa decimal quando o valor é inteiro (10.000 m → "10 km"; 2.500 m → "2,5 km"). O provedor limita esse valor a 10 km. |
| RN-022 | Pressão: hPa, inteiro (ex.: "1015 hPa"). |
| RN-023 | Índice UV: arredondado ao inteiro (ex.: "2 UV"). |
| RN-024 | Ponto de orvalho: inteiro, com a escala ativa (ex.: "19 °C"). |
| RN-025 | Formato numérico em todo o produto: vírgula como separador decimal, sem separador de milhar e sinal "-" para negativos. Um valor que arredonda para zero nunca aparece como "-0". |

### Comportamento em erro e casos de borda

| Cenário | Comportamento esperado | Mensagem ao usuário |
|---|---|---|
| (4) Falha na consulta de dados | Card principal e cards mostram o estado de erro definido na feature 1 (RF-013). | Conforme a feature 1 |
| (5) Resposta sem a lista de alertas | Selo oculto (RN-018). | Nenhuma |
| (5) Um indicador ausente (ex.: visibilidade) | O card mostra "—". Os demais cards aparecem normalmente (P-013). | Nenhuma |
| (5) Temperatura ou descrição ausente | O card principal mostra "—" no lugar do valor ausente. | Nenhuma |
| (5) Código de condição desconhecido | Imagem neutra (RN-017). | Nenhuma |
| (5) Direção do vento ausente com velocidade de 0,5 m/s ou mais | Só a velocidade aparece (ex.: "4 m/s"). | Nenhuma |
| (6) Velocidade do vento menor que 0,5 m/s | O card Vento mostra "Calmo" (RF-022). | Nenhuma |
| (6) Direção do vento de 0° ou 360° | Exibida como "N". | Nenhuma |
| (6) Temperatura negativa (ex.: -3,4 °C) ou próxima de zero (ex.: -0,3 °C) | Exibe "-3°" e "0°", nunca "-0°" (RN-025). | Nenhuma |
| (6) Índice UV 0 (noite) | Exibe "0 UV". | Nenhuma |
| (6) Visibilidade no limite de 10 km | Exibe "10 km". | Nenhuma |
| (6) Mais de 99 alertas | O selo mostra "99+ alertas". | Nenhuma |
| (8) Fuso da cidade diferente do fuso do usuário (ex.: Tóquio) | A hora da medição aparece no fuso da cidade (RN-015). | Nenhuma |
| (8) Medição com horário antigo (atraso do provedor) | Mostra a hora real da medição, sem ajuste. | Nenhuma |
| (9) Imagem ilustrativa não carrega | O card usa fundo de cor neutra, com o texto legível. | Nenhuma |
| (10) Descrição longa (ex.: "Trovoada com chuva forte") | Quebra em até 2 linhas, sem cortar o texto. | Nenhuma |
| (10) Tela estreita | Os seis cards passam de 3 para 2 colunas, sem rolagem horizontal da página (P-024). | Nenhuma |

### Requisitos não-funcionais

| ID | Categoria | Requisito |
|---|---|---|
| RNF-009 | Acessibilidade | Os textos sobre a imagem ilustrativa têm contraste mínimo de 4,5:1 (WCAG 2.1 nível AA). |
| RNF-010 | Acessibilidade | Imagens e ícones têm texto alternativo com a descrição da condição. O selo de alertas comunica a quantidade em texto, não só pela cor (P-018). |
| RNF-011 | Responsividade | Os seis cards ficam em 3 colunas em telas com 600 px ou mais e em 2 colunas abaixo disso. |
| RNF-012 | Consistência | Um mesmo tipo de valor tem a mesma formatação em todos os blocos (RN-014 a RN-025). |

### Dependências e premissas

**Dependências**
- Dados atuais da One Call API 4.0: medições, descrição, código de condição e identificação dos alertas vigentes e futuros.
- Serviço de ícones do OpenWeatherMap.
- Conjunto de imagens ilustrativas, uma por grupo de condição mais uma neutra, com licença que permita o uso.

**Premissas**
- O provedor devolve a descrição em português quando a consulta pede pt-BR.
- Os códigos de condição seguem a tabela publicada pelo provedor.
- A visibilidade vem em metros, limitada a 10 km.

### Critérios de aceite

1. **CA-009** — **Dado** que a temperatura atual é 20,4 °C, a sensação térmica é 20,6 °C e a medição foi às 08:18 no horário da cidade, **Quando** a aba "Hoje" está selecionada, **Então** o card principal mostra "20°", "Sensação de 21°" e "08:18".
2. **CA-010** — **Dado** que a resposta traz 3 alertas, **Quando** o card principal é exibido, **Então** aparece o selo "3 alertas".
3. **CA-011** — **Dado** que a resposta não traz alertas, **Quando** o card principal é exibido, **Então** o selo de alertas não aparece.
4. **CA-012** — **Dado** vento de 4,2 m/s vindo de 95°, **Quando** os cards são exibidos em °C, **Então** o card Vento mostra "4 m/s L".
5. **CA-013** — **Dado** visibilidade de 2.500 m, **Quando** os cards são exibidos, **Então** o card Visibilidade mostra "2,5 km".
6. **CA-014** — **Dado** que o provedor não enviou a visibilidade, **Quando** os cards são exibidos, **Então** o card Visibilidade mostra "—" e os demais cards aparecem normalmente.
7. **CA-015** — **Dado** que o código de condição atual é 501, **Quando** o card principal é exibido, **Então** a imagem ilustrativa é a do grupo Chuva.

---

## 3. Previsão diária

### Problema

O usuário quer planejar os próximos dias vendo a temperatura máxima e o tempo previsto para cada um, e detalhar o resumo de um dia específico.

### Atores

| Ator | Descrição | O que pode fazer | O que não pode fazer |
|---|---|---|---|
| Usuário | Pessoa que consulta o dashboard | Ver as abas de dias; selecionar um dia para ver o resumo; voltar para "Hoje" | Ver dias além dos entregues pelo provedor; ver a previsão hora a hora ou por minuto de dias futuros |
| OpenWeatherMap | Provedor da previsão diária | Fornecer o resumo de hoje e dos próximos 7 dias | — |

### Escopo

**Incluso**
- Faixa de abas com "Hoje" e os dias seguintes entregues pelo provedor, com rolagem horizontal.
- Resumo do dia selecionado no card principal e nos seis cards.
- Selo de alertas considerando só os alertas que alcançam o dia selecionado.
- Volta para "Hoje" ao trocar de cidade.

**Não incluso**
- Previsão hora a hora e por minuto de dias futuros.
- Temperaturas por período do dia (manhã, tarde, noite).
- Nascer e pôr do sol, fases da lua.
- Resumo textual do dia gerado pelo provedor.

### Histórias de usuário

- Como usuário, quero ver a máxima e o tempo previstos para cada um dos próximos dias, para planejar a semana.
- Como usuário, quero selecionar um dia, para ver o resumo dele em detalhe.
- Como usuário, quero voltar facilmente para o dia de hoje, para retomar as condições atuais.

### Requisitos funcionais

| ID | Requisito (EARS) |
|---|---|
| RF-024 | O SISTEMA DEVE exibir uma aba para cada dia da previsão diária, começando por hoje, com o rótulo do dia, a temperatura máxima e o ícone da condição. |
| RF-025 | O SISTEMA DEVE iniciar com a aba "Hoje" selecionada e destacar a aba selecionada. |
| RF-026 | QUANDO o usuário selecionar uma aba diferente de "Hoje", O SISTEMA DEVE exibir no card principal a temperatura máxima, a temperatura mínima, a descrição, a sensação térmica diurna e a data do dia. |
| RF-027 | QUANDO o usuário selecionar uma aba diferente de "Hoje", O SISTEMA DEVE exibir nos seis cards os valores previstos para o dia. |
| RF-028 | QUANDO o usuário selecionar a aba "Hoje", O SISTEMA DEVE voltar a exibir as condições atuais no card principal e nos seis cards. |
| RF-029 | ENQUANTO uma aba diferente de "Hoje" estiver selecionada, O SISTEMA DEVE manter a previsão hora a hora e a previsão por minuto referentes ao momento atual. |
| RF-030 | ENQUANTO uma aba diferente de "Hoje" estiver selecionada, O SISTEMA DEVE contar no selo apenas os alertas cuja vigência alcança aquele dia. |
| RF-031 | QUANDO a cidade selecionada mudar, O SISTEMA DEVE selecionar a aba "Hoje". |
| RF-032 | SE as abas não couberem na largura da tela, ENTÃO O SISTEMA DEVE permitir a rolagem horizontal da faixa de abas. |

### Regras de negócio

| ID | Regra |
|---|---|
| RN-026 | "Hoje" é o dia da previsão cuja data, no fuso da cidade, é igual à data atual da cidade. Dias anteriores a ela são descartados. As demais abas seguem em ordem cronológica. |
| RN-027 | A quantidade de abas é o número de dias entregues pelo provedor a partir de hoje, limitado a 8: "Hoje" mais 7. Dias além do oitavo são ignorados. |
| RN-028 | Rótulos: "Hoje" para o dia atual e, para os demais, o dia da semana abreviado em português: Dom, Seg, Ter, Qua, Qui, Sex, Sáb. |
| RN-029 | A temperatura da aba é a máxima do dia, arredondada (RN-014). |
| RN-030 | No card principal, para um dia diferente de "Hoje": temperatura principal = máxima; linha secundária = "Mín. X°"; sensação = sensação térmica diurna; no lugar da hora, a data no formato "Seg, 05/10". |
| RN-031 | Nos seis cards, para um dia diferente de "Hoje": vento, umidade, visibilidade, pressão, índice UV e ponto de orvalho previstos para o dia, nos formatos de RN-019 a RN-024. Um valor que a previsão do dia não traga mostra "—" (P-013). |
| RN-032 | Um alerta alcança um dia quando o intervalo entre o início e o fim do alerta se sobrepõe, por um tempo maior que zero, ao período de 00:00 a 24:00 desse dia, no fuso da cidade. Um alerta sem início ou sem fim conta em todos os dias. |
| RN-033 | A imagem ilustrativa de um dia diferente de "Hoje" é a do grupo da condição prevista para o dia (RN-017). |

### Comportamento em erro e casos de borda

| Cenário | Comportamento esperado | Mensagem ao usuário |
|---|---|---|
| (5) Provedor entrega menos de 8 dias | Só os dias recebidos viram abas. | Nenhuma |
| (5) Resposta sem previsão diária | A faixa de abas mostra só a mensagem. O card principal e os cards continuam com as condições atuais. | "Previsão diária indisponível." |
| (5) Valor de um dia ausente (ex.: ponto de orvalho ou visibilidade) | O card correspondente mostra "—" (P-013). | Nenhuma |
| (5) Alerta sem início ou sem fim informados | Conta em todos os dias (RN-032). | Nenhuma |
| (6) Alerta que termina às 00:00 de um dia | Conta só no dia anterior, porque a interseção com o dia seguinte tem duração zero (RN-032). | Nenhuma |
| (7) Clique repetido na aba já selecionada | Nada muda. Nenhuma consulta. | Nenhuma |
| (7) Troca rápida entre várias abas | A tela mostra sempre a última aba escolhida, sem consulta ao provedor (P-011). | Nenhuma |
| (8) Dados em cache atravessam a meia-noite da cidade | O dia que virou passado é descartado e o dia seguinte passa a ser "Hoje" (RN-026). Pode haver uma aba a menos até a próxima consulta. | Nenhuma |
| (8) Dados atualizados (RF-014) com outro dia selecionado | O mesmo dia continua selecionado se ainda existir. Se tiver virado passado, a seleção volta para "Hoje". | Nenhuma |
| (8) Fuso da cidade diferente do fuso do usuário | "Hoje" e os dias da semana são calculados no fuso da cidade (P-015). | Nenhuma |
| (9) Ícone de uma aba não carrega | Aparece o texto alternativo com a descrição. A temperatura continua visível. | Nenhuma |
| (10) Tela estreita | A faixa de abas rola na horizontal, sem rolagem horizontal da página. A aba selecionada é trazida para a área visível. | Nenhuma |

### Requisitos não-funcionais

| ID | Categoria | Requisito |
|---|---|---|
| RNF-013 | Desempenho | Ao trocar de aba, o card principal e os cards são atualizados em até 100 ms, sem consulta ao provedor. |
| RNF-014 | Acessibilidade | As abas podem ser navegadas pelo teclado (setas esquerda e direita, Enter). A aba selecionada é identificada por estado acessível e por um destaque que não depende só da cor (P-018, P-023). |
| RNF-015 | Responsividade | A faixa de abas tem rolagem horizontal própria e nunca causa rolagem horizontal da página (P-024). |

### Dependências e premissas

**Dependências**
- Previsão diária da One Call API 4.0: até 10 dias por página, dos quais o produto usa até 8.
- Detalhe de cada alerta da One Call API 4.0, com o início e o fim da vigência. A previsão diária não informa os alertas de cada dia.
- Serviço de ícones do OpenWeatherMap.

**Premissas**
- Cada dia da previsão informa a data que ele representa.
- O primeiro dia da previsão pode ser anterior ao dia atual da cidade. Nesse caso, ele é descartado (RN-026).
- A previsão diária traz vento, umidade, pressão, índice UV e ponto de orvalho. A visibilidade pode faltar.

### Critérios de aceite

1. **CA-016** — **Dado** que o provedor entregou 8 dias, **Quando** o dashboard é exibido, **Então** aparecem a aba "Hoje" e mais 7 abas, cada uma com o dia da semana abreviado, a máxima e o ícone.
2. **CA-017** — **Dado** que a aba "Hoje" está selecionada, **Quando** o usuário seleciona "Qui", com máxima de 35,2 °C e mínima de 21,4 °C, **Então** o card principal mostra "35°", "Mín. 21°", a descrição e a data do dia, e, se a previsão do dia não trouxer visibilidade, o card Visibilidade mostra "—".
3. **CA-018** — **Dado** que a aba "Qui" está selecionada, **Quando** o usuário seleciona "Hoje", **Então** o card principal e os cards voltam a mostrar as condições atuais.
4. **CA-019** — **Dado** que a aba "Qui" está selecionada e são 08:18 na cidade, **Quando** o usuário olha a previsão hora a hora, **Então** ela continua começando em "08:00".
5. **CA-020** — **Dado** que a aba "Sex" está selecionada, **Quando** o usuário escolhe outra cidade, **Então** a aba "Hoje" fica selecionada.
6. **CA-021** — **Dado** um único alerta vigente de quarta às 18:00 até quinta às 06:00, **Quando** o usuário seleciona "Qua" e depois "Sex", **Então** o selo mostra "1 alerta" em "Qua" e fica oculto em "Sex".

---

## 4. Previsão hora a hora

### Problema

O usuário quer saber como a temperatura e a chance de chuva vão variar nas próximas horas, para planejar as atividades do dia.

### Atores

| Ator | Descrição | O que pode fazer | O que não pode fazer |
|---|---|---|---|
| Usuário | Pessoa que consulta o dashboard | Ver a curva e os cards das próximas 24 horas; rolar os cards; ver o valor de um ponto da curva | Escolher outra janela de horas; ver horas além das 24 seguintes; ver vento ou umidade por hora |
| OpenWeatherMap | Provedor da previsão hora a hora | Fornecer a previsão por hora a partir da hora atual, em páginas de até 20 horas | — |

### Escopo

**Incluso**
- Janela de 24 horas a partir da hora atual da cidade.
- Curva de temperatura cobrindo a janela inteira.
- Cards por hora com hora, ícone, chance de precipitação e temperatura.
- Etiquetas de volume de chuva sobre a curva, nas horas com chuva.
- Rolagem horizontal dos cards.

**Não incluso**
- Horas além das 24 seguintes.
- Vento, umidade e outros indicadores por hora.
- Volume de neve.
- Seleção de uma hora para ver detalhes no card principal.

### Histórias de usuário

- Como usuário, quero ver a curva de temperatura das próximas 24 horas, para perceber quando vai esquentar ou esfriar.
- Como usuário, quero ver a chance de chuva de cada hora, para escolher o melhor horário para sair.
- Como usuário, quero ver o volume de chuva previsto nas horas chuvosas, para avaliar a intensidade.

### Requisitos funcionais

| ID | Requisito (EARS) |
|---|---|
| RF-033 | O SISTEMA DEVE exibir cards para as próximas 24 horas, a partir da hora atual da cidade, cada um com hora, ícone da condição, chance de precipitação e temperatura. |
| RF-034 | O SISTEMA DEVE exibir uma curva de temperatura que cubra as mesmas horas dos cards. |
| RF-035 | ONDE uma hora tiver volume de chuva previsto, O SISTEMA DEVE exibir sobre a curva, na posição dessa hora, uma etiqueta com o volume em mm/h. |
| RF-036 | QUANDO o usuário passar o cursor ou o foco sobre um ponto da curva, O SISTEMA DEVE exibir a hora, a temperatura e, se houver, o volume de chuva daquele ponto. |
| RF-037 | SE os cards não couberem na largura do bloco, ENTÃO O SISTEMA DEVE permitir a rolagem horizontal dos cards. |
| RF-038 | SE a previsão hora a hora não vier na resposta, ENTÃO O SISTEMA DEVE exibir no bloco a mensagem de indisponibilidade e manter os demais blocos (P-021). |

### Regras de negócio

| ID | Regra |
|---|---|
| RN-034 | A primeira hora da janela é a que contém o momento atual da cidade. Horas que já passaram são descartadas. Se houver menos de 24 horas disponíveis, exibem-se só as disponíveis. |
| RN-035 | A hora aparece no formato "HH:00", no fuso da cidade (ex.: "08:00", "13:00"). Num fuso com meia hora ou 45 minutos, as horas da previsão começam nesses minutos, e o horário os mostra (ex.: "00:45" no Nepal, UTC+05:45; DEF-01, P-015). A primeira hora de um novo dia mostra também o dia da semana abreviado (ex.: "00:00 Sex"). |
| RN-036 | Chance de precipitação = fração de 0 a 1 do provedor × 100, arredondada ao inteiro, com "%" (ex.: 0,21 → "21%"). |
| RN-037 | Etiqueta de chuva = volume de chuva previsto para a hora, em mm/h, com 2 casas decimais (ex.: "0,21 mm/h"). Só aparece quando o valor arredondado é maior que zero. A falta do volume de chuva na resposta significa "sem chuva prevista", não falha. |
| RN-038 | Quando etiquetas ficariam sobrepostas, fica visível só a de maior volume no grupo. As demais aparecem ao passar o cursor ou o foco (RF-036). |
| RN-039 | A escala vertical da curva vai da menor à maior temperatura da janela, com folga para as etiquetas. Se todas as temperaturas forem iguais, a curva é uma linha reta no centro do bloco. |
| RN-040 | As temperaturas dos cards e da curva seguem RN-014, na escala ativa. |

### Comportamento em erro e casos de borda

| Cenário | Comportamento esperado | Mensagem ao usuário |
|---|---|---|
| (5) Resposta sem previsão hora a hora | O bloco mostra só a mensagem. Os demais blocos continuam (RF-038). | "Previsão hora a hora indisponível para esta cidade." |
| (5) Menos de 24 horas disponíveis | Exibe só as horas disponíveis (RN-034). | Nenhuma |
| (5) Chance de precipitação ausente em uma hora | O card mostra "—" no lugar do percentual. | Nenhuma |
| (5) Volume de chuva ausente | Sem etiqueta naquela hora (RN-037). | Nenhuma |
| (6) Todas as temperaturas iguais | A curva é uma linha reta no centro (RN-039). | Nenhuma |
| (6) Volume de chuva muito pequeno (ex.: 0,004) | Arredonda para 0,00 e não gera etiqueta (RN-037). | Nenhuma |
| (6) Chuva em muitas horas seguidas | As etiquetas sobrepostas são agrupadas (RN-038). | Nenhuma |
| (8) Dados em cache com até 10 minutos e uma nova hora começou | A janela começa na hora atual. A hora que passou é descartada (RN-034). | Nenhuma |
| (8) A janela atravessa a meia-noite | O primeiro card do novo dia mostra o dia da semana (RN-035). | Nenhuma |
| (8) Fuso da cidade diferente do fuso do usuário | As horas aparecem no fuso da cidade (P-015). | Nenhuma |
| (9) Ícone não carrega | Aparece o texto alternativo com a descrição. Percentual e temperatura continuam visíveis. | Nenhuma |
| (10) Tela estreita | A curva se ajusta à largura do bloco e os cards rolam na horizontal, sem rolagem horizontal da página. | Nenhuma |

### Requisitos não-funcionais

| ID | Categoria | Requisito |
|---|---|---|
| RNF-016 | Acessibilidade | A curva tem uma alternativa em texto. Exemplo: "Nas próximas 24 horas, mínima de 18° às 05:00 e máxima de 27° às 15:00". |
| RNF-017 | Acessibilidade | Os cards e os pontos da curva podem ser percorridos pelo teclado (P-023). |
| RNF-018 | Desempenho | A curva e os cards aparecem junto com os demais blocos (RNF-001), sem consulta adicional ao provedor. |

### Dependências e premissas

**Dependências**
- Previsão por hora da One Call API 4.0, com temperatura, chance de precipitação, volume de chuva e ícone. O produto pede 2 páginas a partir da hora atual (até 40 horas), o que cobre a janela de 24 horas mesmo com dados em cache.
- Serviço de ícones do OpenWeatherMap.

**Premissas**
- A primeira hora da previsão é a hora atual ou uma hora anterior.
- O volume de chuva de uma hora vem em milímetros e equivale a mm/h.
- A falta do volume de chuva indica que não há chuva prevista naquela hora.

### Critérios de aceite

1. **CA-022** — **Dado** que são 08:18 na cidade, **Quando** o bloco é exibido, **Então** o primeiro card é "08:00", o último é "07:00" do dia seguinte e há 24 cards.
2. **CA-023** — **Dado** que às 13:00 a chance de precipitação é 0,2 e a temperatura é 24,6 °C, **Quando** o bloco é exibido, **Então** o card "13:00" mostra "20%" e "25°".
3. **CA-024** — **Dado** volume de chuva de 0,21 às 13:00 e nenhum nas demais horas, **Quando** o bloco é exibido, **Então** há uma única etiqueta, "0,21 mm/h", na posição das 13:00.
4. **CA-025** — **Dado** que a resposta não trouxe a previsão hora a hora, **Quando** o dashboard é exibido, **Então** o bloco mostra "Previsão hora a hora indisponível para esta cidade." e os demais blocos aparecem normalmente.
5. **CA-026** — **Dado** temperaturas iguais nas 24 horas, **Quando** o bloco é exibido, **Então** a curva é uma linha reta e os 24 cards aparecem.

---

## 5. Previsão por minuto

### Problema

O usuário que vai sair agora quer saber se vai chover na próxima hora e com que intensidade, minuto a minuto.

### Atores

| Ator | Descrição | O que pode fazer | O que não pode fazer |
|---|---|---|---|
| Usuário | Pessoa que consulta o dashboard | Ver as barras, os marcos, a legenda e o resumo; ver o valor de um minuto específico | Ver além de 60 minutos; mudar a unidade de intensidade |
| OpenWeatherMap | Provedor da previsão por minuto | Fornecer a intensidade de precipitação de cada minuto da próxima hora, onde houver cobertura | Garantir a previsão por minuto para todas as localidades |

### Escopo

**Incluso**
- Painel "Previsão por minuto — precipitação", sobreposto ao mapa.
- Uma barra por minuto da próxima hora, a partir do primeiro minuto disponível.
- Cores por faixa de intensidade.
- Marcos "Agora", "15 min", "30 min", "45 min" e "60 min", com horário local.
- Legenda com as 5 faixas.
- Resumo em texto da próxima hora.
- Valor de um minuto ao passar o cursor ou o foco.

**Não incluso**
- Previsão por minuto além de 60 minutos.
- Tipo de precipitação (chuva, neve, granizo).
- Unidade de intensidade diferente de mm/h.

### Histórias de usuário

- Como usuário, quero ver a intensidade da chuva minuto a minuto na próxima hora, para decidir se saio agora ou espero.
- Como usuário, quero uma legenda de cores, para interpretar as barras.
- Como usuário, quero um resumo em texto, para entender a previsão sem analisar o gráfico.

### Requisitos funcionais

| ID | Requisito (EARS) |
|---|---|
| RF-039 | O SISTEMA DEVE exibir uma barra para cada minuto da previsão da próxima hora, a partir do primeiro minuto que ainda não passou. |
| RF-040 | O SISTEMA DEVE colorir cada barra conforme a faixa de intensidade de precipitação do minuto. |
| RF-041 | O SISTEMA DEVE exibir marcos com rótulo e horário local em "Agora", "15 min", "30 min", "45 min" e "60 min". |
| RF-042 | O SISTEMA DEVE exibir uma legenda com as cinco faixas de intensidade e suas cores. |
| RF-043 | O SISTEMA DEVE exibir um resumo em texto da precipitação prevista para a próxima hora. |
| RF-044 | QUANDO o usuário passar o cursor ou o foco sobre uma barra, O SISTEMA DEVE exibir o horário e a intensidade daquele minuto. |
| RF-045 | SE a previsão por minuto não estiver disponível para a cidade, ENTÃO O SISTEMA DEVE exibir no painel a mensagem de indisponibilidade no lugar das barras, da legenda e do resumo. |

### Regras de negócio

| ID | Regra |
|---|---|
| RN-041 | Faixas de intensidade (p, em mm/h), com o limite superior incluído na faixa: p = 0 → cinza, "0 mm/h"; 0 < p ≤ 0,5 → verde, "até 0,5 mm/h"; 0,5 < p ≤ 2,5 → verde-escuro, "0,5 a 2,5 mm/h"; 2,5 < p ≤ 7,5 → amarelo, "2,5 a 7,5 mm/h"; p > 7,5 → vermelho, "acima de 7,5 mm/h". Os textos entre aspas são os da legenda. |
| RN-042 | A altura da barra é proporcional à intensidade, com teto visual em 10 mm/h: valores maiores ocupam a altura máxima. Intensidade 0 tem uma altura mínima visível. |
| RN-043 | Os marcos correspondem aos minutos 0, 15, 30, 45 e 60 a partir do primeiro minuto da janela, cada um com o horário HH:MM no fuso da cidade (RN-015). O minuto 0 tem o rótulo "Agora". Cada marco fica no início do seu minuto, e o de 60 min fica no fim da última barra. |
| RN-044 | Resumo: sem chuva em nenhum minuto → "Sem chuva prevista na próxima hora."; chuva só a partir de um minuto futuro → "Chuva prevista a partir de HH:MM."; chuva agora que para antes do fim → "Chuva agora, parando por volta de HH:MM."; chuva em todos os minutos → "Chuva durante toda a próxima hora.". "Chuva" quer dizer intensidade maior que 0. |
| RN-045 | O valor exibido no cursor ou no foco tem o formato "HH:MM — X,XX mm/h". |
| RN-046 | A intensidade é sempre exibida em mm/h, qualquer que seja a escala ativa (feature 7). |
| RN-047 | Minutos que já passaram são descartados. O marco de k minutos só aparece quando há pelo menos k barras depois do descarte (o de "Agora", com pelo menos 1). Um valor negativo ou não numérico conta como ausente: a barra não é desenhada e o cursor mostra "—". |

### Comportamento em erro e casos de borda

| Cenário | Comportamento esperado | Mensagem ao usuário |
|---|---|---|
| (5) Localidade sem cobertura de previsão por minuto | O painel mostra só a mensagem. O mapa continua (RF-045). | "Previsão por minuto indisponível para esta localidade." |
| (5) Minuto ausente no meio da série | Um espaço vazio fica no lugar da barra e o cursor mostra "—" (RN-047). | Nenhuma |
| (5) Valor negativo ou não numérico | Tratado como ausente (RN-047). | Nenhuma |
| (6) Todos os minutos com intensidade 0 | Todas as barras ficam cinza, com a altura mínima. | "Sem chuva prevista na próxima hora." |
| (6) Intensidade exatamente 0,5, 2,5 ou 7,5 | Cores verde, verde-escuro e amarelo, respectivamente (RN-041). | Nenhuma |
| (6) Intensidade acima de 10 mm/h | A barra fica vermelha, com a altura máxima. O cursor mostra o valor real (RN-042). | Nenhuma |
| (8) Dados em cache com alguns minutos | Começa no primeiro minuto que ainda não passou, com menos de 60 barras. Os marcos sem barras suficientes não aparecem (RN-047). | Nenhuma |
| (8) Fuso da cidade diferente do fuso do usuário | Os horários dos marcos aparecem no fuso da cidade (P-015). | Nenhuma |
| (7) Usuário alterna °C/°F | O painel não muda (RN-046). | Nenhuma |
| (10) Tela com menos de 600 px | O painel aparece abaixo do mapa, não sobreposto. As barras ficam mais finas, sem rolagem horizontal. | Nenhuma |

### Requisitos não-funcionais

| ID | Categoria | Requisito |
|---|---|---|
| RNF-019 | Acessibilidade | A legenda em texto e o resumo permitem entender a previsão sem depender da cor (P-018). As cores das barras têm contraste mínimo de 3:1 com o fundo do painel (WCAG 2.1, critério 1.4.11). |
| RNF-020 | Acessibilidade | O gráfico de barras é um único elemento focável. As setas esquerda e direita percorrem os minutos e anunciam o valor de cada um (P-023). |
| RNF-021 | Responsividade | Em telas com 600 px ou mais, o painel fica sobreposto ao canto inferior esquerdo do mapa. Abaixo disso, fica abaixo do mapa. |

### Dependências e premissas

**Dependências**
- Previsão por minuto da One Call API 4.0: até 60 minutos, a partir do minuto seguinte ao da consulta.

**Premissas**
- A intensidade vem em mm/h.
- O primeiro item da previsão por minuto é o minuto seguinte ao da consulta.
- Quando o provedor não tem a previsão por minuto da localidade (resposta sem dados ou "não encontrado"), trata-se de falta de cobertura, não de falha.

### Critérios de aceite

1. **CA-027** — **Dado** minutos com intensidades 0; 0,3; 1,0; 5,0 e 8,0, **Quando** o painel é exibido, **Então** as barras desses minutos ficam cinza, verde, verde-escuro, amarelo e vermelho, e a legenda mostra as 5 faixas.
2. **CA-028** — **Dado** minutos com intensidade exatamente 0,5; 2,5 e 7,5, **Quando** o painel é exibido, **Então** as barras ficam verde, verde-escuro e amarelo.
3. **CA-029** — **Dado** que a previsão por minuto começa às 08:18 no horário da cidade, **Quando** o painel é exibido, **Então** os marcos são "Agora 08:18", "15 min 08:33", "30 min 08:48", "45 min 09:03" e "60 min 09:18".
4. **CA-030** — **Dado** que todas as intensidades são 0, **Quando** o painel é exibido, **Então** todas as barras ficam cinza e o resumo é "Sem chuva prevista na próxima hora.".
5. **CA-031** — **Dado** chuva só a partir das 08:38, **Quando** o painel é exibido, **Então** o resumo é "Chuva prevista a partir de 08:38.".
6. **CA-032** — **Dado** que o provedor não enviou a previsão por minuto, **Quando** o dashboard é exibido, **Então** o painel mostra "Previsão por minuto indisponível para esta localidade." e o mapa continua visível.

---

## 6. Mapa de precipitação

### Problema

O usuário quer ver onde está chovendo ao redor da cidade, para entender se a chuva está chegando ou se afastando.

### Atores

| Ator | Descrição | O que pode fazer | O que não pode fazer |
|---|---|---|---|
| Usuário | Pessoa que consulta o dashboard | Ver o mapa com o marcador e a camada de chuva; aproximar, afastar e arrastar o mapa | Escolher uma cidade clicando no mapa; trocar a camada; animar a evolução da chuva |
| OpenWeatherMap | Provedor da camada de precipitação | Fornecer a imagem da precipitação atual por área do mapa | — |
| Provedor de mapa base | Provedor do mapa geográfico, definido em [arquitetura.md](arquitetura.md) (ADR-006) | Fornecer o mapa base | Ser exibido sem a atribuição exigida (P-019) |

### Escopo

**Incluso**
- Mapa centralizado na cidade selecionada, com marcador e rótulo.
- Camada de precipitação semitransparente sobre o mapa base.
- Aproximar, afastar e arrastar.
- Atribuições dos provedores.
- Painel de previsão por minuto sobreposto (feature 5).
- Recentralização ao trocar de cidade.

**Não incluso**
- Outras camadas (temperatura, vento, nuvens).
- Animação ou histórico da precipitação.
- Escolha de cidade pelo mapa.
- Botão para recentralizar e modo de tela cheia.
- Legenda própria da camada de precipitação do mapa. A legenda do painel refere-se às barras da previsão por minuto.

### Histórias de usuário

- Como usuário, quero ver a chuva no mapa ao redor da cidade, para saber se ela está chegando.
- Como usuário, quero aproximar e arrastar o mapa, para explorar a região.
- Como usuário, quero que o mapa acompanhe a cidade escolhida, para não precisar procurá-la.

### Requisitos funcionais

| ID | Requisito (EARS) |
|---|---|
| RF-046 | O SISTEMA DEVE exibir um mapa centralizado nas coordenadas da cidade selecionada, com um marcador e um rótulo com o nome da cidade. |
| RF-047 | O SISTEMA DEVE sobrepor ao mapa base a camada de precipitação, de forma semitransparente. |
| RF-048 | QUANDO a cidade selecionada mudar, O SISTEMA DEVE recentralizar o mapa na nova cidade, mover o marcador e restaurar o zoom inicial. |
| RF-049 | O SISTEMA DEVE permitir aproximar, afastar e arrastar o mapa por mouse, toque e teclado. |
| RF-050 | O SISTEMA DEVE exibir as atribuições do mapa base e dos dados de precipitação (P-019). |
| RF-051 | SE o mapa base não puder ser carregado, ENTÃO O SISTEMA DEVE exibir no bloco a mensagem de indisponibilidade e manter visível o painel de previsão por minuto. |
| RF-052 | SE a camada de precipitação não puder ser carregada, ENTÃO O SISTEMA DEVE manter o mapa base e o marcador e informar que a camada de chuva está indisponível. |

### Regras de negócio

| ID | Regra |
|---|---|
| RN-048 | O zoom inicial é 6 (escala regional, com centenas de quilômetros visíveis). O zoom permitido vai de 3 a 10. |
| RN-049 | A camada de precipitação mostra a precipitação atual, não uma previsão. Ela é parcialmente transparente, para deixar o mapa base legível. |
| RN-050 | O rótulo do marcador é o nome da cidade no formato de RN-006, sem o país. Se a cidade veio da localização sem nome, o rótulo é "Sua localização". |
| RN-051 | Interagir com o mapa não muda a cidade selecionada nem gera consulta de clima. |
| RN-052 | Em telas de toque, um dedo rola a página e dois dedos movem o mapa. |

### Comportamento em erro e casos de borda

| Cenário | Comportamento esperado | Mensagem ao usuário |
|---|---|---|
| (3) Cota da camada de precipitação excedida ou acesso recusado | Mapa base e marcador continuam visíveis, com uma faixa informativa sobre o mapa (RF-052). | "Camada de chuva indisponível no momento." |
| (4) Mapa base fora do ar | O bloco mostra só a mensagem. O painel de previsão por minuto continua (RF-051). | "Mapa indisponível no momento." |
| (4) Camada de precipitação fora do ar | Igual à cota excedida (RF-052). | "Camada de chuva indisponível no momento." |
| (6) Sem chuva na região visível | A camada fica transparente e só o mapa base aparece. | Nenhuma |
| (6) Usuário tenta aproximar ou afastar além dos limites | O zoom para no limite de 3 ou 10 (RN-048). | Nenhuma |
| (7) Usuário arrasta e aproxima o mapa várias vezes | Nenhuma consulta de clima e nenhuma mudança de cidade (RN-051). | Nenhuma |
| (7) Usuário arrasta o mapa para longe e depois troca de cidade | O mapa recentraliza na nova cidade (RF-048). | Nenhuma |
| (8) Cidade selecionada vem da localização do usuário | O marcador fica nas coordenadas informadas pelo navegador. Elas são usadas só para o mapa e o clima (P-008). | Nenhuma |
| (9) Algumas partes do mapa não carregam | Essas áreas ficam em branco e o restante do mapa funciona. | Nenhuma |
| (10) Usuário passa o dedo sobre o mapa para rolar a página no celular | A página rola. O mapa só se move com dois dedos (RN-052). | "Use dois dedos para mover o mapa." |
| (10) Tela com menos de 600 px | O mapa ocupa a largura disponível, com altura mínima de 300 px. O painel de previsão por minuto fica abaixo dele (RNF-021). | Nenhuma |

### Requisitos não-funcionais

| ID | Categoria | Requisito |
|---|---|---|
| RNF-022 | Desempenho | Com os provedores respondendo normalmente, o mapa base e a camada aparecem em até 3 s. O carregamento do mapa não atrasa os demais blocos (P-021). |
| RNF-023 | Custo e cota | Só são carregadas as partes do mapa e da camada que estão na área visível. |
| RNF-024 | Acessibilidade | O mapa tem descrição em texto (ex.: "Mapa de precipitação centrado em Uberlândia") e controles de zoom acessíveis pelo teclado (P-023). |
| RNF-025 | Conformidade | As atribuições ficam sempre visíveis, sem sobreposição do painel de previsão por minuto (P-019). |

### Dependências e premissas

**Dependências**
- Camada de precipitação do OpenWeatherMap.
- Provedor de mapa base, definido em [arquitetura.md](arquitetura.md) (ADR-006), com licença compatível com uso acadêmico.
- Chave de API válida (para a camada de precipitação).

**Premissas**
- A camada de precipitação está incluída no plano gratuito do OpenWeatherMap.
- O provedor de mapa base permite uso gratuito mediante atribuição.

### Critérios de aceite

1. **CA-033** — **Dado** que a cidade selecionada é Uberlândia, **Quando** o mapa é exibido, **Então** ele está centralizado em Uberlândia, com o marcador "Uberlândia" e zoom 6.
2. **CA-034** — **Dado** que o mapa mostra Uberlândia, **Quando** o usuário seleciona Curitiba, **Então** o mapa recentraliza em Curitiba e o marcador mostra "Curitiba".
3. **CA-035** — **Dado** que a camada de precipitação falha, **Quando** o mapa é exibido, **Então** o mapa base e o marcador continuam visíveis e aparece "Camada de chuva indisponível no momento.".
4. **CA-036** — **Dado** que o mapa base falha, **Quando** o dashboard é exibido, **Então** o bloco mostra "Mapa indisponível no momento." e o painel de previsão por minuto continua visível.
5. **CA-037** — **Dado** que o mapa está exibido, **Quando** o usuário arrasta e aproxima o mapa, **Então** nenhuma nova consulta de clima é feita e a cidade selecionada não muda.
6. **CA-038** — **Dado** que o mapa está exibido com o painel de previsão por minuto, **Quando** o usuário observa o bloco, **Então** as atribuições dos provedores estão visíveis e não ficam cobertas pelo painel.

---

## 7. Alternância de unidades

### Problema

Usuários acostumados com Fahrenheit e milhas por hora precisam ler os valores na escala que conhecem, sem esperar nova carga de dados.

### Atores

| Ator | Descrição | O que pode fazer | O que não pode fazer |
|---|---|---|---|
| Usuário | Pessoa que consulta o dashboard | Alternar entre °C e °F | Escolher unidades separadas para temperatura e vento; mudar as unidades de pressão, visibilidade ou precipitação |

### Escopo

**Incluso**
- Seletor °C/°F no cabeçalho, iniciando em °C.
- Conversão de todas as temperaturas e da velocidade do vento (m/s ↔ mph), sem consulta ao provedor.
- Escala mantida ao trocar de cidade ou de aba.

**Não incluso**
- Lembrar a escala escolhida entre visitas.
- Outras unidades (inHg, milhas, polegadas por hora).
- Unidades independentes para temperatura e vento.

### Histórias de usuário

- Como usuário, quero alternar entre °C e °F, para ler as temperaturas na escala que conheço.
- Como usuário, quero que a unidade do vento acompanhe a escala escolhida, para manter um padrão de unidades.
- Como usuário, quero que a troca seja imediata, para comparar as escalas sem esperar.

### Requisitos funcionais

| ID | Requisito (EARS) |
|---|---|
| RF-053 | O SISTEMA DEVE exibir no cabeçalho um seletor com as opções °C e °F, destacando a escala ativa. |
| RF-054 | O SISTEMA DEVE iniciar com a escala °C ativa. |
| RF-055 | QUANDO o usuário escolher a outra escala, O SISTEMA DEVE converter todas as temperaturas exibidas e a velocidade do vento, sem consultar o provedor (P-011). |
| RF-056 | O SISTEMA DEVE exibir a velocidade do vento em m/s com a escala °C e em mph com a escala °F. |
| RF-057 | QUANDO a cidade selecionada ou a aba de dia mudar, O SISTEMA DEVE manter a escala ativa. |
| RF-058 | QUANDO novos dados chegarem do provedor, O SISTEMA DEVE exibi-los já na escala ativa. |

### Regras de negócio

| ID | Regra |
|---|---|
| RN-053 | °F = °C × 9/5 + 32. |
| RN-054 | mph = m/s × 2,23694. |
| RN-055 | A conversão parte sempre do valor original recebido do provedor, e o arredondamento acontece só na exibição (P-014). Exemplo: 20,4 °C → 68,72 °F → "69°". |
| RN-056 | Valores convertidos: temperatura atual, sensação térmica, máxima e mínima (card principal e abas), temperaturas por hora (cards e curva), ponto de orvalho e velocidade do vento (atual e diária). |
| RN-057 | Valores que não mudam: umidade (%), pressão (hPa), visibilidade (km), índice UV, chance de precipitação (%) e intensidade e volume de chuva (mm/h). |
| RN-058 | A escala escolhida vale só enquanto a página estiver aberta. Ao recarregar, volta a ser °C. |
| RN-059 | A consulta ao provedor usa sempre o sistema métrico. A escala do usuário afeta só a exibição. |

### Comportamento em erro e casos de borda

| Cenário | Comportamento esperado | Mensagem ao usuário |
|---|---|---|
| (5) Valor ausente ("—") | Continua "—" nas duas escalas. | Nenhuma |
| (6) Temperatura de -40 °C | Exibe "-40°" nas duas escalas. | Nenhuma |
| (6) Temperatura de -17,8 °C convertida para °F (-0,04 °F) | Exibe "0°", nunca "-0°" (RN-025). | Nenhuma |
| (6) Vento calmo | "Calmo" nas duas escalas, porque a regra usa o valor original (RN-019). | Nenhuma |
| (7) Usuário alterna várias vezes e volta à escala original | Os valores são idênticos aos iniciais, sem erro acumulado (RN-055). | Nenhuma |
| (7) Clique na escala já ativa | Nada muda. | Nenhuma |
| (7) Usuário alterna durante o carregamento de uma cidade | A escala muda na hora. Os dados chegam já na nova escala (RF-058), sem consulta adicional. | Nenhuma |
| (8) Usuário recarrega a página com °F ativo | A página volta para °C (RN-058). | Nenhuma |
| (10) Valores com mais dígitos em °F (ex.: "104°") | O layout acomoda 3 dígitos e sinal negativo sem cortar nem quebrar. | Nenhuma |

### Requisitos não-funcionais

| ID | Categoria | Requisito |
|---|---|---|
| RNF-026 | Desempenho | Todos os blocos mostram a nova escala em até 100 ms após a escolha. |
| RNF-027 | Custo e cota | Alternar a escala gera zero consultas ao provedor (P-011). |
| RNF-028 | Acessibilidade | O seletor pode ser operado pelo teclado e informa a escala ativa por estado acessível, não só pela cor (P-018, P-023). |
| RNF-029 | Consistência | Em qualquer momento, todos os blocos usam a mesma escala. |

### Dependências e premissas

**Dependências**
- Nenhuma dependência externa nova. A feature usa os dados já recebidos nas features 1 a 4.

**Premissas**
- O provedor devolve temperaturas em °C e vento em m/s quando a consulta pede o sistema métrico.

### Critérios de aceite

1. **CA-039** — **Dado** a escala °C e temperatura atual de 20,4 °C, **Quando** o usuário escolhe °F, **Então** o card principal mostra "69°" e nenhuma consulta é feita ao provedor.
2. **CA-040** — **Dado** vento de 4,2 m/s, **Quando** o usuário escolhe °F, **Então** o card Vento mostra "9 mph".
3. **CA-041** — **Dado** a escala °F ativa, **Quando** o usuário escolhe outra cidade, **Então** os dados da nova cidade aparecem em °F e mph.
4. **CA-042** — **Dado** temperatura atual de 20,4 °C, **Quando** o usuário alterna a escala 10 vezes e termina em °C, **Então** o card principal mostra "20°".
5. **CA-043** — **Dado** umidade de 94%, pressão de 1015 hPa e visibilidade de 10 km, **Quando** o usuário escolhe °F, **Então** esses valores não mudam.
6. **CA-044** — **Dado** a escala °F ativa, **Quando** a página é recarregada, **Então** a escala ativa é °C.
