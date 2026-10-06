/**
 * Localização do dispositivo, só pelo pedido de permissão do navegador (P-005; arquitetura,
 * seção 7.4).
 *
 * O prazo é um `setTimeout` próprio, contado a partir do pedido: a opção `timeout` da API não
 * conta o tempo em que o usuário decide sobre a permissão, por isso não é usada. O pedido não é
 * cancelado no fim do prazo: se a coordenada chegar depois, ela vai para `onLate` (RN-003).
 */

/**
 * @typedef {{ status: 'ok', lat: number, lon: number }} Located
 * @typedef {{ status: 'unavailable' }} Unavailable
 */

const OPTIONS = Object.freeze({ enableHighAccuracy: false, maximumAge: 600_000 });
const UNAVAILABLE = Object.freeze({ status: 'unavailable' });

/**
 * Pede a localização ao navegador (RF-001, RN-002).
 * - Coordenada dentro do prazo → `{ status: 'ok', lat, lon }`.
 * - Permissão negada, falha, prazo vencido, navegador sem o recurso ou página fora de
 *   contexto seguro → `{ status: 'unavailable' }`.
 * - Coordenada depois do prazo → `onLate({ status: 'ok', lat, lon })`.
 * @param {{ timeoutMs: number, onLate?: (location: Located) => void }} options
 * @returns {Promise<Located | Unavailable>}
 */
export function requestLocation({ timeoutMs, onLate }) {
  const geolocation = window.isSecureContext ? navigator.geolocation : undefined;
  if (!geolocation) return Promise.resolve(UNAVAILABLE);

  return new Promise((resolve) => {
    let expired = false;
    const timer = setTimeout(() => {
      expired = true;
      resolve(UNAVAILABLE);
    }, timeoutMs);
    const answer = (result) => {
      clearTimeout(timer);
      resolve(result);
    };

    geolocation.getCurrentPosition(
      ({ coords }) => {
        const location = { status: 'ok', lat: coords.latitude, lon: coords.longitude };
        if (expired) onLate?.(location);
        else answer(location);
      },
      () => {
        if (!expired) answer(UNAVAILABLE);
      },
      OPTIONS,
    );
  });
}
