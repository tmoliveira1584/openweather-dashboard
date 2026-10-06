/**
 * Mapa de precipitação (arquitetura, seções 5.1 e 7.2; ADR-006; feature 6): mapa base do
 * CARTO, camada de chuva pelo proxy do backend, marcador com o nome da cidade, atribuições e
 * os avisos de falha.
 *
 * O mapa só acompanha a cidade selecionada. Interagir com ele não chama nenhuma ação, então
 * não muda a cidade nem gera consulta de clima (RN-051), e a escala e os dados de clima não
 * mexem nele. Ele não depende do estado da consulta de clima: uma falha no clima não afeta
 * o mapa, e uma falha no mapa não afeta os demais blocos (P-021).
 *
 * O Leaflet é o objeto global `L`, carregado antes pelo `index.html` (ADR-006). Só este
 * módulo o usa (seção 5.2).
 */

import { MESSAGES } from '../messages.js';
import { getState, subscribe } from '../state.js';
import { el, setText } from './dom.js';

const BASE_URL = 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png';
const RAIN_URL = '/api/tiles/precipitation/{z}/{x}/{y}.png';
const ZOOM = Object.freeze({ initial: 6, min: 3, max: 10 }); // RN-048
const RAIN_OPACITY = 0.6; // RN-049
const MARKER_SIZE = 20; // px do círculo do marcador
const HINT_MS = 1_500; // tempo da dica dos dois dedos (RN-052)
const HINT_MOVE_PX = 10; // movimento de um dedo que conta como tentativa de mover o mapa

/**
 * Monta o bloco e passa a acompanhar a cidade selecionada. O mapa é criado na primeira
 * cidade: antes dela, o bloco mostra só o fundo (seção 7.2).
 * @param {HTMLElement} root o `#map`, contêiner do Leaflet
 */
export function mount(root) {
  const notices = {
    unavailable: notice('map-unavailable', MESSAGES.map.unavailable),
    rain: notice('map-rain-unavailable', MESSAGES.map.rainUnavailable),
    hint: notice('map-hint', MESSAGES.map.twoFingers),
  };
  root.append(notices.rain, notices.hint, notices.unavailable);

  const leaflet = globalThis.L;
  if (!leaflet) {
    // Sem o Leaflet, o bloco mostra só a mensagem, e os demais seguem (RF-051, P-021).
    notices.unavailable.hidden = false;
    return;
  }

  let view = null;
  const show = (city) => {
    if (!city) return;
    view ??= createMap(leaflet, root, city, notices);
    view.center(city);
    root.setAttribute('aria-label', MESSAGES.map.label(city.markerLabel));
  };
  subscribe((state, previous) => {
    if (state.city !== previous.city) show(state.city);
  });
  show(getState().city);
}

/** Aviso sobre o mapa (falha ou dica), oculto de início. */
function notice(className, text) {
  return el('p', { class: `map-notice ${className}`, text, attrs: { role: 'status', hidden: '' } });
}

/**
 * Cria o mapa na cidade, com as duas camadas, o marcador, os controles e os avisos.
 * @returns {{ center(city: import('../state.js').City): void }}
 */
function createMap(leaflet, root, city, notices) {
  const touchScreen = matchMedia('(pointer: coarse)').matches;
  const map = leaflet.map(root, {
    center: [city.lat, city.lon],
    zoom: ZOOM.initial,
    minZoom: ZOOM.min,
    maxZoom: ZOOM.max,
    // Em telas de toque, um dedo rola a página e dois movem o mapa (RN-052, seção 7.2).
    dragging: !touchScreen,
    touchZoom: true,
    zoomControl: false,
    attributionControl: false,
  });

  leaflet.control
    .zoom({ zoomInTitle: MESSAGES.map.zoomIn, zoomOutTitle: MESSAGES.map.zoomOut })
    .addTo(map);
  attributionControl(leaflet).addTo(map);

  // O Leaflet só pede as tiles da área visível (RNF-023).
  const base = leaflet.tileLayer(BASE_URL, { subdomains: 'abcd' }).addTo(map);
  const rain = leaflet.tileLayer(RAIN_URL, { opacity: RAIN_OPACITY }).addTo(map);
  watchBaseLayer(base, notices);
  watchRainLayer(rain, notices);
  if (touchScreen) watchOneFinger(root, notices.hint);

  const label = el('span', { class: 'map-marker-name' });
  const marker = leaflet
    .marker([city.lat, city.lon], {
      icon: leaflet.divIcon({ className: 'map-marker', iconSize: [MARKER_SIZE, MARKER_SIZE] }),
      interactive: false,
      keyboard: false,
    })
    // O rótulo recebe um elemento, não uma string: o Leaflet trataria a string como HTML,
    // e o nome da cidade vem de fora (P-003).
    .bindTooltip(label, {
      permanent: true,
      direction: 'top',
      offset: [0, -MARKER_SIZE / 2],
      className: 'map-marker-label',
    })
    .addTo(map);

  return {
    /** Centraliza na cidade com o zoom inicial e move o marcador (RF-046, RF-048, RN-050). */
    center({ lat, lon, markerLabel }) {
      map.setView([lat, lon], ZOOM.initial, { animate: false });
      marker.setLatLng([lat, lon]);
      setText(label, markerLabel);
      marker.getTooltip().update();
    },
  };
}

