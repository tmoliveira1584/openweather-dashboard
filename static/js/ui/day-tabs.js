/**
 * Faixa de abas de dias (arquitetura, seção 5.1; feature 3): "Hoje" e os dias seguintes, com
 * a máxima e o ícone da condição.
 *
 * Segue o padrão de abas da ARIA com ativação manual: as setas, Home e End movem o foco, e o
 * Enter (ou o Espaço, ou o clique) seleciona (RNF-014). Só a aba selecionada entra na ordem
 * do Tab. Os dias visíveis e o dia ativo saem de `logic/time-window.js`, com o relógio do
 * navegador (ADR-004); o card principal (`ui/current.js`) faz o mesmo cálculo.
 */

import { retry, selectDay } from '../actions.js';
import { activeDay, cityToday, visibleDays } from '../logic/time-window.js';
import { MESSAGES } from '../messages.js';
import { getState, subscribe } from '../state.js';
import { blockState, el, renderBlockState, setConditionIcon, setText } from './dom.js';

/**
 * Monta a faixa e passa a redesenhá-la a cada mudança de estado.
 * @param {HTMLElement} root o `<nav class="day-tabs">`
 */
export function mount(root) {
  root.setAttribute('aria-label', MESSAGES.daily.label);
  const list = root.querySelector('.day-tabs-list');
  let drawn = { daily: null, dates: '', selected: null };

  // A aba de hoje seleciona "Hoje" (`null`); as demais, a data do dia.
  list.addEventListener('click', (event) => {
    const tab = event.target.closest('[role="tab"]');
    if (tab) selectDay(tab.dataset.day || null);
  });
  list.addEventListener('keydown', (event) => moveFocus(list, event));

  const render = (state) => {
    const weather = state.weather;
    const nowSec = Math.floor(Date.now() / 1000);
    const offset = weather?.timezone_offset;
    const days = visibleDays(weather?.daily ?? null, nowSec, offset);
    renderBlockState(root, stripState(state, days), { onRetry: () => retry() });
    if (!days.length) {
      if (weather) list.replaceChildren();
      drawn = { daily: null, dates: '', selected: null };
      return;
    }

    const today = cityToday(nowSec, offset);
    const dates = days.map((day) => day.local_date).join();
    if (weather.daily !== drawn.daily || dates !== drawn.dates) {
      rebuild(list, days, today);
      drawn = { daily: weather.daily, dates, selected: null };
    }

    const selected = activeDay(days, state.selectedDay, nowSec, offset)?.local_date ?? today;
    days.forEach((day, index) => {
      const tab = list.children[index];
      const isSelected = day.local_date === selected;
      setText(tab.querySelector('.day-tab-temp'), day.max[state.scale]);
      tab.setAttribute('aria-selected', String(isSelected));
      tab.tabIndex = isSelected ? 0 : -1;
    });
    // A aba selecionada é trazida para a área visível da faixa (feature 3, categoria 10).
    if (selected !== drawn.selected) {
      if (drawn.selected !== null) {
        list.querySelector('[aria-selected="true"]')?.scrollIntoView({
          block: 'nearest',
          inline: 'nearest',
        });
      }
      drawn.selected = selected;
    }
  };
  subscribe(render);
  render(getState());
}

/**
 * Estado da faixa: o de `blockState`, e "indisponível" também quando nenhum dia da previsão
 * é de hoje em diante (RF-024, feature 3, categoria 5).
 */
function stripState(state, days) {
  const view = blockState(state, { part: 'daily', unavailable: MESSAGES.daily.unavailable });
  return view.kind === 'ready' && !days.length
    ? { kind: 'unavailable', message: MESSAGES.daily.unavailable }
    : view;
}

/**
 * Recria as abas: rótulo "Hoje" ou dia da semana (RN-028), máxima (RN-029) e ícone com a
 * descrição como texto alternativo (RF-024, RNF-010). Uma aba com o foco continua com ele.
 */
function rebuild(list, days, today) {
  const focused = list.contains(document.activeElement) ? document.activeElement : null;
  const focusedDate = focused?.dataset.date;
  list.replaceChildren(
    ...days.map((day) => {
      const isToday = day.local_date === today;
      const icon = el('img', { class: 'day-tab-icon', attrs: { width: '32', height: '32' } });
      setConditionIcon(icon, day.icon, day.description);
      return el(
        'button',
        {
          class: 'day-tab',
          attrs: {
            type: 'button',
            role: 'tab',
            'data-date': day.local_date,
            'data-day': isToday ? '' : day.local_date,
          },
        },
        [
          el('span', {
            class: 'day-tab-label',
            text: isToday ? MESSAGES.daily.today : day.weekday_label,
          }),
          ' ',
          el('span', { class: 'day-tab-temp' }),
          icon,
        ],
      );
    }),
  );
  if (focusedDate) list.querySelector(`[data-date="${focusedDate}"]`)?.focus();
}

/** Setas, Home e End movem o foco entre as abas, dando a volta nas pontas (RNF-014). */
function moveFocus(list, event) {
  const tabs = [...list.children];
  const index = tabs.indexOf(event.target.closest('[role="tab"]'));
  if (index < 0) return;
  const last = tabs.length - 1;
  const next = {
    ArrowRight: index === last ? 0 : index + 1,
    ArrowLeft: index === 0 ? last : index - 1,
    Home: 0,
    End: last,
  }[event.key];
  if (next === undefined) return;
  event.preventDefault();
  tabs[next].focus();
}
