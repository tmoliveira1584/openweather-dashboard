/**
 * Janelas de tempo que dependem do "agora" sobre dados em cache (ADR-004, seção 6.6).
 *
 * Funções puras: o "agora" chega por parâmetro (`nowSec`, em segundos Unix), nunca por
 * `Date.now()` (guardrail 9). Datas e horas no fuso da cidade: `(ts + offset)` lido em UTC
 * (seção 7.5).
 *
 * Janelas: os dias da previsão diária, as horas da previsão hora a hora e os minutos da
 * previsão por minuto, com os marcos.
 */

import { MESSAGES } from '../messages.js';

export const MAX_DAYS = 8; // "Hoje" mais 7 (RN-027)
export const MAX_HOURS = 24; // RN-034
export const MAX_MINUTES = 60; // a próxima hora (RF-039)
export const MARK_STEP = 15; // minutos entre dois marcos (RN-043)

const HOUR_SEC = 3600;
const MINUTE_SEC = 60;

/** Horário `HH:MM` no fuso da cidade, como o `time_label` do backend (RN-015, P-015). */
function timeLabel(ts, offset) {
  return new Date((ts + offset) * 1000).toISOString().slice(11, 16);
}

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

/**
 * Minutos da previsão por minuto: começa no primeiro minuto que ainda não passou e vai, em
 * ordem, até o último recebido, no máximo 60 (RF-039, RN-047). Um minuto que falta no meio
 * da série (registro sem `dt`, descartado pelo backend) ocupa o lugar dele, sem intensidade:
 * a barra fica vazia e o cursor mostra "—". Sem previsão por minuto, nenhum.
 * @template {{ dt: number, time_label: string, intensity: number | null,
 *              band: string | null, tooltip: string }} Minute
 * @param {Minute[] | null} minutely `WeatherView.minutely`
 * @param {number} nowSec agora, em segundos Unix
 * @param {number} offset fuso da cidade, em segundos em relação ao UTC
 * @returns {Minute[]}
 */
export function minuteWindow(minutely, nowSec, offset) {
  if (!minutely) return [];
  const coming = new Map();
  for (const minute of minutely) {
    if (minute.dt + MINUTE_SEC > nowSec) coming.set(minute.dt, minute);
  }
  if (!coming.size) return [];
  const first = Math.min(...coming.keys());
  const last = Math.max(...coming.keys());
  const count = Math.min(MAX_MINUTES, Math.floor((last - first) / MINUTE_SEC) + 1);
  return Array.from({ length: count }, (_, k) => {
    const dt = first + k * MINUTE_SEC;
    return coming.get(dt) ?? missingMinute(dt, offset);
  });
}

/** Minuto sem registro: sem intensidade nem faixa, e "HH:MM — —" no cursor (RN-047). */
function missingMinute(dt, offset) {
  const time = timeLabel(dt, offset);
  return {
    dt,
    time_label: time,
    intensity: null,
    band: null,
    tooltip: MESSAGES.minutely.missingTooltip(time),
  };
}

/**
 * Marcos da previsão por minuto: "Agora", "15 min", "30 min", "45 min" e "60 min", nos
 * minutos 0, 15, 30, 45 e 60 da janela, com o horário no fuso da cidade (RF-041, RN-043,
 * P-015). O marco de k minutos só aparece com pelo menos k barras, e o de "Agora", com pelo
 * menos 1 (RN-047). A posição vai de 0 (início da primeira barra) a 1 (fim da última): cada
 * marco fica no início do seu minuto, e o de 60 min, no fim da última barra.
 * @param {{ dt: number }[]} window resultado de `minuteWindow`
 * @param {number} offset
 * @returns {{ label: string, time: string, position: number }[]}
 */
export function minuteMarks(window, offset) {
  const count = window.length;
  return MESSAGES.minutely.marks
    .map((label, index) => ({ label, minute: index * MARK_STEP }))
    .filter(({ minute }) => count >= Math.max(minute, 1))
    .map(({ label, minute }) => ({
      label,
      time: timeLabel(window[0].dt + minute * MINUTE_SEC, offset),
      position: minute / count,
    }));
}
