/**
 * Ponto de entrada do frontend (arquitetura, seção 5.1).
 *
 * Monta o cabeçalho, as abas de dias, as condições atuais, a previsão hora a hora, a
 * previsão por minuto e o mapa, e inicia o fluxo de localização (`start`). Cada bloco desenha
 * o próprio estado (carregando, erro, indisponível).
 *
 * Também liga o relógio aos fluxos: a virada de cada minuto chama `tick`, e voltar à página
 * chama `tick` e `refreshIfStale` (RF-014, arquitetura, seção 7.4).
 */

import { refreshIfStale, start, tick } from './actions.js';
import { mount as mountCurrent } from './ui/current.js';
import { mount as mountDayTabs } from './ui/day-tabs.js';
import { mount as mountHeader } from './ui/header.js';
import { mount as mountHourly } from './ui/hourly.js';
import { mount as mountMap } from './ui/map.js';
import { mount as mountMinutely } from './ui/minutely.js';

mountHeader(document.querySelector('.app-header'));
mountDayTabs(document.querySelector('.day-tabs'));
mountCurrent(document.querySelector('.current'));
mountHourly(document.querySelector('.hourly'));
mountMinutely(document.querySelector('.minutely'));
mountMap(document.querySelector('#map'));
start();

/** Chama `tick` agora e de novo no próximo minuto cheio do relógio. */
function followClock() {
  const now = Date.now();
  tick(now);
  setTimeout(followClock, 60_000 - (now % 60_000));
}
followClock();

// Em segundo plano, o navegador atrasa os `setTimeout`: ao voltar, o relógio e os dados são
// conferidos na hora.
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState !== 'visible') return;
  const now = Date.now();
  tick(now);
  refreshIfStale(now);
});
