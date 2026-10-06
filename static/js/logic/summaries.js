/**
 * Resumos em texto que dependem da janela de tempo (ADR-004, seção 6.6).
 *
 * Funções puras: recebem a janela já recortada por `logic/time-window.js`. Os textos fixos
 * vêm do `messages.js` (guardrail 10); os valores, prontos do view model, na escala ativa.
 *
 * Até aqui: o texto alternativo da curva por hora (fatia 9). O resumo da próxima hora
 * (`minuteSummary`) entra na fatia 10.
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
