/**
 * Condições atuais (arquitetura, seção 5.1; feature 2): card principal e os seis indicadores.
 * Com uma aba de dia diferente de "Hoje" selecionada, mostra o resumo desse dia (feature 3).
 *
 * Usa a estrutura do `index.html` e preenche os textos pelo `messages.js` e pelo view model.
 * Os valores chegam prontos do backend, nas duas escalas: aqui só se escolhe o texto da escala
 * ativa (ADR-004, guardrail 8). A ilustração de cada grupo de condição fica no CSS, pelo
 * `data-condition` do card (ADR-012). O dia ativo sai de `logic/time-window.js`, com o
 * relógio do navegador, como nas abas (`ui/day-tabs.js`).
 */

import { retry } from '../actions.js';
import { activeDay, visibleDays } from '../logic/time-window.js';
import { MESSAGES } from '../messages.js';
import { getState, subscribe } from '../state.js';
import { blockState, renderBlockState, setConditionIcon, setText } from './dom.js';

// Rótulo de cada indicador, pela chave do view model (RF-020).
const INDICATOR_LABELS = {
  wind: MESSAGES.indicators.wind,
  humidity: MESSAGES.indicators.humidity,
  visibility: MESSAGES.indicators.visibility,
  pressure: MESSAGES.indicators.pressure,
  uvi: MESSAGES.indicators.uvi,
  dew_point: MESSAGES.indicators.dewPoint,
};

/**
 * Texto de um valor na escala ativa: `Scaled` (`{ c, f }`) escolhe a chave da escala, e um
 * texto que não muda com a escala (umidade, pressão…) é usado como veio (RN-056, RN-057).
 * @param {string | { c: string, f: string }} value
 * @param {'c' | 'f'} scale
 */
function inScale(value, scale) {
  return typeof value === 'string' ? value : value[scale];
}

/**
 * Monta o bloco e passa a redesenhá-lo a cada mudança de estado.
 * @param {HTMLElement} root a `<section class="current">`
 */
export function mount(root) {
  root.setAttribute('aria-label', MESSAGES.current.label);
  const card = root.querySelector('.current-card');
  const nodes = {
    alerts: card.querySelector('.current-alerts'),
    alertsText: card.querySelector('.current-alerts-text'),
    time: card.querySelector('.current-time'),
    temp: card.querySelector('.current-temp'),
    min: card.querySelector('.current-min'),
    icon: card.querySelector('.current-icon'),
    description: card.querySelector('.current-description'),
    feelsLike: card.querySelector('.current-feels-like'),
  };
  const values = new Map();
  for (const item of root.querySelectorAll('.indicator')) {
    const key = item.dataset.indicator;
    setText(item.querySelector('.indicator-name'), INDICATOR_LABELS[key]);
    values.set(key, item.querySelector('.indicator-value'));
  }

  let drawn = { current: null, day: null, scale: null };
  const render = (state) => {
    renderBlockState(root, blockState(state), { onRetry: () => retry() });
    const current = state.weather?.current;
    if (!current) return;
    const day = selectedDay(state.weather, state.selectedDay);
    // Redesenha só com dados novos, outro dia ou outra escala (RF-055, RF-058, RNF-013).
    const { scale } = state;
    if (current === drawn.current && day === drawn.day && scale === drawn.scale) return;
    drawn = { current, day, scale };
    drawCard(card, nodes, day ? daySummary(day) : currentSummary(current), scale);
    const { indicators } = day ?? current;
    for (const [key, node] of values) setText(node, inScale(indicators[key], scale));
  };
  subscribe(render);
  render(getState());
}

/**
 * Dia que o bloco resume, ou `null` para as condições atuais (RF-026 a RF-028, seção 7.4).
 * @returns {object | null} item de `WeatherView.daily`
 */
function selectedDay(weather, selected) {
  if (selected == null || !weather.daily) return null;
  const nowSec = Math.floor(Date.now() / 1000);
  const days = visibleDays(weather.daily, nowSec, weather.timezone_offset);
  return activeDay(days, selected, nowSec, weather.timezone_offset);
}

/** Card da aba "Hoje": temperatura atual, hora local e sensação (RF-016, RN-014 a RN-016). */
function currentSummary(current) {
  return {
    ...current,
    time: current.time_label,
    temp: current.temp,
    min: null,
  };
}

/**
 * Card de outro dia: máxima, "Mín. X°", sensação diurna e a data no lugar da hora (RF-026,
 * RN-030), com a ilustração e o selo do dia (RF-030, RN-033).
 */
function daySummary(day) {
  return {
    ...day,
    time: day.date_label,
    temp: day.max,
    min: day.min_label,
  };
}

/**
 * Desenha o card principal: temperatura, descrição, sensação, hora ou data, selo de alertas,
 * ícone e ilustração (RF-016 a RF-019, RN-017, RN-018). Valor ausente já vem como "—"
 * (RF-023, P-013).
 */
function drawCard(card, nodes, summary, scale) {
  card.dataset.condition = summary.condition_group;
  setText(nodes.time, summary.time);
  setText(nodes.temp, inScale(summary.temp, scale));
  setText(nodes.min, summary.min && inScale(summary.min, scale));
  nodes.min.hidden = summary.min == null;
  setText(nodes.description, summary.description);
  setText(nodes.feelsLike, inScale(summary.feels_like, scale));
  setConditionIcon(nodes.icon, summary.icon, summary.description);
  // O selo diz a quantidade em texto, e some sem alertas (RF-018, RF-019, RNF-010).
  setText(nodes.alertsText, summary.alerts_label);
  nodes.alerts.hidden = summary.alerts_label == null;
}
