/**
 * Fluxos da aplicação: a única camada que muda o estado (arquitetura, seções 2.2 e 6.6).
 *
 * Nesta fatia: `selectCity` e `retry`. Os demais fluxos (`start`, `search`, `selectDay`,
 * `setScale`, `refreshIfStale`) entram nas fatias 6b, 6c, 8 e 12.
 */

import { MESSAGES } from './messages.js';
import { fetchWeather } from './services/api.js';
import * as cache from './services/cache.js';
import { getState, setState } from './state.js';

export const SLOW_AFTER_MS = 3_000; // "Ainda carregando…" (RN-012)

/** Cidade padrão: Uberlândia, BR (RN-001). */
export const DEFAULT_CITY = Object.freeze({
  lat: -18.9186,
  lon: -48.2772,
  headerLabel: MESSAGES.defaultCity.headerLabel,
  markerLabel: MESSAGES.defaultCity.markerLabel,
  source: 'default',
});

/**
 * Torna `city` a cidade selecionada e obtém o clima dela (RF-004, RF-005, RN-013).
 * Com dado válido no cache, ele aparece na hora, sem consulta e sem carregamento (RN-010,
 * RNF-002). Sem cache, o status fica `loading` até a resposta.
 * @param {import('./state.js').City} city
 * @returns {Promise<void>} termina quando a consulta termina
 */
export function selectCity(city) {
  const selectionId = getState().selectionId + 1;
  const cached = cache.get(cache.cacheKey(city.lat, city.lon), Date.now());
  const common = { city, selectionId, selectedDay: null, weatherError: null };
  if (cached) {
    setState({
      ...common,
      weather: cached.value,
      fetchedAt: cached.storedAt,
      weatherStatus: 'ready',
    });
    return Promise.resolve();
  }
  setState({ ...common, weather: null, fetchedAt: null, weatherStatus: 'loading' });
  return loadWeather(city, selectionId);
}

/**
 * "Tentar novamente": refaz só a consulta de clima que falhou, da cidade atual (RN-013,
 * RF-013). Fora do estado de erro não faz nada, então vários cliques geram uma única
 * consulta (RF-015).
 * @returns {Promise<void>}
 */
export function retry() {
  const { city, selectionId, weatherStatus } = getState();
  if (weatherStatus !== 'error' || !city) return Promise.resolve();
  setState({ weatherStatus: 'loading', weatherError: null });
  return loadWeather(city, selectionId);
}

async function loadWeather(city, selectionId) {
  const isCurrent = () => getState().selectionId === selectionId;
  const slowTimer = setTimeout(() => {
    if (isCurrent() && getState().weatherStatus === 'loading') {
      setState({ weatherStatus: 'slow' });
    }
  }, SLOW_AFTER_MS);

  try {
    const result = await fetchWeather(city.lat, city.lon);
    const receivedAt = Date.now();
    // Só sucesso vai para o cache (RN-011). A resposta de uma cidade anterior também vai:
    // voltar a ela em menos de 10 min não gera outra consulta (P-010, D-18).
    if (result.ok) cache.set(cache.cacheKey(city.lat, city.lon), result.data, receivedAt);
    if (!isCurrent()) return; // a cidade mudou: a resposta é descartada (P-012)
    setState(
      result.ok
        ? { weather: result.data, fetchedAt: receivedAt, weatherStatus: 'ready' }
        : { weatherStatus: 'error', weatherError: result.error },
    );
  } finally {
    clearTimeout(slowTimer);
  }
}
