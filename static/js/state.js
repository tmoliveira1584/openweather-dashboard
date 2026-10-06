/**
 * Estado único do frontend (arquitetura, seção 6.5).
 *
 * Só `actions.js` muda o estado. Os blocos de `ui/` assinam e redesenham a cada mudança.
 * Nada daqui é persistido: o estado some ao recarregar a página (RN-058, P-007).
 */

/**
 * @typedef {{ lat: number, lon: number, headerLabel: string, markerLabel: string,
 *             source: 'geolocation' | 'default' | 'search' }} City
 * @typedef {'idle'|'loading'|'slow'|'ready'|'refreshing'|'error'} WeatherStatus
 */

const initialState = Object.freeze({
  city: null, // City | null
  selectionId: 0, // aumenta a cada troca de cidade (P-012)
  scale: 'c', // 'c' | 'f' (RF-054). Nunca persistido (RN-058)
  selectedDay: null, // local_date da aba ativa. null = "Hoje" (RF-025, RF-031)
  weather: null, // WeatherView | null
  weatherStatus: 'idle', // 'slow' = mais de 3 s ("Ainda carregando…", RN-012)
  weatherError: null, // código da seção 6.4 | 'server_unreachable' | null
  fetchedAt: null, // ms do recebimento, para RF-014
  locationNotice: false, // aviso de cidade padrão (RF-003, RN-002)
  search: Object.freeze({ status: 'idle', results: [], truncated: false, message: null }),
  // status: 'idle' | 'loading' | 'open' | 'empty' | 'error'
});

let state = initialState;
const listeners = new Set();

/**
 * Estado atual. É congelado: para mudar, use `setState`.
 * @returns {Readonly<typeof initialState>}
 */
export function getState() {
  return state;
}

/**
 * Cria um estado novo com as chaves do patch e avisa os assinantes.
 * @param {Partial<typeof initialState>} patch
 */
export function setState(patch) {
  const previous = state;
  state = Object.freeze({ ...state, ...patch });
  for (const listener of [...listeners]) listener(state, previous);
}

/**
 * Passa a avisar `listener(state, previous)` a cada mudança.
 * @param {(state: object, previous: object) => void} listener
 * @returns {() => void} função que cancela a assinatura
 */
export function subscribe(listener) {
  listeners.add(listener);
  return () => listeners.delete(listener);
}
