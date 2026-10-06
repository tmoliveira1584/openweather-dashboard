/**
 * Ponto de entrada do frontend (arquitetura, seção 5.1).
 *
 * Monta o cabeçalho e as condições atuais, aplica os estados de bloco (carregando, erro,
 * indisponível) aos blocos de dados que ainda são o esqueleto da fatia 5 e inicia o fluxo de
 * localização (`start`). Esses blocos passam a ter o próprio `ui/<bloco>.js` nas fatias 8 a 11.
 */

import { retry, start } from './actions.js';
import { MESSAGES } from './messages.js';
import { getState, subscribe } from './state.js';
import { mount as mountCurrent } from './ui/current.js';
import { blockState, renderBlockState } from './ui/dom.js';
import { mount as mountHeader } from './ui/header.js';

// Blocos de dados ainda sem módulo próprio e a parte de cada um no view model (seção 6.3).
const DATA_BLOCKS = [
  { selector: '.day-tabs', part: 'daily', unavailable: MESSAGES.daily.unavailable },
  { selector: '.hourly', part: 'hourly', unavailable: MESSAGES.hourly.unavailable },
  { selector: '.minutely', part: 'minutely', unavailable: MESSAGES.minutely.unavailable },
];

function mountDataBlocks() {
  const blocks = DATA_BLOCKS.map((block) => ({
    ...block,
    root: document.querySelector(block.selector),
  }));
  const render = (state) => {
    for (const block of blocks) {
      renderBlockState(block.root, blockState(state, block), { onRetry: () => retry() });
    }
  };
  subscribe(render);
  render(getState());
}

mountHeader(document.querySelector('.app-header'));
mountCurrent(document.querySelector('.current'));
mountDataBlocks();
start();
