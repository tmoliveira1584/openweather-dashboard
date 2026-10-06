/**
 * Utilitários dos blocos de `ui/`: criação de elementos, texto e estados de bloco
 * (arquitetura, seções 6.5 e 8.2).
 *
 * Texto sempre por `textContent`, nunca como marcação (P-003, guardrail 4).
 */

import { MESSAGES, weatherErrorMessage } from '../messages.js';

/**
 * Cria um elemento com classe, texto, atributos, eventos e filhos.
 * @param {string} tag
 * @param {{ class?: string, text?: string | null, attrs?: Record<string, string>,
 *           on?: Record<string, EventListener> }} [props]
 * @param {Node[]} [children]
 * @returns {HTMLElement}
 */
export function el(tag, { class: className, text, attrs = {}, on = {} } = {}, children = []) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text != null) node.textContent = text;
  for (const [name, value] of Object.entries(attrs)) node.setAttribute(name, value);
  for (const [type, listener] of Object.entries(on)) node.addEventListener(type, listener);
  node.append(...children);
  return node;
}

/**
 * Troca o texto do nó. Valor ausente vira texto vazio (P-003).
 * @param {Node} node
 * @param {string | null | undefined} text
 */
export function setText(node, text) {
  node.textContent = text ?? '';
}

// Ícones de condição do provedor: exceção ao guardrail 2 (arquitetura, seção 8.4).
const ICON_BASE_URL = 'https://openweathermap.org/img/wn/';

/**
 * Mostra o ícone de condição do provedor com a descrição como texto alternativo (RNF-010).
 * Sem código de ícone, a imagem fica oculta. O código entra codificado na URL (P-003).
 * @param {HTMLImageElement} img
 * @param {string | null} icon código do ícone (ex.: `10d`)
 * @param {string} description
 */
export function setConditionIcon(img, icon, description) {
  img.hidden = !icon;
  img.alt = icon ? description : '';
  if (!icon) {
    img.removeAttribute('src');
    return;
  }
  const src = `${ICON_BASE_URL}${encodeURIComponent(icon)}@2x.png`;
  if (img.getAttribute('src') !== src) img.src = src;
}

/**
 * @typedef {{ kind: 'loading' | 'slow' | 'error' | 'unavailable' | 'refreshing' | 'ready',
 *             message?: string }} BlockView
 */

/**
 * Estado de um bloco, derivado do estado da aplicação e nunca guardado (seção 6.5).
 * `part` é a chave do bloco no view model (ex.: `daily`): com `ready` e a parte `null`, o
 * bloco fica indisponível com a mensagem `unavailable`.
 * @param {{ weatherStatus: string, weatherError?: string | null, weather?: object | null }} state
 * @param {{ part?: string, unavailable?: string }} [block]
 * @returns {BlockView}
 */
export function blockState(state, { part, unavailable } = {}) {
  switch (state.weatherStatus) {
    case 'slow':
      return { kind: 'slow', message: MESSAGES.stillLoading };
    case 'error':
      return { kind: 'error', message: weatherErrorMessage(state.weatherError) };
    case 'refreshing':
      return { kind: 'refreshing', message: MESSAGES.refreshing };
    case 'ready':
      if (part && unavailable && state.weather?.[part] == null) {
        return { kind: 'unavailable', message: unavailable };
      }
      return { kind: 'ready' };
    default:
      // 'idle' e 'loading': o bloco aguarda dados (RF-005, P-020).
      return { kind: 'loading' };
  }
}

const BUSY = new Set(['loading', 'slow', 'refreshing']);

/**
 * Desenha o estado no bloco (RF-005, RF-013, RN-012, P-020, P-022).
 *
 * O bloco recebe `data-block-state` e `aria-busy`, e um `.block-state` com o indicador, a
 * mensagem ou o botão "Tentar novamente". O CSS esconde o conteúdo do bloco (menos o título)
 * enquanto ele aguarda, falha ou está indisponível. Em `refreshing`, os dados antigos
 * continuam visíveis. Redesenhar o mesmo estado não recria nada, e o foco é mantido.
 * @param {HTMLElement} block
 * @param {BlockView} view
 * @param {{ onRetry?: () => void }} [options]
 */
export function renderBlockState(block, view, { onRetry } = {}) {
  let box = block.querySelector(':scope > .block-state');
  if (!box) {
    box = el('div', { class: 'block-state', attrs: { role: 'status' } });
    block.append(box);
  }
  block.dataset.blockState = view.kind;
  block.setAttribute('aria-busy', String(BUSY.has(view.kind)));

  const signature = `${view.kind}|${view.message ?? ''}`;
  if (box.dataset.signature === signature) return;
  box.dataset.signature = signature;
  box.hidden = view.kind === 'ready';
  box.replaceChildren(...stateContent(view, onRetry));
}

function spinner() {
  return el('span', { class: 'block-state-spinner', attrs: { 'aria-hidden': 'true' } });
}

function stateContent(view, onRetry) {
  switch (view.kind) {
    case 'loading':
      return [spinner(), el('span', { class: 'visually-hidden', text: MESSAGES.loading })];
    case 'slow':
    case 'refreshing':
      return [spinner(), el('span', { text: view.message })];
    case 'error':
      return [
        el('p', { text: view.message }),
        el('button', {
          class: 'block-state-retry',
          text: MESSAGES.retry,
          attrs: { type: 'button' },
          on: { click: () => onRetry?.() },
        }),
      ];
    case 'unavailable':
      return [el('p', { text: view.message })];
    default:
      return [];
  }
}
