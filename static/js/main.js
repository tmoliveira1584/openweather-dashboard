/**
 * Ponto de entrada do frontend (arquitetura, seção 5.1).
 *
 * Monta o cabeçalho, as abas de dias, as condições atuais e a previsão hora a hora, aplica os
 * estados de bloco (carregando, erro, indisponível) ao bloco de dados que ainda é o esqueleto
 * da fatia 5 e inicia o fluxo de localização (`start`). Esse bloco passa a ter o próprio
 * `ui/<bloco>.js` na fatia 10.
 */

import { retry, start } from './actions.js';
import { MESSAGES } from './messages.js';
import { getState, subscribe } from './state.js';
import { mount as mountCurrent } from './ui/current.js';
import { mount as mountDayTabs } from './ui/day-tabs.js';
import { blockState, renderBlockState } from './ui/dom.js';
import { mount as mountHeader } from './ui/header.js';
import { mount as mountHourly } from './ui/hourly.js';

// Blocos de dados ainda sem módulo próprio e a parte de cada um no view model (seção 6.3).
const DATA_BLOCKS = [
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
mountDayTabs(document.querySelector('.day-tabs'));
mountCurrent(document.querySelector('.current'));
mountHourly(document.querySelector('.hourly'));
mountDataBlocks();
start();
