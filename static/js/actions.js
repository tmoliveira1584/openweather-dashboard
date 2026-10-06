/**
 * Fluxos da aplicação: a única camada que muda o estado (arquitetura, seções 2.2 e 6.6).
 *
 * Até aqui: `selectCity` e `retry` (fatia 6a), busca e escala (fatia 6b), localização inicial
 * e aviso de localização (fatia 6c). Os demais fluxos (`selectDay`, `refreshIfStale`) entram
 * nas fatias 8 e 12.
 */

import { MESSAGES } from './messages.js';
import { fetchWeather, reverseGeocode, searchCities } from './services/api.js';
import * as cache from './services/cache.js';
import { requestLocation } from './services/location.js';
import { getState, setState } from './state.js';

export const LOCATION_TIMEOUT_MS = 10_000; // prazo da localização, a partir do pedido (RN-002)
export const SLOW_AFTER_MS = 3_000; // "Ainda carregando…" (RN-012)
export const SEARCH_MAX_LENGTH = 100; // o campo não aceita mais caracteres (RN-004)
const SEARCH_MIN_LENGTH = 2; // sem os espaços das pontas (RN-004)
const SCALES = new Set(['c', 'f']);
const SEARCH_IDLE = Object.freeze({ status: 'idle', results: [], truncated: false, message: null });

/** Cidade padrão: Uberlândia, BR (RN-001). */
export const DEFAULT_CITY = Object.freeze({
  lat: -18.9186,
  lon: -48.2772,
  headerLabel: MESSAGES.defaultCity.headerLabel,
  markerLabel: MESSAGES.defaultCity.markerLabel,
  source: 'default',
});

/**
 * Abertura da página: pede a localização e seleciona a cidade dela ou a cidade padrão
 * (RF-001 a RF-003, RN-001, RN-002).
 * - Localização obtida no prazo: o nome vem da geocodificação reversa, ou "Sua localização"
 *   se ela falhar ou não trouxer um nome (RF-002, RN-009).
 * - Negada, indisponível ou sem resposta em 10 s: cidade padrão com o aviso de localização.
 * - Localização que chega depois do prazo: substitui a cidade padrão, se ela ainda estiver
 *   selecionada (RN-003).
 * - A busca funciona com o pedido pendente, e a cidade escolhida nela prevalece (P-009).
 * @returns {Promise<void>} termina quando a primeira consulta de clima termina
 */
export async function start() {
  const location = await requestLocation({
    timeoutMs: LOCATION_TIMEOUT_MS,
    onLate: applyLateLocation,
  });
  if (getState().city) return; // a busca já escolheu uma cidade (P-009)
  if (location.status === 'ok') return selectLocation(location);
  setState({ locationNotice: true });
  return selectCity(DEFAULT_CITY);
}

/**
 * Localização tardia: substitui a cidade padrão. Se o usuário já escolheu outra cidade, ela é
 * descartada (RN-003).
 */
function applyLateLocation(location) {
  if (getState().city?.source === 'default') selectLocation(location);
}

/**
 * Seleciona a coordenada do dispositivo com o nome da geocodificação reversa (RF-002, RN-009).
 * Se outra cidade for escolhida enquanto o nome é buscado, a localização é descartada
 * (RN-003, P-009).
 */
async function selectLocation({ lat, lon }) {
  const { selectionId } = getState();
  const result = await reverseGeocode(lat, lon);
  if (getState().selectionId !== selectionId) return;
  const place = result.ok ? result.data.result : null;
  return selectCity({
    lat,
    lon,
    headerLabel: place?.header_label || MESSAGES.location.unnamed,
    markerLabel: place?.marker_label || MESSAGES.location.unnamed,
    source: 'geolocation',
  });
}

/** Fecha o aviso de localização. A cidade selecionada continua a mesma (RN-002). */
export function dismissLocationNotice() {
  if (getState().locationNotice) setState({ locationNotice: false });
}

/**
 * Torna `city` a cidade selecionada e obtém o clima dela (RF-004, RF-005, RN-013).
 * Com dado válido no cache, ele aparece na hora, sem consulta e sem carregamento (RN-010,
 * RNF-002). Sem cache, o status fica `loading` até a resposta. Escolher uma cidade que não
 * seja a padrão fecha o aviso de localização (RN-002).
 * @param {import('./state.js').City} city
 * @returns {Promise<void>} termina quando a consulta termina
 */
