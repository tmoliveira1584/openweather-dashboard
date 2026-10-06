/**
 * Janelas de tempo que dependem do "agora" sobre dados em cache (ADR-004, seção 6.6).
 *
 * Funções puras: o "agora" chega por parâmetro (`nowSec`, em segundos Unix), nunca por
 * `Date.now()` (guardrail 9). Datas e horas no fuso da cidade: `(ts + offset)` lido em UTC
 * (seção 7.5).
 *
 * Até aqui: os dias da previsão diária (fatia 8) e as horas da previsão hora a hora (fatia
 * 9). A janela por minuto entra na fatia 10.
 */

export const MAX_DAYS = 8; // "Hoje" mais 7 (RN-027)
export const MAX_HOURS = 24; // RN-034

const HOUR_SEC = 3600;

/**
 * Data atual da cidade, no formato `AAAA-MM-DD` de `daily[].local_date` (RN-026, P-015).
 * @param {number} nowSec agora, em segundos Unix
 * @param {number} offset fuso da cidade, em segundos em relação ao UTC
 * @returns {string}
 */
export function cityToday(nowSec, offset) {
  return new Date((nowSec + offset) * 1000).toISOString().slice(0, 10);
}

/**
 * Dias da previsão que viram abas: descarta os dias anteriores a "Hoje", ordena e limita a 8
 * (RN-026, RN-027, D-14). Sem previsão diária, nenhum dia.
 * @template {{ local_date: string }} Day
 * @param {Day[] | null} daily `WeatherView.daily`
 * @param {number} nowSec
 * @param {number} offset
 * @returns {Day[]}
 */
export function visibleDays(daily, nowSec, offset) {
  if (!daily) return [];
  const today = cityToday(nowSec, offset);
  return daily
    .filter((day) => day.local_date >= today)
    .sort((a, b) => a.local_date.localeCompare(b.local_date))
    .slice(0, MAX_DAYS);
}

/**
 * Dia que o card principal e os indicadores resumem (RF-026 a RF-028, seção 7.4):
 * - `null` ("Hoje") quando nenhum dia está selecionado ou o selecionado é a data de hoje: o
 *   bloco mostra as condições atuais;
 * - o dia selecionado, se ele ainda estiver entre os visíveis;
 * - `null` se ele virou passado ou não veio nos dados atualizados (feature 3, categoria 8).
 * @template {{ local_date: string }} Day
 * @param {Day[]} days resultado de `visibleDays`
 * @param {string | null} selectedDay `state.selectedDay`
 * @param {number} nowSec
 * @param {number} offset
 * @returns {Day | null}
 */
export function activeDay(days, selectedDay, nowSec, offset) {
  if (selectedDay == null || selectedDay === cityToday(nowSec, offset)) return null;
  return days.find((day) => day.local_date === selectedDay) ?? null;
}

/**
 * Horas da previsão hora a hora: começa na hora que contém o momento atual, descarta as que
 * já terminaram, ordena e limita a 24 (RN-034). Com menos de 24 disponíveis, só as
 * disponíveis; sem previsão hora a hora, nenhuma. Não depende da aba de dia (RF-029).
 * @template {{ dt: number }} Hour
 * @param {Hour[] | null} hourly `WeatherView.hourly`
 * @param {number} nowSec agora, em segundos Unix
 * @returns {Hour[]}
 */
export function hourlyWindow(hourly, nowSec) {
  if (!hourly) return [];
  return hourly
    .filter((hour) => hour.dt + HOUR_SEC > nowSec)
    .sort((a, b) => a.dt - b.dt)
    .slice(0, MAX_HOURS);
}
