/**
 * Cabeçalho (arquitetura, seção 5.1): título, seletor °C/°F, cidade selecionada, busca e aviso
 * de localização.
 *
 * Usa a estrutura do `index.html` e preenche os textos pelo `messages.js` e pelo estado. As
 * regras da busca ficam em `actions.js`; aqui ficam só o desenho e os eventos. A opção
 * destacada pelas setas é estado só da tela e não vai para o `state.js`.
 */

import {
  chooseSearchResult,
  closeSearch,
  dismissLocationNotice,
  SEARCH_MAX_LENGTH,
  search,
  setScale,
} from '../actions.js';
import { MESSAGES } from '../messages.js';
import { getState, subscribe } from '../state.js';
import { el, setText } from './dom.js';

// Status da busca com uma mensagem abaixo do campo (seção 6.5).
const WITH_MESSAGE = new Set(['invalid', 'empty', 'error']);

/**
 * Monta o cabeçalho e passa a redesenhá-lo a cada mudança de estado.
 * @param {HTMLElement} root o `<header class="app-header">`
 */
export function mount(root) {
  setText(root.querySelector('.app-title'), MESSAGES.header.title);
  const parts = [
    mountScale(root.querySelector('.scale-toggle')),
    mountCity(root.querySelector('.city')),
    mountSearch(root.querySelector('.search')),
    mountNotice(root.querySelector('.location-notice')),
  ];
  const render = (state, previous) => {
    for (const renderPart of parts) renderPart(state, previous);
  };
  subscribe(render);
  render(getState(), getState());
}

/**
 * Seletor °C/°F: a escala ativa tem `aria-pressed` e destaque além da cor (RF-053, RF-054,
 * RNF-028). Os botões já funcionam pelo teclado (Tab, Enter e Espaço).
 */
function mountScale(group) {
  group.setAttribute('aria-label', MESSAGES.header.scaleGroup);
  const buttons = [...group.querySelectorAll('.scale-option')];
  for (const button of buttons) {
    setText(button, MESSAGES.header.scales[button.dataset.scale]);
    button.addEventListener('click', () => setScale(button.dataset.scale));
  }
  return (state) => {
    for (const button of buttons) {
      button.setAttribute('aria-pressed', String(button.dataset.scale === state.scale));
    }
  };
}

/**
 * Cidade selecionada no formato "<nome>, <país>", trocada na hora (RF-010, RN-007, RN-013).
 * Nome longo: cortado com "…" e completo ao passar o cursor ou focar (CSS).
 */
function mountCity(city) {
  const name = city.querySelector('.city-name');
  return (state) => setText(name, state.city?.headerLabel);
}

/**
 * Campo de busca e lista de resultados no padrão combobox da ARIA (RF-006 a RF-009, RF-011,
 * RF-012, RNF-007): o foco fica no campo, e a opção destacada é indicada por
 * `aria-activedescendant` e `aria-selected`.
 */
