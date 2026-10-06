/**
 * Resumos em texto que dependem da janela de tempo (ADR-004, seção 6.6).
 *
 * Funções puras: recebem a janela já recortada por `logic/time-window.js`. Os textos fixos
 * vêm do `messages.js` (guardrail 10); os valores, prontos do view model, na escala ativa.
 *
 * Resumos: o texto alternativo da curva por hora e o da próxima hora, na previsão por
 * minuto.
 */

import { MESSAGES } from '../messages.js';

/**
 * Texto alternativo da curva de temperatura (RNF-016): a mínima e a máxima da janela, com a
 * hora de cada uma, na escala ativa (RN-040). A comparação usa a temperatura sem arredondar
 * e, no empate, vale a hora mais cedo. Uma hora sem temperatura é ignorada (P-013). Com a
 * mesma temperatura exibida em todas as horas, diz que ela está estável (D-23).
 * @param {{ hour_label: string, temp: Record<string, string>,
 *           temp_value: Record<string, number | null> }[]} window resultado de `hourlyWindow`
 * @param {'c' | 'f'} scale
 * @returns {string | null} `null` sem nenhuma temperatura, quando não há curva
 */
export function hourlyAltText(window, scale) {
  let min = null;
  let max = null;
  for (const hour of window) {
    const value = hour.temp_value[scale];
    if (!Number.isFinite(value)) continue;
    if (!min || value < min.temp_value[scale]) min = hour;
    if (!max || value > max.temp_value[scale]) max = hour;
  }
  if (!min) return null;

  const { hourly } = MESSAGES;
  const period = hourly.period(window.length);
  const [low, high] = [min.temp[scale], max.temp[scale]];
  return low === high
    ? hourly.steadyText(period, low)
    : hourly.altText(period, low, min.hour_label, high, max.hour_label);
}

/**
 * Resumo da próxima hora (RF-043, RN-044). "Chuva" é intensidade maior que 0:
 * - nenhum minuto com chuva: "Sem chuva prevista na próxima hora.";
 * - o primeiro minuto sem chuva: "Chuva prevista a partir de HH:MM.", no primeiro com chuva;
 * - chuva no primeiro minuto: "Chuva agora, parando por volta de HH:MM.", no primeiro minuto
 *   com intensidade 0, ou "Chuva durante toda a próxima hora." se nenhum tiver 0.
 * Um minuto sem intensidade não conta como chuva nem como estiagem (RN-047, P-013, D-24).
 * @param {{ time_label: string, intensity: number | null }[]} window resultado de
 *   `minuteWindow`
 * @returns {string | null} `null` sem nenhuma intensidade
 */
export function minuteSummary(window) {
  if (!window.some((minute) => Number.isFinite(minute.intensity))) return null;
  const { summary } = MESSAGES.minutely;
  const rain = window.find((minute) => minute.intensity > 0);
  if (!rain) return summary.dry;
  if (rain !== window[0]) return summary.startsAt(rain.time_label);
  const stop = window.find((minute) => minute.intensity === 0);
  return stop ? summary.stopsAt(stop.time_label) : summary.allHour;
}
