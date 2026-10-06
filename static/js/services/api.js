/**
 * Chamadas ao próprio backend (`/api`), nunca ao OpenWeatherMap (guardrail 3, ADR-003).
 *
 * Toda função devolve `{ ok: true, data }` ou `{ ok: false, error }`, com `error` sendo um
 * código da seção 6.4 ou `server_unreachable`. O corpo de um erro nunca chega à tela (P-004).
 */

import { roundCoord } from './cache.js';

// Trava de segurança: o backend desiste em 15 s, e esta trava cobre o caso de ele não
// responder (RN-012, arquitetura, seção 7.4).
export const REQUEST_GUARD_MS = 17_000;

const KNOWN_ERRORS = new Set([
  'invalid_request',
  'provider_unauthorized',
  'provider_rate_limited',
  'provider_unavailable',
  'provider_timeout',
  'network_unavailable',
]);

// Promessas em andamento por URL: pedidos idênticos recebem a mesma (RF-015).
const inFlight = new Map();

/**
 * Consulta de clima da coordenada, arredondada a 2 casas como a chave do cache (RN-010, P-008).
 * @param {number} lat
 * @param {number} lon
 */
export function fetchWeather(lat, lon) {
  return request(`/api/weather?lat=${roundCoord(lat)}&lon=${roundCoord(lon)}`);
}

/**
 * Busca de cidades. O termo vai como texto, codificado na query string (RN-004, P-003).
 * @param {string} q
 */
export function searchCities(q) {
  return request(`/api/geo/search?q=${encodeURIComponent(q)}`);
}

/**
 * Nome da cidade da localização (RF-002, RN-009).
 * @param {number} lat
 * @param {number} lon
 */
export function reverseGeocode(lat, lon) {
  return request(
    `/api/geo/reverse?lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}`,
  );
}

function request(url) {
  const pending = inFlight.get(url);
  if (pending) return pending;
  const promise = send(url).finally(() => inFlight.delete(url));
  inFlight.set(url, promise);
  return promise;
}

async function send(url) {
  const controller = new AbortController();
  const guard = setTimeout(() => controller.abort(), REQUEST_GUARD_MS);
  try {
    const response = await fetch(url, {
      signal: controller.signal,
      headers: { Accept: 'application/json' },
    });
    const body = await response.json().catch(() => undefined);
    if (response.ok && body !== undefined) return { ok: true, data: body };
    const code = body?.error;
    return { ok: false, error: KNOWN_ERRORS.has(code) ? code : 'provider_unavailable' };
  } catch {
    if (controller.signal.aborted) return { ok: false, error: 'provider_timeout' };
    // O backend é local: sem rede no navegador, a falha é a conexão (seção 7.3).
    return {
      ok: false,
      error: navigator.onLine === false ? 'network_unavailable' : 'server_unreachable',
    };
  } finally {
    clearTimeout(guard);
  }
}
