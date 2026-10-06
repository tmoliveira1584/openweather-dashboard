/**
 * Cache das consultas de clima, só na memória da página (RN-010, P-010, ADR-005).
 *
 * Some ao recarregar a página: nada vai para `localStorage`, `sessionStorage`, IndexedDB
 * ou cookies (P-007). Quem chama grava só respostas de sucesso (RN-011).
 */

export const CACHE_TTL_MS = 10 * 60 * 1000; // 10 min a partir do recebimento (RN-010)

const entries = new Map();

/**
 * Coordenada com 2 casas decimais, em texto, sem "-0.00". É a mesma usada no `/api/weather`
 * (arquitetura, seção 7.4).
 * @param {number} value
 * @returns {string}
 */
export function roundCoord(value) {
  const text = Number(value).toFixed(2);
  return text === '-0.00' ? '0.00' : text;
}

/**
 * Chave do cache: as coordenadas arredondadas a 2 casas, cerca de 1 km (RN-010).
 * @param {number} lat
 * @param {number} lon
 * @returns {string}
 */
export function cacheKey(lat, lon) {
  return `${roundCoord(lat)},${roundCoord(lon)}`;
}

/**
 * Dado guardado e ainda válido (menos de 10 min), ou `null`. O vencido sai do cache.
 * @param {string} key
 * @param {number} nowMs
 * @returns {{ value: unknown, storedAt: number } | null}
 */
export function get(key, nowMs) {
  const entry = entries.get(key);
  if (!entry) return null;
  if (nowMs - entry.storedAt >= CACHE_TTL_MS) {
    entries.delete(key);
    return null;
  }
  return entry;
}

/**
 * Guarda a resposta. A validade conta a partir de `nowMs`, o momento do recebimento.
 * @param {string} key
 * @param {unknown} value
 * @param {number} nowMs
 */
export function set(key, value, nowMs) {
  entries.set(key, Object.freeze({ value, storedAt: nowMs }));
}
