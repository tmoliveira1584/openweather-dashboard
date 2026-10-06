/**
 * Previsão por minuto (arquitetura, seção 5.1; feature 5): marcos, barras por faixa de
 * intensidade, resumo da próxima hora e legenda, no painel sobreposto ao mapa.
 *
 * As barras são um SVG esticado (ADR-007): cada minuto é uma coluna de largura 1 no
 * `viewBox`, e a altura vai de 0 a 100. A janela de minutos, os marcos, o resumo e a altura
 * das barras saem de `logic/` (ADR-004); aqui só se desenha. A intensidade é sempre em mm/h,
 * e o painel não depende da escala ativa (RN-046, RN-057).
 *
 * O gráfico é um único elemento focável, com o papel de controle deslizante: as setas, Home e
 * End percorrem os minutos, e o valor do minuto ("HH:MM — X,XX mm/h") é anunciado pelo
 * `aria-valuetext` (RNF-020). O minuto ativo, pelo cursor ou pelo foco, mostra o mesmo valor
 * na dica (RF-044).
 */

import { retry } from '../actions.js';
import { barHeight } from '../logic/chart-math.js';
import { minuteSummary } from '../logic/summaries.js';
import { minuteMarks, minuteWindow } from '../logic/time-window.js';
import { MESSAGES } from '../messages.js';
import { getState, subscribe } from '../state.js';
import { blockState, el, renderBlockState, setText } from './dom.js';

const SVG_NS = 'http://www.w3.org/2000/svg';
// Altura das barras, em % da altura do gráfico: o teto de 10 mm/h ocupa tudo, e 0 mm/h fica
// com a altura mínima visível (RN-042).
const BAR_MAX = 100;
const BAR_MIN = 8;
// Espaço entre duas barras, em fração da coluna do minuto.
const BAR_GAP = 0.2;
// Faixas na ordem da legenda (RN-041).
const BANDS = ['none', 'light', 'moderate', 'heavy', 'extreme'];

/**
 * Monta o bloco e passa a redesenhá-lo a cada mudança de estado.
 * @param {HTMLElement} root a `<section class="minutely">`
 */
export function mount(root) {
  const nodes = {
    marks: root.querySelector('.minutely-marks'),
    chart: root.querySelector('.minutely-bars'),
    cursor: root.querySelector('.minutely-cursor'),
    bars: root.querySelector('.minutely-bar-list'),
    tooltip: root.querySelector('.minutely-tooltip'),
    summary: root.querySelector('.minutely-summary'),
    legend: root.querySelector('.minutely-legend'),
  };
  setText(root.querySelector('.panel-title'), MESSAGES.minutely.title);
  nodes.legend.replaceChildren(...BANDS.map(legendItem));

  const view = { minutes: [] };
  const pointer = activeMinute(nodes, view);
  wireChart(nodes.chart, pointer);
  let drawn = { minutely: null, dates: '' };

  const render = (state) => {
    const weather = state.weather;
    const minutes = minuteWindow(
      weather?.minutely ?? null,
      Math.floor(Date.now() / 1000),
      weather?.timezone_offset ?? 0,
    );
    renderBlockState(root, panelState(state, minutes), { onRetry: () => retry() });

    // Redesenha só com dados novos ou outra janela (um minuto passou). A escala não muda
    // nada no painel (RN-046).
    const dates = minutes.map((minute) => minute.dt).join();
    if (weather?.minutely === drawn.minutely && dates === drawn.dates) return;
    view.minutes = minutes;
    draw(nodes, minutes, weather?.timezone_offset ?? 0);
    pointer.refresh();
    drawn = { minutely: weather?.minutely ?? null, dates };
  };
  subscribe(render);
  render(getState());
}

/**
 * Estado do bloco: o de `blockState`, e "indisponível" também quando todos os minutos
 * recebidos já passaram (RF-045, RN-047).
 */
function panelState(state, minutes) {
  const unavailable = MESSAGES.minutely.unavailable;
  const view = blockState(state, { part: 'minutely', unavailable });
  return view.kind === 'ready' && !minutes.length
    ? { kind: 'unavailable', message: unavailable }
    : view;
}

/** Item da legenda: a cor da faixa e o texto dela, que não depende da cor (RF-042, RNF-019). */
function legendItem(band) {
  return el('li', { class: 'legend-item' }, [
    el('span', { class: `legend-swatch band-${band}`, attrs: { 'aria-hidden': 'true' } }),
    el('span', { text: MESSAGES.minutely.legend[band] }),
  ]);
}

/** Marcos, barras e resumo dos minutos da janela. Sem minutos, o painel fica vazio. */
function draw(nodes, minutes, offset) {
  const count = minutes.length;
  nodes.marks.replaceChildren(...minuteMarks(minutes, offset).map(markItem));
  nodes.chart.setAttribute('viewBox', `0 0 ${Math.max(count, 1)} ${BAR_MAX}`);
  nodes.bars.replaceChildren(...minutes.map(bar));
  const summary = minuteSummary(minutes);
  setText(nodes.summary, summary);
  nodes.summary.hidden = summary == null;
}

