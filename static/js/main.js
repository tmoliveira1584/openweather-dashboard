/**
 * Ponto de entrada do frontend (arquitetura, seção 5.1).
 *
 * Versão provisória: monta o cabeçalho (fatia 6b), aplica os estados de bloco (carregando,
 * erro, indisponível) aos blocos de dados do esqueleto da fatia 5 e seleciona a cidade padrão
 * direto. Cada bloco passa a ter o próprio `ui/<bloco>.js` nas fatias 7 a 11, e o fluxo de
 * localização (`actions.start()`) substitui a seleção direta na fatia 6c.
 */

import { DEFAULT_CITY, retry, selectCity } from './actions.js';
import { MESSAGES } from './messages.js';
import { getState, subscribe } from './state.js';
import { blockState, renderBlockState } from './ui/dom.js';
import { mount as mountHeader } from './ui/header.js';

// Blocos de dados da tela e a parte de cada um no view model (seção 6.3).
const DATA_BLOCKS = [
  { selector: '.day-tabs', part: 'daily', unavailable: MESSAGES.daily.unavailable },
  { selector: '.current' },
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
mountDataBlocks();
selectCity(DEFAULT_CITY);
