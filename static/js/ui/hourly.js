/**
 * Previsão hora a hora (arquitetura, seção 5.1; feature 4): curva de temperatura, etiquetas
 * de chuva, pontos da curva e cards das próximas 24 horas, no mesmo contêiner de rolagem.
 *
 * Cada hora é uma coluna de largura fixa (`--hour-column`, seção 7.1), e o ponto, a etiqueta
 * e o card de uma hora ficam no centro da coluna dela. As posições são em % da largura e da
 * altura do gráfico, e a curva é um SVG esticado com o mesmo sistema (ADR-007). A janela de
 * horas, a escala vertical, o caminho, o agrupamento das etiquetas e o texto alternativo
 * saem de `logic/` (ADR-004); aqui só se desenha. Os valores chegam prontos do backend, nas
 * duas escalas (guardrail 8).
 *
 * Os pontos seguem o padrão de tabindex móvel: uma só parada do Tab, e as setas, Home e End
 * percorrem as horas (RNF-017). O ponto ativo, pelo cursor ou pelo foco, mostra a dica com a
 * hora, a temperatura e a chuva (RF-036) e destaca o card da mesma hora.
 */

import { retry } from '../actions.js';
import { groupRainLabels, monotonePath, scaleY } from '../logic/chart-math.js';
import { hourlyAltText } from '../logic/summaries.js';
import { hourlyWindow } from '../logic/time-window.js';
import { MESSAGES } from '../messages.js';
import { getState, subscribe } from '../state.js';
import { blockState, el, renderBlockState, setConditionIcon, setText } from './dom.js';

// Faixa da curva, em % da altura do gráfico. O centro fica em 50%: com temperaturas iguais, a
// linha fica no centro do bloco (RN-039). Acima, a dica do ponto; abaixo, as etiquetas.
const CURVE_TOP = 25;
const CURVE_BOTTOM = 75;
// Espaço mínimo entre duas etiquetas de chuva visíveis, em px (RN-038).
const RAIN_LABEL_GAP = 4;

/**
 * Monta o bloco e passa a redesenhá-lo a cada mudança de estado.
 * @param {HTMLElement} root a `<section class="hourly">`
 */
export function mount(root) {
  setText(root.querySelector('.panel-title'), MESSAGES.hourly.title);
  const nodes = {
    curve: root.querySelector('.hourly-curve'),
    path: root.querySelector('.hourly-curve path'),
    rain: root.querySelector('.hourly-rain'),
    points: root.querySelector('.hourly-points'),
    tooltip: root.querySelector('.hourly-tooltip'),
    list: root.querySelector('.hourly-list'),
  };
  const view = { hours: [], scale: 'c' };
  let drawn = { hourly: null, dates: '', scale: null };

  const pointer = activePoint(nodes, view);
  wirePoints(nodes.points, pointer);

  const render = (state) => {
    const weather = state.weather;
    const hours = hourlyWindow(weather?.hourly ?? null, Math.floor(Date.now() / 1000));
    renderBlockState(root, panelState(state, hours), { onRetry: () => retry() });
    if (!hours.length) {
      if (weather) clear(nodes);
      view.hours = [];
      drawn = { hourly: null, dates: '', scale: null };
      return;
    }

    // Redesenha só com dados novos, outra janela (uma hora passou) ou outra escala (RF-055).
    const dates = hours.map((hour) => hour.dt).join();
    const changed = weather.hourly !== drawn.hourly || dates !== drawn.dates;
    if (!changed && state.scale === drawn.scale) return;
    view.hours = hours;
    view.scale = state.scale;
    if (changed) build(nodes, hours, pointer);
    drawValues(nodes, hours, state.scale);
    pointer.refresh();
    drawn = { hourly: weather.hourly, dates, scale: state.scale };
  };
  subscribe(render);
  render(getState());
}

/**
 * Estado do bloco: o de `blockState`, e "indisponível" também quando todas as horas
 * recebidas já passaram (RF-038, RN-034).
 */
function panelState(state, hours) {
  const view = blockState(state, { part: 'hourly', unavailable: MESSAGES.hourly.unavailable });
  return view.kind === 'ready' && !hours.length
    ? { kind: 'unavailable', message: MESSAGES.hourly.unavailable }
    : view;
}

function clear(nodes) {
  nodes.path.removeAttribute('d');
  nodes.rain.replaceChildren();
  nodes.points.replaceChildren();
  nodes.list.replaceChildren();
  nodes.tooltip.hidden = true;
}