export function selectCity(city) {
  const selectionId = getState().selectionId + 1;
  const cached = cache.get(cache.cacheKey(city.lat, city.lon), Date.now());
  const common = { city, selectionId, selectedDay: null, weatherError: null };
  if (city.source !== 'default') common.locationNotice = false;
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

// Busca em andamento ou com a lista aberta. `searchRun` aumenta a cada busca nova e a cada
// fechamento: a resposta de uma busca substituída ou fechada é descartada.
let searchRun = 0;
let currentSearch = null; // { term, promise }

/**
 * Busca cidades pelo termo (RF-006, RN-004, RN-005).
 * - Termo vazio ou com 1 caractere, sem os espaços das pontas: nenhuma consulta, status
 *   `invalid` com a mensagem do spec.
 * - O mesmo termo com a busca em andamento ou com a lista dele aberta: nada muda, e não há
 *   outra consulta (RF-015).
 * - Resultado: nenhuma cidade → `empty` com a mensagem (RF-012); uma → selecionada direto,
 *   sem lista (RF-007); mais → lista aberta (`open`). Falha → `error` com a mensagem do spec.
 *   Em todos os casos, a cidade selecionada só muda quando uma cidade é escolhida.
 * @param {string} term texto do campo, tratado sempre como texto (P-003)
 * @returns {Promise<void>} termina quando a busca termina
 */
export function search(term) {
  const text = String(term ?? '').trim();
  if (text.length < SEARCH_MIN_LENGTH) {
    discardSearch();
    const message = text ? MESSAGES.search.tooShort : MESSAGES.search.empty;
    setState({ search: { ...SEARCH_IDLE, status: 'invalid', message } });
    return Promise.resolve();
  }
  const { status } = getState().search;
  if (currentSearch?.term === text && (status === 'loading' || status === 'open')) {
    return currentSearch.promise;
  }
  const run = discardSearch();
  setState({ search: { ...SEARCH_IDLE, status: 'loading' } });
  const promise = runSearch(text, run);
  currentSearch = { term: text, promise };
  return promise;
}

/**
 * Fecha a lista ou a mensagem da busca, sem alterar a cidade selecionada (RF-011). Uma busca
 * em andamento é descartada.
 */
export function closeSearch() {
  discardSearch();
  if (getState().search.status !== 'idle') setState({ search: SEARCH_IDLE });
}

/**
 * Escolha de uma cidade da lista: fecha a lista e seleciona a cidade (RF-008). O campo é
 * limpo pelo cabeçalho, que vê a troca de cidade com origem `search`.
 * @param {{ lat: number, lon: number, header_label: string, marker_label: string }} result
 *   item de `CitySearchResult.results` (seção 6.3)
 * @returns {Promise<void>} termina quando a consulta de clima termina
 */
export function chooseSearchResult(result) {
  closeSearch();
  return selectCity({
    lat: result.lat,
    lon: result.lon,
    headerLabel: result.header_label,
    markerLabel: result.marker_label,
    source: 'search',
  });
}

/**
 * Troca a escala ativa. Muda só o estado: nenhuma consulta (RNF-027, P-011) e nada é
 * guardado (RN-058). Escolher a escala já ativa não muda nada.
 * @param {'c' | 'f'} scale
 */
export function setScale(scale) {
  if (SCALES.has(scale) && scale !== getState().scale) setState({ scale });
}

function discardSearch() {
  currentSearch = null;
  searchRun += 1;
  return searchRun;
}

async function runSearch(term, run) {
  const result = await searchCities(term);
  if (run !== searchRun) return; // fechada ou substituída por outra busca
  if (!result.ok) {
    setState({ search: { ...SEARCH_IDLE, status: 'error', message: MESSAGES.search.failed } });
    return;
  }
  const { results, truncated } = result.data;
  if (results.length === 0) {
    const message = MESSAGES.search.noResults(term);
    setState({ search: { ...SEARCH_IDLE, status: 'empty', message } });
  } else if (results.length === 1) {
    await chooseSearchResult(results[0]);
  } else {
    setState({ search: { status: 'open', results, truncated, message: null } });
  }
}