/**
 * Marco com rótulo e horário (RF-041). O marco é deslocado pela mesma fração da posição dele:
 * o de "Agora" começa no início da primeira barra, o de 60 min termina no fim da última, e
 * nenhum sai do gráfico. A marca no pé do marco fica exatamente no início do seu minuto
 * (RN-043).
 */
function markItem({ label, time, position }) {
  return el('li', { class: 'mark', attrs: { style: `--position: ${position}` } }, [
    el('span', { class: 'mark-label', text: label }),
    el('span', { class: 'mark-time', text: time }),
  ]);
}

/**
 * Barra de um minuto, colorida pela faixa (RF-039, RF-040, RN-041) e com a altura de
 * `barHeight` (RN-042). Sem intensidade, a coluna fica vazia (RN-047).
 */
function bar(minute, index) {
  const height = barHeight(minute.intensity, BAR_MAX, BAR_MIN);
  const node = document.createElementNS(SVG_NS, 'rect');
  node.setAttribute('class', minute.band ? `bar band-${minute.band}` : 'bar is-missing');
  node.setAttribute('x', String(index + BAR_GAP / 2));
  node.setAttribute('width', String(1 - BAR_GAP));
  node.setAttribute('y', String(BAR_MAX - height));
  node.setAttribute('height', String(height));
  return node;
}

/**
 * Minuto ativo do gráfico: o apontado pelo cursor ou, sem cursor, o selecionado pelo
 * teclado enquanto o gráfico tem o foco. Ele mostra a dica e o destaque da coluna. O minuto
 * selecionado pelo teclado é o valor do controle deslizante (RNF-020).
 */
function activeMinute(nodes, view) {
  let current = 0; // minuto do teclado
  let currentDt = null;
  let hovered = null;

  const focused = () => document.activeElement === nodes.chart;

  const show = () => {
    const count = view.minutes.length;
    const chart = nodes.chart;
    if (count) {
      chart.setAttribute('aria-valuemin', '0');
      chart.setAttribute('aria-valuemax', String(count - 1));
      chart.setAttribute('aria-valuenow', String(current));
      chart.setAttribute('aria-valuetext', view.minutes[current].tooltip);
    } else {
      for (const name of ['aria-valuemin', 'aria-valuemax', 'aria-valuenow', 'aria-valuetext']) {
        chart.removeAttribute(name);
      }
    }

    const active = hovered ?? (focused() ? current : null);
    const { cursor, tooltip } = nodes;
    const hidden = active == null || !count;
    // O destaque é um elemento SVG, sem a propriedade `hidden` dos elementos HTML.
    cursor.style.display = hidden ? 'none' : '';
    tooltip.hidden = hidden;
    if (hidden) return;
    cursor.setAttribute('x', String(active));
    // Como os marcos: deslocada pela fração do centro da barra, a dica nunca sai do gráfico.
    tooltip.style.setProperty('--position', String((active + 0.5) / count));
    setText(tooltip, view.minutes[active].tooltip);
  };

  const select = (index) => {
    current = index;
    currentDt = view.minutes[index]?.dt ?? null;
    show();
  };

  return {
    count: () => view.minutes.length,
    current: () => current,
    select,
    /** O cursor está sobre o minuto `index` ou saiu do gráfico (`null`). */
    hover(index) {
      hovered = index;
      show();
    },
    /** O gráfico ganhou ou perdeu o foco. */
    focusChanged: show,
    /** Depois de redesenhar: o teclado continua no mesmo minuto, se ele ainda estiver na janela. */
    refresh() {
      hovered = null;
      const index = view.minutes.findIndex((minute) => minute.dt === currentDt);
      select(index >= 0 ? index : 0);
    },
  };
}

/** Cursor, foco e teclado no gráfico (RF-044, RNF-020). */
function wireChart(chart, pointer) {
  chart.addEventListener('pointermove', (event) => {
    const count = pointer.count();
    if (!count) return;
    const box = chart.getBoundingClientRect();
    const index = Math.floor(((event.clientX - box.left) / box.width) * count);
    pointer.hover(Math.min(Math.max(index, 0), count - 1));
  });
  chart.addEventListener('pointerleave', () => pointer.hover(null));
  chart.addEventListener('focus', () => pointer.focusChanged());
  chart.addEventListener('blur', () => pointer.focusChanged());
  chart.addEventListener('keydown', (event) => {
    const last = pointer.count() - 1;
    if (last < 0) return;
    const index = pointer.current();
    const next = {
      ArrowRight: Math.min(index + 1, last),
      ArrowLeft: Math.max(index - 1, 0),
      Home: 0,
      End: last,
    }[event.key];
    if (next === undefined) return;
    event.preventDefault();
    pointer.select(next);
  });
}