function mountSearch(form) {
  const input = form.querySelector('.search-input');
  const popup = form.querySelector('.search-popup');
  const list = form.querySelector('.search-results');
  const hint = form.querySelector('.search-hint');
  const message = form.querySelector('.search-message');
  let drawnResults = null;
  let active = -1; // índice da opção destacada pelas setas; -1 = nenhuma

  input.maxLength = SEARCH_MAX_LENGTH;
  input.placeholder = MESSAGES.search.label;
  input.setAttribute('aria-label', MESSAGES.search.label);
  form.querySelector('.search-button').setAttribute('aria-label', MESSAGES.search.button);
  list.setAttribute('aria-label', MESSAGES.search.results);
  setText(hint, MESSAGES.search.truncated);

  const options = () => [...list.children];
  const isOpen = () => getState().search.status === 'open';
  const choose = (index) => chooseSearchResult(getState().search.results[index]);
  const closeIfShown = () => {
    if (getState().search.status !== 'idle') closeSearch();
  };

  const highlight = (index) => {
    active = index;
    options().forEach((option, i) => option.setAttribute('aria-selected', String(i === index)));
    if (index >= 0) input.setAttribute('aria-activedescendant', options()[index].id);
    else input.removeAttribute('aria-activedescendant');
  };

  // Enter no campo ou clique na lupa. O foco fica no campo, também quando o termo é inválido.
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    input.focus();
    search(input.value);
  });

  // Teclado na lista: setas, Enter e Esc (RNF-007).
  input.addEventListener('keydown', (event) => {
    const count = options().length;
    if ((event.key === 'ArrowDown' || event.key === 'ArrowUp') && isOpen() && count) {
      event.preventDefault();
      const step = event.key === 'ArrowDown' ? 1 : -1;
      const start = event.key === 'ArrowDown' ? 0 : count - 1;
      highlight(active < 0 ? start : (active + step + count) % count);
    } else if (event.key === 'Enter' && isOpen() && active >= 0) {
      event.preventDefault(); // escolhe a opção em vez de buscar de novo
      choose(active);
    } else if (event.key === 'Escape' && getState().search.status !== 'idle') {
      event.preventDefault(); // fecha a lista sem apagar o termo digitado
      closeSearch();
    }
  });

  // Editar o termo apaga a mensagem anterior (termo inválido, nenhum resultado ou falha).
  input.addEventListener('input', () => {
    if (WITH_MESSAGE.has(getState().search.status)) closeSearch();
  });

  // Clique numa opção: o `pointerdown` não tira o foco do campo.
  list.addEventListener('pointerdown', (event) => event.preventDefault());
  list.addEventListener('click', (event) => {
    const option = event.target.closest('[role="option"]');
    if (option) choose(Number(option.dataset.index));
  });

  // Clique fora ou foco fora da busca fecha a lista (RF-011).
  document.addEventListener('pointerdown', (event) => {
    if (!form.contains(event.target)) closeIfShown();
  });
  form.addEventListener('focusout', (event) => {
    if (event.relatedTarget && !form.contains(event.relatedTarget)) closeIfShown();
  });

  return (state, previous) => {
    const { status, results, truncated } = state.search;
    // Cidade escolhida pela busca: o campo é limpo (RF-008).
    if (state.selectionId !== previous.selectionId && state.city?.source === 'search') {
      input.value = '';
    }
    if (results !== drawnResults) {
      drawnResults = results;
      list.replaceChildren(
        ...results.map((result, index) =>
          el('li', {
            class: 'search-option',
            text: result.list_label, // texto, nunca marcação (P-003)
            attrs: {
              id: `search-option-${index}`,
              role: 'option',
              'aria-selected': 'false',
              'data-index': String(index),
            },
          }),
        ),
      );
      highlight(-1);
    }
    const open = status === 'open';
    if (!open && active >= 0) highlight(-1);
    popup.hidden = !open;
    hint.hidden = !truncated;
    input.setAttribute('aria-expanded', String(open));
    form.setAttribute('aria-busy', String(status === 'loading'));
    setText(message, WITH_MESSAGE.has(status) ? state.search.message : null);
  };
}

/**
 * Aviso de localização, com o botão que o fecha (RF-003, RN-002). O texto só entra quando o
 * aviso aparece, e só uma vez, para que leitores de tela o anunciem sem repetir
 * (`role="status"`).
 */
function mountNotice(notice) {
  const text = notice.querySelector('.location-notice-text');
  const close = notice.querySelector('.location-notice-close');
  close.setAttribute('aria-label', MESSAGES.location.closeNotice);
  close.addEventListener('click', () => dismissLocationNotice());
  return (state) => {
    const message = state.locationNotice ? MESSAGES.location.notice : '';
    if (text.textContent !== message) setText(text, message);
    notice.hidden = !state.locationNotice;
  };
}