/**
 * Atribuições do mapa base e da camada de chuva no canto inferior direito (RF-050, RNF-025,
 * P-019). Os textos vêm do `messages.js` e entram por `textContent`.
 */
function attributionControl(leaflet) {
  const Attribution = leaflet.Control.extend({
    options: { position: 'bottomright' },
    onAdd() {
      const parts = MESSAGES.map.attribution.map((part) =>
        typeof part === 'string'
          ? document.createTextNode(part)
          : el('a', {
              text: part.text,
              attrs: { href: part.href, target: '_blank', rel: 'noopener noreferrer' },
            }),
      );
      const node = el('div', { class: 'leaflet-control-attribution map-attribution' }, parts);
      leaflet.DomEvent.disableClickPropagation(node);
      return node;
    },
  });
  return new Attribution();
}

/**
 * Mapa base fora do ar (RF-051): num ciclo de carregamento sem nenhuma tile carregada e com
 * pelo menos uma falha, o mapa é coberto pela mensagem. Algumas tiles com falha deixam só
 * essas áreas em branco (feature 6, categoria 9). Um ciclo seguinte com tiles carregadas,
 * como o da troca de cidade, tira a mensagem.
 */
function watchBaseLayer(layer, notices) {
  let loaded = 0;
  let failed = 0;
  layer.on('loading', () => {
    loaded = 0;
    failed = 0;
  });
  layer.on('tileload', () => {
    loaded += 1;
  });
  layer.on('tileerror', () => {
    failed += 1;
  });
  layer.on('load', () => {
    if (loaded) notices.unavailable.hidden = true;
    else if (failed) notices.unavailable.hidden = false;
  });
}

/**
 * Camada de chuva fora do ar ou com a cota excedida (RF-052): a faixa aparece no primeiro
 * erro e some no próximo carregamento sem erro. O mapa base e o marcador continuam.
 */
function watchRainLayer(layer, notices) {
  let failed = false;
  layer.on('loading', () => {
    failed = false;
  });
  layer.on('tileerror', () => {
    failed = true;
    notices.rain.hidden = false;
  });
  layer.on('load', () => {
    if (!failed) notices.rain.hidden = true;
  });
}

/**
 * Dica dos dois dedos (RN-052): quando um único dedo tenta mover o mapa, a página rola e a
 * dica aparece por 1,5 s. A tentativa é o toque cancelado pelo navegador para rolar a página
 * ou um movimento de mais de 10 px.
 */
function watchOneFinger(container, hint) {
  const touches = new Map(); // pointerId → ponto inicial
  let timer = null;
  const showHint = () => {
    hint.hidden = false;
    clearTimeout(timer);
    timer = setTimeout(() => {
      hint.hidden = true;
    }, HINT_MS);
  };
  const alone = (event) => touches.size === 1 && touches.has(event.pointerId);

  container.addEventListener('pointerdown', (event) => {
    if (event.pointerType === 'touch') {
      touches.set(event.pointerId, { x: event.clientX, y: event.clientY });
    }
  });
  container.addEventListener('pointermove', (event) => {
    if (!alone(event)) return;
    const start = touches.get(event.pointerId);
    if (Math.hypot(event.clientX - start.x, event.clientY - start.y) > HINT_MOVE_PX) showHint();
  });
  container.addEventListener('pointercancel', (event) => {
    if (alone(event)) showHint();
    touches.delete(event.pointerId);
  });
  container.addEventListener('pointerup', (event) => {
    touches.delete(event.pointerId);
  });
}
