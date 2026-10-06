/**
 * Geometria dos gráficos em SVG próprio (ADR-007, seção 6.6): escala e caminho da curva por
 * hora, etiquetas de chuva sobre ela e altura das barras por minuto.
 *
 * Funções puras, sem DOM: as posições e larguras chegam por parâmetro, nas unidades de quem
 * desenha.
 */

// Teto visual das barras por minuto, em mm/h (RN-042).
export const BAR_CEILING = 10;

/**
 * Posição vertical de cada temperatura na faixa da curva (RN-039). A maior fica em `top` e a
 * menor em `bottom` (o eixo y do SVG cresce para baixo), e o espaço fora da faixa fica de
 * folga para as etiquetas. Com todas iguais, todas ficam no centro, e a curva é uma linha
 * reta. Temperatura ausente não ganha posição (P-013).
 * @param {(number | null)[]} values temperaturas, sem arredondar
 * @param {number} top
 * @param {number} bottom
 * @returns {(number | null)[]}
 */
export function scaleY(values, top, bottom) {
  const numbers = values.filter(Number.isFinite);
  const min = Math.min(...numbers);
  const max = Math.max(...numbers);
  return values.map((value) => {
    if (!Number.isFinite(value)) return null;
    if (max === min) return (top + bottom) / 2;
    return bottom - ((value - min) / (max - min)) * (bottom - top);
  });
}

/**
 * Caminho SVG suave pelos pontos, com interpolação cúbica monotônica (Fritsch–Carlson,
 * ADR-007). Em cada trecho, os pontos de controle ficam entre os dois pontos, então a curva
 * nunca passa da mínima nem da máxima reais (RN-039). Um ponto sem `y` interrompe a curva,
 * que continua no ponto seguinte (P-013).
 * @param {{ x: number, y: number | null }[]} points em ordem crescente de `x`
 * @returns {string} atributo `d` (`M` e `C`), ou texto vazio sem pontos
 */
export function monotonePath(points) {
  const runs = [[]];
  for (const point of points) {
    if (Number.isFinite(point.y)) runs.at(-1).push(point);
    else if (runs.at(-1).length) runs.push([]);
  }
  return runs
    .filter((run) => run.length)
    .map(runPath)
    .join(' ');
}

/** Subcaminho de um trecho contínuo: `M` no primeiro ponto e uma cúbica até cada um dos demais. */
function runPath(points) {
  const slopes = tangents(points);
  const parts = [`M${coord(points[0])}`];
  for (let i = 0; i < points.length - 1; i += 1) {
    const [a, b] = [points[i], points[i + 1]];
    const third = (b.x - a.x) / 3;
    const start = { x: a.x + third, y: a.y + slopes[i] * third };
    const end = { x: b.x - third, y: b.y - slopes[i + 1] * third };
    parts.push(`C${coord(start)} ${coord(end)} ${coord(b)}`);
  }
  return parts.join(' ');
}

/**
 * Inclinação da curva em cada ponto (Fritsch e Carlson, 1980): a média das secantes vizinhas,
 * zero nos picos, vales e platôs, e reduzida quando passaria da razão 3 em relação à secante.
 * Assim, cada trecho é monotônico entre os seus dois pontos.
 */
function tangents(points) {
  const n = points.length;
  if (n < 2) return [0];
  const secants = [];
  for (let i = 0; i < n - 1; i += 1) {
    secants.push((points[i + 1].y - points[i].y) / (points[i + 1].x - points[i].x));
  }
  const slopes = [secants[0]];
  for (let i = 1; i < n - 1; i += 1) {
    const [before, after] = [secants[i - 1], secants[i]];
    slopes.push(before * after <= 0 ? 0 : (before + after) / 2);
  }
  slopes.push(secants[n - 2]);

  for (let i = 0; i < n - 1; i += 1) {
    if (secants[i] === 0) {
      slopes[i] = 0;
      slopes[i + 1] = 0;
      continue;
    }
    const alpha = slopes[i] / secants[i];
    const beta = slopes[i + 1] / secants[i];
    const length = Math.hypot(alpha, beta);
    if (length > 3) {
      slopes[i] = (3 / length) * alpha * secants[i];
      slopes[i + 1] = (3 / length) * beta * secants[i];
    }
  }
  return slopes;
}

/** Par `x,y` com até 3 casas, para o caminho ficar curto. */
function coord({ x, y }) {
  return `${Number(x.toFixed(3))},${Number(y.toFixed(3))}`;
}

/**
 * Etiquetas de chuva que ficam visíveis (RN-038). Da etiqueta de maior volume para a de
 * menor, cada uma só aparece se ficar a pelo menos `minGapPx` de todas as que já estão
 * visíveis. Assim, nenhuma etiqueta visível se sobrepõe a outra, e cada oculta fica no grupo
 * de uma visível de volume maior ou igual, sempre a de maior volume do grupo. No empate, vale
 * a hora mais cedo. As ocultas aparecem no ponto da curva (RF-036).
 * @param {{ x: number, width: number, value: number }[]} items centro e largura de cada
 *   etiqueta, em px, e o volume de chuva, na ordem das horas
 * @param {number} minGapPx espaço mínimo entre duas etiquetas visíveis
 * @returns {boolean[]} se cada etiqueta fica visível, na ordem de `items`
 */
export function groupRainLabels(items, minGapPx) {
  const byVolume = items
    .map((item, index) => ({ ...item, index }))
    .sort((a, b) => b.value - a.value || a.index - b.index);
  const shown = [];
  for (const item of byVolume) {
    const clear = shown.every(
      (other) => Math.abs(other.x - item.x) >= (other.width + item.width) / 2 + minGapPx,
    );
    if (clear) shown.push(item);
  }
  const visible = items.map(() => false);
  for (const item of shown) visible[item.index] = true;
  return visible;
}

/**
 * Altura da barra de um minuto (RN-042): proporcional à intensidade, com teto em 10 mm/h
 * (valores maiores ocupam `maxPx`). Intensidade 0, ou tão pequena que ficaria abaixo de
 * `minPx`, fica com a altura mínima visível. Sem intensidade, nenhuma barra (RN-047).
 * @param {number | null} intensity mm/h
 * @param {number} maxPx altura máxima, nas unidades de quem desenha
 * @param {number} minPx altura mínima visível
 * @returns {number}
 */
export function barHeight(intensity, maxPx, minPx) {
  if (!Number.isFinite(intensity) || intensity < 0) return 0;
  return Math.max(minPx, (Math.min(intensity, BAR_CEILING) / BAR_CEILING) * maxPx);
}
