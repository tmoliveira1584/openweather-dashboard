/**
 * Condições atuais (arquitetura, seção 5.1; feature 2): card principal e os seis indicadores.
 *
 * Usa a estrutura do `index.html` e preenche os textos pelo `messages.js` e pelo view model.
 * Os valores chegam prontos do backend, nas duas escalas: aqui só se escolhe o texto da escala
 * ativa (ADR-004, guardrail 8). A ilustração de cada grupo de condição fica no CSS, pelo
 * `data-condition` do card (ADR-012).
 */

import { retry } from '../actions.js';
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

  let drawn = { current: null, scale: null };
  const render = (state) => {
    renderBlockState(root, blockState(state), { onRetry: () => retry() });
    const current = state.weather?.current;
    // Redesenha só com dados novos ou outra escala (RF-055, RF-058).
    if (!current || (current === drawn.current && state.scale === drawn.scale)) return;
    drawn = { current, scale: state.scale };
    drawCard(card, nodes, current, state.scale);
    for (const [key, node] of values) setText(node, inScale(current.indicators[key], state.scale));
  };
  subscribe(render);
  render(getState());
}

/**
 * Card principal da aba "Hoje": temperatura, descrição, sensação, hora local, selo de alertas,
 * ícone e ilustração (RF-016 a RF-019, RN-014 a RN-018). Valor ausente já vem como "—"
 * (RF-023, P-013).
 */
function drawCard(card, nodes, current, scale) {
  card.dataset.condition = current.condition_group;
  setText(nodes.time, current.time_label);
  setText(nodes.temp, inScale(current.temp, scale));
  setText(nodes.description, current.description);
  setText(nodes.feelsLike, inScale(current.feels_like, scale));
  setConditionIcon(nodes.icon, current.icon, current.description);
  // O selo diz a quantidade em texto, e some sem alertas (RF-018, RF-019, RNF-010).
  setText(nodes.alertsText, current.alerts_label);
  nodes.alerts.hidden = current.alerts_label == null;
}
