/**
 * Catálogo dos textos fixos da interface (arquitetura, seção 7.3; RNF-008, P-022).
 *
 * Os textos são copiados literalmente do spec: tabelas "Comportamento em erro e casos de
 * borda", requisitos e regras de negócio de cada feature. Textos que dependem de dados
 * (cidades, horas, valores) vêm prontos do backend. Nenhum outro módulo escreve texto fixo
 * de interface (guardrail 10).
 */

/** Congela o objeto e os objetos aninhados: o catálogo não muda em tempo de execução. */
function deepFreeze(object) {
  for (const value of Object.values(object)) {
    if (value && typeof value === 'object') deepFreeze(value);
  }
  return Object.freeze(object);
}

export const MESSAGES = deepFreeze({
  // Estados dos blocos de dados (feature 1: RF-005, RF-013, RF-014, RN-012).
  // "Carregando…" não está no spec: é o nome do indicador para leitores de tela (D-17).
  loading: 'Carregando…',
  stillLoading: 'Ainda carregando…',
  refreshing: 'Atualizando…',
  retry: 'Tentar novamente',

  // Falhas da consulta de clima, por código da seção 6.4 (feature 1, categorias 3 e 4).
  errors: {
    provider_unauthorized: 'O serviço de clima recusou o acesso. Tente novamente mais tarde.',
    provider_rate_limited:
      'Limite de consultas ao serviço de clima atingido. Tente novamente em alguns minutos.',
    provider_unavailable: 'O serviço de clima está indisponível no momento.',
    server_unreachable: 'O serviço de clima está indisponível no momento.',
    invalid_request: 'O serviço de clima está indisponível no momento.',
    provider_timeout: 'O serviço de clima demorou para responder.',
    network_unavailable: 'Sem conexão com a internet. Verifique sua rede e tente novamente.',
  },

  // Cabeçalho (feature 7: RF-053). O título vem do print de referência, e o nome do grupo do
  // seletor não está no spec: é o nome para leitores de tela (D-19).
  header: {
    title: 'Previsão do tempo',
    scaleGroup: 'Escala de temperatura',
    scales: { c: '°C', f: '°F' },
  },

  // Cidade padrão e localização (feature 1: RN-001, RN-002, RN-009, categoria 2). O nome do
  // botão que fecha o aviso não está no spec: é o nome para leitores de tela (D-20).
  defaultCity: { headerLabel: 'Uberlândia, BR', markerLabel: 'Uberlândia' },
  location: {
    notice:
      'Não foi possível usar sua localização. Mostrando Uberlândia, BR. ' +
      'Use a busca para escolher outra cidade.',
    unnamed: 'Sua localização',
    closeNotice: 'Fechar aviso',
  },

  // Busca de cidade (feature 1: RNF-007, categoria 1 e 4). Os nomes da lupa e da lista não
  // estão no spec: são os nomes para leitores de tela (D-19).
  search: {
    label: 'Buscar cidade',
    button: 'Buscar',
    results: 'Cidades encontradas',
    empty: 'Digite o nome de uma cidade.',
    tooShort: 'Digite pelo menos 2 caracteres.',
    noResults: (term) => `Nenhuma cidade encontrada para "${term}". Verifique a grafia.`,
    truncated:
      'Mostrando as 5 primeiras cidades. Inclua o estado ou o país para refinar ' +
      '(ex.: Santa Maria, BR).',
    failed: 'Não foi possível buscar cidades agora. Tente novamente.',
  },

  // Condições atuais (feature 2: RF-020). O nome do bloco é o título da feature 2 no spec e
  // serve aos leitores de tela (D-21).
  current: {
    label: 'Condições atuais',
  },
  indicators: {
    wind: 'Vento',
    humidity: 'Umidade',
    visibility: 'Visibilidade',
    pressure: 'Pressão',
    uvi: 'Índice UV',
    dewPoint: 'Ponto de orvalho',
  },

  // Previsão diária (feature 3: RN-028, categoria 5). O nome da faixa de abas não está no
  // spec: é o nome para leitores de tela (D-22).
  daily: {
    label: 'Dias da previsão',
    today: 'Hoje',
    unavailable: 'Previsão diária indisponível.',
  },

  // Previsão hora a hora (feature 4: RNF-016, RF-036, categoria 5). O spec dá o texto
  // alternativo da curva só para 24 horas com mínima e máxima diferentes; o período com menos
  // horas e a temperatura estável seguem o mesmo modelo (D-23).
  hourly: {
    title: 'Previsão hora a hora',
    unavailable: 'Previsão hora a hora indisponível para esta cidade.',
    period: (hours) => (hours === 1 ? 'Na próxima hora' : `Nas próximas ${hours} horas`),
    altText: (period, min, minAt, max, maxAt) =>
      `${period}, mínima de ${min} às ${minAt} e máxima de ${max} às ${maxAt}`,
    steadyText: (period, temp) => `${period}, temperatura estável em ${temp}`,
    // Ponto da curva: hora, temperatura e, se houver, o volume de chuva (RF-036).
    point: (hour, temp, rain) => [hour, temp, rain].filter(Boolean).join(' · '),
  },

  // Previsão por minuto (feature 5: RF-041, RN-041, RN-044, RN-045, RN-047, categoria 5).
  minutely: {
    title: 'Previsão por minuto — precipitação',
    unavailable: 'Previsão por minuto indisponível para esta localidade.',
    marks: ['Agora', '15 min', '30 min', '45 min', '60 min'],
    // Valor do cursor de um minuto que falta na série, igual ao do backend (RN-045, RN-047).
    missingTooltip: (time) => `${time} — —`,
    legend: {
      none: '0 mm/h',
      light: 'até 0,5 mm/h',
      moderate: '0,5 a 2,5 mm/h',
      heavy: '2,5 a 7,5 mm/h',
      extreme: 'acima de 7,5 mm/h',
    },
    summary: {
      dry: 'Sem chuva prevista na próxima hora.',
      startsAt: (time) => `Chuva prevista a partir de ${time}.`,
      stopsAt: (time) => `Chuva agora, parando por volta de ${time}.`,
      allHour: 'Chuva durante toda a próxima hora.',
    },
  },

  // Mapa de precipitação (feature 6: RNF-024, categorias 3, 4 e 10).
  map: {
    label: (place) => `Mapa de precipitação centrado em ${place}`,
    unavailable: 'Mapa indisponível no momento.',
    rainUnavailable: 'Camada de chuva indisponível no momento.',
    twoFingers: 'Use dois dedos para mover o mapa.',
  },
});

/**
 * Mensagem do spec para um código de erro da consulta de clima (seção 7.3; RNF-008, P-004).
 * Um código desconhecido ou ausente nunca é exibido: vira a mensagem genérica.
 * @param {string | null | undefined} code
 * @returns {string}
 */
export function weatherErrorMessage(code) {
  return Object.hasOwn(MESSAGES.errors, code ?? '')
    ? MESSAGES.errors[code]
    : MESSAGES.errors.provider_unavailable;
}