/** Posição horizontal do centro da coluna `index`, em % da largura do gráfico. */
function columnCenter(index, count) {
  return `${((index + 0.5) / count) * 100}%`;
}

/** Hora com o dia da semana na primeira hora de um novo dia: "00:00 Ter" (RN-035). */
function hourText(hour) {
  return [hour.hour_label, hour.weekday_label].filter(Boolean).join(' ');
}

/**
 * Recria os cards, os pontos e as etiquetas de chuva das horas da janela. O ponto com o foco
 * continua com ele, se a hora dele ainda estiver na janela.
 */
function build(nodes, hours, pointer) {
  const focusedDt = nodes.points.contains(document.activeElement)
    ? Number(document.activeElement.dataset.dt)
    : null;
  const count = hours.length;

  nodes.list.replaceChildren(...hours.map(hourCard));
  nodes.points.replaceChildren(
    ...hours.map((hour, index) =>
      el(
        'span',
        {
          class: 'hourly-point',
          attrs: {
            role: 'img',
            tabindex: '-1',
            'data-index': String(index),
            'data-dt': String(hour.dt),
            style: `left: ${(index / count) * 100}%; width: ${100 / count}%`,
          },
        },
        [el('span', { class: 'hourly-dot' })],
      ),
    ),
  );
  drawRainLabels(nodes.rain, hours);

  const focusedIndex = hours.findIndex((hour) => hour.dt === focusedDt);
  pointer.reset(focusedIndex);
  if (focusedIndex >= 0) nodes.points.children[focusedIndex].focus();
}

/**
 * Card da hora: hora (com o dia da semana às 00:00), ícone com a descrição como texto
 * alternativo, chance de precipitação e temperatura (RF-033, RN-035, RN-036, RNF-010). A
 * temperatura é preenchida por `drawValues`, na escala ativa.
 */
function hourCard(hour) {
  const icon = el('img', { class: 'hour-icon', attrs: { width: '40', height: '40' } });
  setConditionIcon(icon, hour.icon, hour.description);
  const weekday = hour.weekday_label
    ? [' ', el('span', { class: 'hour-weekday', text: hour.weekday_label })]
    : [];
  return el('li', { class: 'hour-card' }, [
    el('span', { class: 'hour-label', text: hour.hour_label }, weekday),
    icon,
    el('span', { class: 'hour-pop', text: hour.pop }),
    el('span', { class: 'hour-temp' }),
  ]);
}

/**
 * Etiquetas de chuva na posição de cada hora com volume (RF-035, RN-037). As que ficariam
 * sobrepostas são agrupadas, e só a de maior volume do grupo fica visível (RN-038): por isso
 * as etiquetas são medidas depois de entrarem na tela.
 */
function drawRainLabels(container, hours) {
  const count = hours.length;
  const labels = [];
  hours.forEach((hour, index) => {
    if (hour.rain_label == null) return;
    const label = el('span', {
      class: 'rain-label',
      text: hour.rain_label,
      attrs: { style: `left: ${columnCenter(index, count)}` },
    });
    labels.push({ label, value: hour.rain_value });
  });
  container.replaceChildren(...labels.map(({ label }) => label));

  const items = labels.map(({ label, value }) => {
    const box = label.getBoundingClientRect();
    return { x: box.left + box.width / 2, width: box.width, value };
  });
  const visible = groupRainLabels(items, RAIN_LABEL_GAP);
  labels.forEach(({ label }, index) => {
    label.hidden = !visible[index];
  });
}

/**
 * Valores que dependem da escala ativa: temperaturas dos cards, caminho da curva, posição e
 * nome de cada ponto e texto alternativo da curva (RN-040, RNF-016, RN-056). A curva usa a
 * temperatura sem arredondar (`temp_value`) só para a posição (guardrail 8).
 */
