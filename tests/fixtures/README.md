# Fixtures de teste

Respostas do OpenWeatherMap usadas nos testes, sem internet e sem cota (seção 9.2 de `docs/arquitetura.md`).

**Regras:**
- Só cidades públicas, nunca a localização real de alguém (P-006).
- Nenhuma fixture contém a chave nem o parâmetro `appid` (P-001). O teste `tests/unit/test_fixtures.py` confere o `appid`, e a definição de pronto confere o valor da chave com `git grep`.
- Cada variante editada tem a origem e a alteração descritas aqui.

## Capturas reais

As chamadas abaixo foram feitas uma única vez, com a chave lida do `.env` e acrescentada como `appid` (omitido aqui). As respostas foram salvas em JSON indentado com 2 espaços e UTF-8. As coordenadas estão arredondadas a 2 casas, como o app pede (RN-010).

**Única alteração:** os campos `next` e `prev` das respostas da One Call 4.0 foram removidos, porque trazem a URL de paginação com a chave (ADR-013).

**Data da captura:** 2026-10-05, 19:41 UTC (16:41 em Uberlândia e 04:41 do dia 06/10 em Tóquio). `{start}` = `1791226800` (19:00 UTC).

### One Call 4.0 (uma pasta por cidade, um arquivo por endpoint)

Base: `https://api.openweathermap.org/data/4.0/onecall/`. Todas as chamadas usam `units=metric&lang=pt_br`. `{start}` é a hora UTC cheia do momento da captura, em Unix.

| Arquivo | Chamada | Cobre |
|---|---|---|
| `onecall4/uberlandia/current.json` | `current?lat=-18.92&lon=-48.28` | Dados atuais da cidade padrão |
| `onecall4/uberlandia/1min.json` | `timeline/1min?lat=-18.92&lon=-48.28` | Previsão por minuto |
| `onecall4/uberlandia/1h_p1.json` | `timeline/1h?lat=-18.92&lon=-48.28&start={start}` | Previsão por hora, 1ª página |
| `onecall4/uberlandia/1h_p2.json` | `timeline/1h?lat=-18.92&lon=-48.28&start={start + 72000}` | Previsão por hora, 2ª página (+20 h) |
| `onecall4/uberlandia/1day.json` | `timeline/1day?lat=-18.92&lon=-48.28` | Previsão diária |
| `onecall4/uberlandia/alert_1.json` a `alert_3.json` | `alert/{id}`, um para cada ID distinto nas listas `alerts` acima (o ID vai codificado na URL) | Detalhe dos 3 alertas de vento do INMET ativos na captura, com início e fim |
| `onecall4/tokyo/*.json` | As mesmas 5 chamadas, com `lat=35.68&lon=139.69` | Fuso diferente do usuário (categoria 8 do spec). Sem alertas na captura |

### Geocoding

| Arquivo | Chamada | Cobre |
|---|---|---|
| `geo_direct_santa_maria.json` | `GET https://api.openweathermap.org/geo/1.0/direct?q=Santa Maria&limit=5` | Busca com várias cidades homônimas (feature 1) |
| `geo_direct_empty.json` | `GET https://api.openweathermap.org/geo/1.0/direct?q=Xqzwvy&limit=5` | Busca sem resultados (feature 1) |
| `geo_reverse_uberlandia.json` | `GET https://api.openweathermap.org/geo/1.0/reverse?lat=-18.92&lon=-48.28&limit=1` | Geocodificação reversa da localização (feature 1) |

### O que as capturas mostraram sobre a documentação da 4.0

| Ponto | O que a captura mostrou |
|---|---|
| Idioma e unidades | Descrições em pt-BR (ex.: "chuva leve", "céu limpo") e temperaturas em °C com `units=metric` |
| `timezone_offset` | Presente em todas as respostas: -10800 em Uberlândia e 32400 em Tóquio |
| `timeline/1min` | 60 registros, alinhados ao minuto. **O primeiro é o minuto seguinte ao da consulta** (19:42:00 numa consulta às 19:41:05), não o minuto atual |
| `timeline/1h` | 20 registros por página. Com `start` na hora UTC cheia, o primeiro é a hora atual (19:00). A 2ª página (`start` + 20 h) continua sem buraco nem repetição: 40 horas no total |
| `timeline/1day` | 10 registros. **O `dt` de cada dia é 00:00 UTC da data que ele representa**, o mesmo nas duas cidades. Em Uberlândia, `dt + timezone_offset` cai às 21:00 do dia anterior, mas o `sunrise` do registro é do próprio dia. O primeiro dia é a data UTC atual, que em Tóquio já era "ontem" no horário local |
| `timeline/1day`: `visibility` | **Ausente** nas duas cidades |
| `timeline/1day`: `alerts` | **Ausente**, mesmo com 3 alertas ativos em Uberlândia. Os IDs aparecem só em `current`, `timeline/1min` e `timeline/1h` |
| `current.alerts` | Lista **também alertas futuros**: o `alert_1` começa às 00:00 do dia seguinte. Funciona como a lista de alertas da 3.0 |
| `alert/{id}` | Campos `id`, `sender_name`, `event` (vazio nos 3), `start`, `end`, `description` (lista por idioma) e `tags` |
| 404 sem cobertura | Não verificado: as duas cidades têm previsão por minuto. O cliente trata 404 e lista vazia do mesmo jeito (ADR-013) |

## Exemplo do contrato

`weather_view_example.json` é o exemplo de `WeatherView` da seção 6.3 da arquitetura, copiado sem alteração. Os testes conferem que os modelos e o view model reproduzem esse contrato.

## Variantes editadas

Pacotes no formato da seção 6.2 da arquitetura, criados na T-3.1. **Origem comum:** o pacote de Uberlândia montado por `merge_onecall` com as 5 capturas e os 3 detalhes de alerta acima. Cada arquivo parte de uma cópia desse pacote e recebe só a alteração descrita. Foram salvos em JSON indentado com 2 espaços e UTF-8.

| Arquivo | Alteração | Cobre |
|---|---|---|
| `onecall_no_minutely.json` | Sem o bloco `minutely` | RF-045, CA-032 |
| `onecall_partial.json` | Sem os blocos `hourly` e `daily`. Em `current`, sem `visibility`, `feels_like`, `dew_point` e `wind_deg` | RF-023, RF-038, CA-014, CA-025 |
| `onecall_alerts.json` | `current.alerts` = `urn:oid:teste.a` e `urn:oid:teste.b`, e `alerts` com as vigências abaixo, no fuso de Uberlândia (-10800). As listas `alerts` dos registros por minuto e por hora foram retiradas, para não sobrar ID real | CA-010, CA-021, RN-032 |
| `onecall_minutely_bands.json` | `precipitation` dos 11 primeiros minutos = 0; 0,3; 0,5; 1,0; 2,5; 5,0; 7,5; 8,0; 12; -1 e ausente (campo retirado). Os demais minutos ficam como na captura | CA-027, CA-028, RN-041, RN-047 |

Vigências de `onecall_alerts.json` (a captura é de segunda, 05/10/2026):

| ID | Início | Fim | Para que serve |
|---|---|---|---|
| `urn:oid:teste.a` | quarta 07/10, 18:00 | quinta 08/10, 06:00 | CA-021: conta em "Qua" e "Qui", não em "Sex" |
| `urn:oid:teste.b` | terça 06/10, 12:00 | quarta 07/10, 00:00 | RN-032: termina às 00:00 e conta só na terça |