function drawValues(nodes, hours, scale) {
  const count = hours.length;
  const ys = scaleY(
    hours.map((hour) => hour.temp_value[scale]),
    CURVE_TOP,
    CURVE_BOTTOM,
  );

  nodes.curve.setAttribute('viewBox', `0 0 ${count} 100`);
  nodes.path.setAttribute('d', monotonePath(ys.map((y, index) => ({ x: index + 0.5, y }))));
  const altText = hourlyAltText(hours, scale);
  if (altText) {
    nodes.curve.setAttribute('role', 'img');
    nodes.curve.setAttribute('aria-label', altText);
    nodes.curve.removeAttribute('aria-hidden');
  } else {
    nodes.curve.removeAttribute('role');
    nodes.curve.removeAttribute('aria-label');
    nodes.curve.setAttribute('aria-hidden', 'true');
  }

  hours.forEach((hour, index) => {
    setText(nodes.list.children[index].querySelector('.hour-temp'), hour.temp[scale]);
    const point = nodes.points.children[index];
    point.setAttribute('aria-label', pointText(hour, scale));
    const dot = point.firstElementChild;
    dot.hidden = ys[index] == null;
    dot.style.top = `${ys[index] ?? 0}%`;
  });
}

/** Hora, temperatura e, se houver, volume de chuva de um ponto (RF-036). */
function pointText(hour, scale) {
  return MESSAGES.hourly.point(hourText(hour), hour.temp[scale], hour.rain_label);
}

/**
 * Ponto ativo da curva: o último apontado pelo cursor ou focado. Ele mostra a dica e o
 * marcador e destaca o card da mesma hora. Também guarda qual ponto entra na ordem do Tab.
 */
function activePoint(nodes, view) {
  let tabStop = 0; // o ponto que fica na ordem do Tab
  let hovered = null;
  let active = null;

  const focused = () =>
    nodes.points.contains(document.activeElement)
      ? Number(document.activeElement.dataset.index)
      : null;

  const setTabStop = (index) => {
    tabStop = index;
    [...nodes.points.children].forEach((point, i) => {
      point.tabIndex = i === index ? 0 : -1;
    });
  };

  const show = () => {
    for (const list of [nodes.points.children, nodes.list.children]) {
      [...list].forEach((node, i) => node.classList.toggle('is-active', i === active));
    }
    const { tooltip } = nodes;
    tooltip.hidden = active == null;
    if (active == null) return;
    const count = view.hours.length;
    const align = active === 0 ? 'start' : active === count - 1 ? 'end' : 'center';
    const edge = { start: active, center: active + 0.5, end: active + 1 }[align];
    tooltip.dataset.align = align;
    tooltip.style.left = `${(edge / count) * 100}%`;
    setText(tooltip, pointText(view.hours[active], view.scale));
  };

  return {
    /** O cursor entrou num ponto (`index`) ou saiu da curva (`null`): volta ao ponto focado. */
    hover(index) {
      hovered = index;
      active = index ?? focused();
      show();
    },
    focus(index) {
      setTabStop(index);
      active = index;
      show();
    },
    /** O foco saiu de um ponto: fica o ponto sob o cursor, se houver. */
    blur() {
      active = hovered;
      show();
    },
    /** Depois de recriar os pontos: o ponto com o foco, ou o primeiro, entra no Tab. */
    reset(index) {
      hovered = null;
      active = null;
      setTabStop(index >= 0 ? index : 0);
    },
    /** Depois de redesenhar os valores: a dica acompanha a escala e os dados novos. */
    refresh() {
      if (tabStop >= view.hours.length) setTabStop(0);
      if (active >= view.hours.length) active = null;
      show();
    },
  };
}

/**
 * Cursor, foco e teclado nos pontos da curva (RF-036, RNF-017). Só um movimento real do
 * cursor muda o ponto ativo: a rolagem pelo teclado passa as colunas sob o cursor parado,
 * e isso não pode tirar a dica do ponto focado.
 */
function wirePoints(container, pointer) {
  const indexOf = (target) => {
    const point = target.closest?.('.hourly-point');
    return point ? Number(point.dataset.index) : null;
  };
  let last = null;
  container.addEventListener('pointermove', (event) => {
    const position = `${event.clientX},${event.clientY}`;
    if (position === last) return;
    last = position;
    pointer.hover(indexOf(event.target));
  });
  container.addEventListener('pointerleave', () => {
    last = null;
    pointer.hover(null);
  });
  container.addEventListener('focusin', (event) => pointer.focus(indexOf(event.target)));
  container.addEventListener('focusout', () => pointer.blur());
  container.addEventListener('keydown', (event) => {
    const index = indexOf(event.target);
    if (index == null) return;
    const lastIndex = container.children.length - 1;
    const next = {
      ArrowRight: Math.min(index + 1, lastIndex),
      ArrowLeft: Math.max(index - 1, 0),
      Home: 0,
      End: lastIndex,
    }[event.key];
    if (next === undefined) return;
    event.preventDefault();
    container.children[next].focus();
  });
}
