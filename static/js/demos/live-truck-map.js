/* Live Truck Map, drawn like the dispatch screen it is: a fleet list on the
   left and a real map of the United States on the right. The whole fleet
   first sits in clusters across the country; the feed is polled, alerts
   stand out, the map flies to Texas where clusters break into single
   trucks, and picking a unit opens a Leaflet-style popup.

   Only the base map scales on zoom (strokes stay hairline); labels,
   markers and clusters live in an overlay that is re-projected each
   frame, so they keep their size exactly like a real web map. */

import { cluster, controls, attribution, pathOf, projector, road, scaleBar, shield, vehicle } from "./map-kit.js";

const MAP = { x: 124, w: 276 };
// z = 1 shows the contiguous US; Texas detail is z ≈ 3.4, a single unit z ≈ 8
const P = projector({ lon0: -125.5, lon1: -125.5 + 58.5, lat1: 58.15, latMid: 37, x: MAP.x, y: 0, w: MAP.w });

const US = [[-124.7, 48.4], [-123.0, 49.0], [-95.15, 49.0], [-95.15, 49.38], [-94.6, 48.7], [-93.0, 48.6], [-91.4, 48.05], [-89.6, 48.0],
  [-88.4, 48.3], [-84.8, 46.9], [-84.1, 46.5], [-82.4, 45.0], [-82.5, 43.0], [-83.1, 42.0], [-82.5, 41.7], [-79.0, 42.8], [-79.0, 43.3],
  [-76.3, 43.6], [-75.0, 44.8], [-71.5, 45.0], [-70.6, 45.6], [-70.0, 46.7], [-69.2, 47.45], [-67.8, 47.1], [-67.0, 45.2], [-67.0, 44.6],
  [-68.8, 44.0], [-70.2, 43.6], [-70.8, 42.9], [-70.6, 42.6], [-71.0, 42.3], [-70.0, 41.8], [-70.5, 41.5], [-71.4, 41.4], [-72.9, 41.2],
  [-73.9, 40.6], [-74.0, 40.1], [-74.6, 39.3], [-74.95, 38.9], [-75.1, 38.3], [-76.0, 37.0], [-75.9, 36.6], [-75.5, 35.5], [-76.5, 34.7],
  [-77.9, 33.9], [-79.2, 33.2], [-80.6, 32.4], [-81.3, 31.4], [-81.5, 30.4], [-80.6, 28.5], [-80.0, 26.9], [-80.1, 25.8], [-80.6, 25.2],
  [-81.2, 25.4], [-81.8, 26.4], [-82.6, 27.6], [-82.8, 28.7], [-83.6, 29.9], [-84.6, 29.9], [-85.4, 29.7], [-86.5, 30.4], [-88.0, 30.4],
  [-89.4, 30.2], [-89.6, 29.4], [-89.2, 29.1], [-90.2, 29.1], [-91.3, 29.3], [-92.6, 29.6], [-93.8, 29.72], [-94.4, 29.55], [-95.0, 29.2],
  [-96.4, 28.4], [-97.0, 28.0], [-97.3, 27.6], [-97.17, 26.0], [-97.4, 25.9], [-99.1, 26.4], [-99.5, 27.5], [-100.9, 29.3], [-101.4, 29.77],
  [-102.7, 29.75], [-103.3, 28.98], [-104.5, 29.6], [-104.9, 30.6], [-106.0, 31.4], [-106.53, 31.78], [-108.2, 31.78], [-108.2, 31.33],
  [-111.1, 31.33], [-114.8, 32.5], [-114.7, 32.7], [-117.1, 32.53], [-117.3, 33.2], [-118.5, 34.0], [-119.2, 34.15], [-120.6, 34.55],
  [-120.9, 35.4], [-121.9, 36.3], [-122.0, 36.95], [-122.5, 37.5], [-122.5, 37.8], [-123.0, 38.0], [-123.7, 38.9], [-123.8, 39.8],
  [-124.4, 40.4], [-124.1, 41.0], [-124.2, 42.0], [-124.5, 42.8], [-124.0, 43.7], [-124.1, 44.6], [-123.9, 46.2], [-124.1, 46.9]];
const CANADA = [[-140, 49], [-123.0, 49.0], [-95.15, 49.0], [-95.15, 49.38], [-94.6, 48.7], [-89.6, 48.0], [-84.8, 46.9], [-82.4, 45.0],
  [-82.5, 43.0], [-79.0, 42.8], [-76.3, 43.6], [-75.0, 44.8], [-71.5, 45.0], [-69.2, 47.45], [-67.8, 47.1], [-67.0, 45.2], [-64, 45.3],
  [-61, 45.6], [-60, 47], [-60, 70], [-140, 70]];
const MEXICO = [[-117.1, 32.53], [-114.7, 32.7], [-114.8, 32.5], [-111.1, 31.33], [-108.2, 31.33], [-108.2, 31.78], [-106.53, 31.78], [-106.0, 31.4],
  [-104.9, 30.6], [-104.5, 29.6], [-103.3, 28.98], [-102.7, 29.75], [-101.4, 29.77], [-100.9, 29.3], [-99.5, 27.5], [-99.1, 26.4], [-97.4, 25.9],
  [-97.7, 22.3], [-96.6, 20.5], [-95.9, 18.8], [-94.5, 18.3], [-92, 18.6], [-90.5, 19.8], [-90.4, 21.0], [-87.0, 21.5], [-86.8, 18.5],
  [-88, 15], [-105, 15], [-105.3, 20.4], [-105.7, 22.5], [-109.0, 25.6], [-111.0, 27.9], [-112.9, 30.8], [-114.8, 31.75]];
const BAJA = [[-117.1, 32.53], [-116.6, 31.3], [-115.6, 29.7], [-114.1, 28.0], [-112.3, 26.0], [-111.6, 24.6], [-110.3, 23.4], [-109.9, 22.9],
  [-110.3, 24.2], [-111.0, 26.0], [-112.2, 27.7], [-113.1, 29.0], [-114.1, 30.4], [-114.8, 31.75]];
const CUBA = [[-84.9, 21.9], [-82.0, 23.1], [-79.0, 22.9], [-77.0, 21.5], [-74.2, 20.2], [-75.5, 19.9], [-77.6, 19.9], [-80.0, 21.7], [-82.0, 22.1], [-84.0, 21.6]];
const LAKES_GREAT = [
  [[-92.1, 46.7], [-90.5, 46.6], [-87.6, 46.4], [-86.5, 46.5], [-84.8, 46.5], [-84.8, 47.5], [-86.5, 48.7], [-88.4, 48.8], [-89.4, 48.2], [-90.8, 47.6]],
  [[-87.8, 41.7], [-86.8, 41.8], [-86.2, 42.8], [-86.4, 43.8], [-85.6, 45.0], [-85.0, 45.8], [-85.9, 45.95], [-86.9, 45.9], [-87.7, 44.6], [-87.9, 43.3], [-87.6, 42.2]],
  [[-84.4, 45.8], [-83.5, 45.3], [-83.3, 44.4], [-83.9, 43.9], [-82.5, 43.0], [-81.7, 43.4], [-81.7, 44.6], [-80.6, 45.2], [-81.3, 45.9], [-83.5, 46.1]],
  [[-83.4, 41.7], [-82.0, 41.5], [-80.5, 42.0], [-79.0, 42.8], [-80.3, 42.6], [-81.6, 42.6], [-83.1, 42.1]],
  [[-79.8, 43.25], [-78.2, 43.4], [-76.3, 43.5], [-76.3, 44.1], [-77.6, 44.0], [-79.4, 43.7]],
];
const LAKES = [[-96.7, 33.86, 0.32, 0.07], [-93.8, 31.4, 0.07, 0.42], [-95.6, 35.28, 0.18, 0.08], [-94.2, 31.1, 0.12, 0.2], [-107.2, 33.2, 0.05, 0.25], [-112.5, 41.1, 0.35, 0.4]];
const BORDERS = [
  [[-106.6, 32.0], [-103.06, 32.0], [-103.04, 37.0]],
  [[-103.04, 36.5], [-100.0, 36.5], [-100.0, 34.56], [-99.2, 34.35], [-98.1, 34.13], [-97.2, 33.85], [-96.3, 33.75],
    [-95.2, 33.9], [-94.48, 33.64], [-94.04, 33.55], [-94.04, 31.0], [-93.6, 30.0], [-93.8, 29.72]],
  [[-94.48, 33.64], [-94.43, 35.4], [-94.62, 36.5], [-94.62, 40.6]],
  [[-109.05, 37.0], [-94.62, 37.0]], [[-109.05, 31.33], [-109.05, 41.0]],
  [[-94.04, 33.02], [-91.2, 33.0]], [[-94.62, 36.5], [-90.0, 36.5]], [[-102.05, 37.0], [-102.05, 40.0]],
];
const NATIONAL = [
  [[-117.16, 32.72], [-118.24, 34.05], [-121.49, 38.58], [-122.39, 40.59], [-123.09, 44.05], [-122.68, 45.52], [-122.33, 47.61], [-122.5, 49]],
  [[-118.24, 34.05], [-112.07, 33.45], [-110.97, 32.22], [-106.78, 32.31], [-106.49, 31.76], [-104.83, 31.04], [-102.88, 30.89], [-98.49, 29.42], [-95.37, 29.76], [-91.15, 30.45], [-90.07, 29.95], [-88.04, 30.69], [-84.28, 30.44], [-81.66, 30.33]],
  [[-117.16, 32.72], [-117.3, 34.1], [-115.14, 36.17], [-113.58, 37.1], [-111.89, 40.76], [-112.03, 43.49], [-111.3, 47.5], [-111.9, 49]],
  [[-104.2, 31.06], [-102.08, 31.99], [-99.73, 32.45], [-97.33, 32.75], [-96.8, 32.78], [-93.75, 32.52], [-90.18, 32.3], [-86.8, 33.52], [-84.39, 33.75], [-81.03, 34.0], [-79.76, 34.2]],
  [[-106.78, 32.31], [-106.65, 35.08], [-105.94, 35.69], [-104.99, 39.74], [-104.82, 41.14], [-106.7, 44.35]],
  [[-99.5, 27.5], [-98.49, 29.42], [-97.74, 30.27], [-97.15, 31.55], [-97.05, 32.8], [-97.52, 35.47], [-97.33, 37.69], [-94.58, 39.1], [-93.6, 41.59], [-93.27, 44.98], [-92.1, 46.79]],
  [[-117.02, 34.9], [-111.65, 35.2], [-106.65, 35.08], [-104.68, 34.94], [-101.83, 35.22], [-97.52, 35.47], [-94.4, 35.39], [-92.29, 34.75], [-90.05, 35.15], [-86.78, 36.16], [-83.92, 35.96], [-82.55, 35.6], [-80.24, 36.1], [-78.64, 35.78], [-77.9, 34.2]],
  [[-87.63, 41.88], [-89.65, 39.8], [-90.2, 38.63], [-90.05, 35.15], [-90.18, 32.3], [-90.07, 29.95]],
  [[-87.5, 41.6], [-86.16, 39.77], [-85.76, 38.25], [-86.78, 36.16], [-86.8, 33.52], [-86.3, 32.37], [-88.04, 30.69]],
  [[-112.6, 38.6], [-108.55, 39.06], [-104.99, 39.74], [-95.68, 39.05], [-94.58, 39.1], [-90.2, 38.63], [-86.16, 39.77], [-82.99, 39.96], [-80.25, 40.17], [-76.61, 39.29]],
  [[-83.05, 42.33], [-83.54, 41.65], [-84.19, 39.76], [-84.51, 39.1], [-84.5, 38.04], [-83.92, 35.96], [-85.31, 35.05], [-84.39, 33.75], [-83.63, 32.84], [-82.46, 27.95], [-81.79, 26.14], [-80.19, 25.76]],
  [[-122.42, 37.77], [-121.49, 38.58], [-119.81, 39.53], [-111.89, 40.76], [-104.82, 41.14], [-96.7, 40.81], [-95.94, 41.26], [-93.6, 41.59], [-87.63, 41.6], [-83.54, 41.65], [-81.69, 41.5], [-77.0, 41.1], [-74.0, 40.71]],
  [[-122.33, 47.61], [-117.43, 47.66], [-114.0, 46.87], [-108.5, 45.78], [-103.23, 44.08], [-96.73, 43.54], [-89.4, 43.07], [-87.63, 41.88], [-83.54, 41.65], [-81.69, 41.5], [-78.88, 42.89], [-73.76, 42.65], [-71.06, 42.36]],
  [[-108.5, 45.78], [-100.78, 46.81], [-96.79, 46.88], [-93.27, 44.98], [-89.4, 43.07], [-87.91, 43.04], [-87.63, 41.88], [-83.05, 42.33]],
  [[-80.19, 25.76], [-81.66, 30.33], [-81.1, 32.08], [-79.76, 34.2], [-77.44, 37.54], [-76.61, 39.29], [-75.16, 39.95], [-74.0, 40.71], [-72.93, 41.31], [-71.06, 42.36], [-70.26, 43.66], [-68.77, 44.8], [-67.84, 46.13]],
  [[-96.8, 32.78], [-96.0, 31.3], [-95.37, 29.76]],
  [[-98.49, 33.91], [-97.52, 35.47], [-95.99, 36.15], [-93.29, 37.21], [-90.2, 38.63]],
  [[-96.8, 32.78], [-95.6, 33.15], [-94.05, 33.43], [-92.29, 34.75]],
  [[-101.85, 33.58], [-101.71, 34.18], [-101.83, 35.22]],
  [[-98.49, 29.42], [-97.9, 28.4], [-97.4, 27.8]],
];
// Geometry the Texas trucks move along (the same roads as drawn above)
const MOVE = {
  "40": [[-106.65, 35.08], [-104.68, 34.94], [-101.83, 35.22], [-97.52, 35.47], [-94.4, 35.39], [-92.29, 34.75]],
  "35": [[-98.49, 29.42], [-97.74, 30.27], [-97.15, 31.55], [-97.05, 32.8], [-97.52, 35.47], [-97.33, 37.69]],
  "20": [[-104.2, 31.06], [-102.08, 31.99], [-99.73, 32.45], [-97.33, 32.75], [-96.8, 32.78], [-93.75, 32.52]],
  "10": [[-106.49, 31.76], [-104.83, 31.04], [-102.88, 30.89], [-98.49, 29.42], [-95.37, 29.76], [-91.15, 30.45]],
  "45": [[-96.8, 32.78], [-96.0, 31.3], [-95.37, 29.76]],
  "44": [[-98.49, 33.91], [-97.52, 35.47], [-95.99, 36.15], [-93.29, 37.21]],
  "27": [[-101.85, 33.58], [-101.71, 34.18], [-101.83, 35.22]],
  "25": [[-106.78, 32.31], [-106.65, 35.08], [-105.94, 35.69], [-104.99, 39.74]],
  "30": [[-96.8, 32.78], [-95.6, 33.15], [-94.05, 33.43], [-92.29, 34.75]],
};
const BIG = [["Seattle", -122.33, 47.61], ["San Francisco", -122.42, 37.77], ["Los Angeles", -118.24, 34.05], ["Phoenix", -112.07, 33.45],
  ["Denver", -104.99, 39.74], ["Dallas", -96.8, 32.78], ["Houston", -95.37, 29.76], ["Chicago", -87.63, 41.88], ["Atlanta", -84.39, 33.75],
  ["Miami", -80.19, 25.76], ["New York", -74.0, 40.71], ["Minneapolis", -93.27, 44.98], ["Salt Lake City", -111.89, 40.76], ["Nashville", -86.78, 36.16]];
const LOCAL = [["Albuquerque", -106.65, 35.08], ["El Paso", -106.49, 31.76], ["Amarillo", -101.83, 35.22], ["Lubbock", -101.85, 33.58],
  ["Midland", -102.08, 31.99], ["Oklahoma City", -97.52, 35.47], ["Tulsa", -95.99, 36.15], ["Wichita", -97.33, 37.69],
  ["Austin", -97.74, 30.27], ["San Antonio", -98.49, 29.42], ["Little Rock", -92.29, 34.75], ["Corpus Christi", -97.4, 27.8]];
const LEFT = new Set(["Dallas", "Oklahoma City", "San Antonio", "Little Rock", "New York", "Miami", "Atlanta", "Nashville"]);
const STATES = [["TEXAS", -99.6, 31.2], ["OKLAHOMA", -98.2, 36.15], ["NEW MEXICO", -106.0, 34.0], ["KANSAS", -98.6, 38.6], ["ARKANSAS", -92.9, 35.95], ["LOUISIANA", -92.5, 31.4]];
const CLUSTERS = [[64, -87.63, 41.88], [51, -84.39, 33.75], [48, -96.8, 32.78], [42, -118.24, 34.05], [37, -74.0, 40.71], [36, -95.37, 29.76],
  [29, -90.05, 35.15], [23, -112.07, 33.45], [21, -97.52, 35.47], [19, -94.58, 39.1], [18, -104.99, 39.74], [14, -80.19, 25.76], [12, -122.33, 47.61], [9, -111.89, 40.76]];
// Cities that hold a cluster: the bubble stands in for the label until the map zooms in
const CLUSTERED = new Set(["Seattle", "Los Angeles", "Phoenix", "Denver", "Dallas", "Houston", "Chicago", "Atlanta", "Miami", "New York", "Salt Lake City"]);

const STATUS = { move: "#34a853", idle: "#8a94a6", fuel: "#f29900", fault: "#d93025" };
const clamp01 = (v) => Math.max(0, Math.min(1, v));

export default {
  duration: 12600,
  rest: 1400,
  i18n: {
    en: {
      steps: [
        "575 trucks across the US, positions from the Motive API",
        "The map refreshes every ~10 seconds",
        "Zoom in: clusters break into single trucks, faults stand out",
        "Pick a unit: speed, road and fuel at a glance",
      ],
      fleet: "Fleet", live: "Live", ago: "s ago", search: "Search unit", fuel: "Fuel", low: "Low fuel", idle: "Idle", fault: "Fault",
      heading: "heading W", near: "near",
    },
    uz: {
      steps: [
        "AQSH bo'ylab 575 ta mashina, joylashuvi Motive API'dan",
        "Xarita har ~10 soniyada yangilanadi",
        "Yaqinlashganda klasterlar alohida mashinalarga ajraladi, nosozliklar ko'zga tashlanadi",
        "Mashinani tanlang: tezlik, yo'l va yoqilg'i bir qarashda",
      ],
      fleet: "Park", live: "Jonli", ago: "s oldin", search: "Mashina raqami", fuel: "Yoqilg'i", low: "Yoqilg'i kam", idle: "Turibdi", fault: "Nosozlik",
      heading: "g'arbga", near: "yaqinida",
    },
    ru: {
      steps: [
        "575 тягачей по всей стране, координаты из Motive API",
        "Карта обновляется каждые ~10 секунд",
        "При приближении кластеры распадаются на машины, неисправности видны сразу",
        "Выберите юнит: скорость, трасса и топливо сразу",
      ],
      fleet: "Парк", live: "Онлайн", ago: "с назад", search: "Найти юнит", fuel: "Топливо", low: "Мало топлива", idle: "Стоит", fault: "Неисправность",
      heading: "на запад", near: "около",
    },
  },

  build(svg, { h, rng }, t) {
    const R = rng(9);
    const uid = "tm" + Math.random().toString(36).slice(2, 8);
    const clip = h("clipPath", { id: `${uid}c` }, h("defs", {}, svg));
    h("rect", { x: MAP.x, y: 0, width: MAP.w, height: 250 }, clip);

    // ── Base map (this group zooms) ──
    const frame = h("g", { "clip-path": `url(#${uid}c)` }, svg);
    const base = h("g", { class: "vb" }, frame);
    h("rect", { x: -2000, y: -2000, width: 5000, height: 5000, class: "m-water" }, base);
    [CANADA, MEXICO, BAJA, CUBA].forEach((poly) => h("path", { d: pathOf(poly, P, true), class: "m-land2" }, base));
    h("path", { d: pathOf(US, P, true), class: "m-land" }, base);
    LAKES_GREAT.forEach((poly) => h("path", { d: pathOf(poly, P, true), class: "m-water" }, base));
    LAKES.forEach(([lon, lat, rx, ry]) => { const [x, y] = P([lon, lat]); h("ellipse", { cx: x, cy: y, rx: rx * P.kx, ry: ry * P.ky, class: "m-water" }, base); });
    h("path", { d: pathOf(US, P, true), fill: "none", style: "stroke: var(--map-hwy-case)", "stroke-width": 0.5, opacity: 0.5 }, base);
    const borders = h("g", { opacity: 0 }, base);
    BORDERS.forEach((b) => h("path", { d: pathOf(b, P), class: "m-border", "stroke-width": 0.8 }, borders));
    NATIONAL.forEach((pts) => road(h, base, pathOf(pts, P), "hwy"));
    base.querySelectorAll("path").forEach((el) => el.setAttribute("vector-effect", "non-scaling-stroke"));
    const roads = {};
    for (const [num, pts] of Object.entries(MOVE)) roads[num] = h("path", { d: pathOf(pts, P), fill: "none", stroke: "none" }, base);

    // ── Overlay (re-projected, never scaled) ──
    const over = h("g", { "clip-path": `url(#${uid}c)` }, svg);
    const labels = [];
    STATES.forEach(([name, lon, lat]) => {
      const [x, y] = P([lon, lat]);
      labels.push({ x, y, minZ: 2.4, el: h("text", { "font-size": 7, class: "m-label", "text-anchor": "middle", "letter-spacing": 2.2, "font-weight": 600, opacity: 0.55, text: name }, over) });
    });
    const addCity = (name, lon, lat, minZ, maxZ, big) => {
      const [x, y] = P([lon, lat]);
      const left = LEFT.has(name);
      const dot = h("circle", { r: big ? 2.2 : 1.7, style: "fill: var(--map-label); stroke: var(--map-halo)", "stroke-width": 0.9 }, over);
      const el = h("text", { "font-size": big ? 8 : 7.5, class: "m-label", "font-weight": big ? 600 : 500, "text-anchor": left ? "end" : "start", text: name }, over);
      labels.push({ x, y, el, dot, minZ, maxZ, dx: left ? -4 : 4, dy: left ? -3 : 3 });
    };
    BIG.forEach(([n, lon, lat]) => addCity(n, lon, lat, CLUSTERED.has(n) ? 2.2 : 0, 99, true));
    LOCAL.forEach(([n, lon, lat]) => addCity(n, lon, lat, 2.4, 99, false));
    const shields = [["40", -99.3, 35.3], ["35", -97.1, 31.95], ["20", -100.9, 32.25], ["10", -103.9, 30.95], ["44", -96.8, 35.82], ["45", -96.0, 31.25], ["25", -106.3, 33.6]]
      .map(([n, lon, lat]) => { const [x, y] = P([lon, lat]); return { x, y, minZ: 2.4, el: shield(h, over, 0, 0, n, 1) }; });

    const clusters = CLUSTERS.map(([n, lon, lat]) => { const [x, y] = P([lon, lat]); return { x, y, n, c: cluster(h, over, 0, 0, n) }; });

    // Trucks on the Texas–Oklahoma roads (they appear once clusters break up)
    const pick = ["40", "40", "35", "35", "20", "20", "10", "10", "44", "45", "27", "25", "30", "40", "35", "20", "10", "25", "30", "40", "35", "10"];
    const trucks = pick.map((num, i) => {
      const status = i === 9 ? "fuel" : i % 6 === 3 ? "idle" : "move";
      const v = vehicle(h, over, STATUS[status]);
      return { road: roads[num], len: roads[num].getTotalLength(), pos: 0.06 + R() * 0.88, dir: R() > 0.5 ? 1 : -1, status, v, step: status === "idle" ? 0 : 0.01 + R() * 0.01 };
    });
    const fault = { road: roads["44"], len: roads["44"].getTotalLength(), pos: 0.48, dir: 1, status: "fault", step: 0, alert: true, v: vehicle(h, over, STATUS.fault) };
    const target = { road: roads["40"], len: roads["40"].getTotalLength(), pos: 0.33, dir: -1, status: "fuel", step: 0.005, alert: true, v: vehicle(h, over, STATUS.fuel) };
    trucks.push(fault, target);
    const faultRing = h("circle", { r: 6, fill: "none", stroke: STATUS.fault, "stroke-width": 1.4 }, over);

    controls(h, svg, 376, 8);
    attribution(h, svg, 400, 250);
    const scale = scaleBar(h, svg, 132, 240, 40, "500 mi");

    // Popup (screen coordinates; the picked truck is flown to 262,152)
    const popup = h("g", { opacity: 0 }, svg);
    h("path", { d: "M200 54h124a6 6 0 0 1 6 6v68a6 6 0 0 1-6 6h-56l-6 7-6-7h-56a6 6 0 0 1-6-6V60a6 6 0 0 1 6-6Z", class: "d-card", style: "filter: drop-shadow(0 4px 10px rgba(0,0,0,0.18))" }, popup);
    h("text", { x: 208, y: 71, "font-size": 10.5, class: "d-tx dd", text: "#1112" }, popup);
    h("rect", { x: 268, y: 61, width: 56, height: 14, rx: 7, fill: STATUS.fuel, opacity: 0.16 }, popup);
    h("text", { x: 296, y: 71, "font-size": 7.5, fill: STATUS.fuel, "text-anchor": "middle", class: "db", text: t.low }, popup);
    h("text", { x: 208, y: 87, "font-size": 8.5, class: "d-tx2", text: `63 mph · ${t.heading}` }, popup);
    h("text", { x: 208, y: 99, "font-size": 8, class: "d-tx3", text: `I-40 ${t.near} Amarillo, TX` }, popup);
    h("text", { x: 208, y: 115, "font-size": 7.5, class: "d-tx3", text: t.fuel }, popup);
    h("text", { x: 322, y: 115, "font-size": 7.5, fill: STATUS.fuel, "text-anchor": "end", class: "dm db", text: "12%" }, popup);
    h("rect", { x: 208, y: 119, width: 114, height: 4, rx: 2, class: "d-card2" }, popup);
    const fuelBar = h("rect", { x: 208, y: 119, width: 114 * 0.12, height: 4, rx: 2, fill: STATUS.fuel, class: "o-l" }, popup);

    // ── Fleet list ──
    h("rect", { x: 0, y: 0, width: MAP.x, height: 250, class: "d-card" }, svg);
    h("text", { x: 10, y: 20, "font-size": 11, class: "d-tx db", text: t.fleet }, svg);
    h("text", { x: 114, y: 20, "font-size": 9.5, class: "d-tx2 dm", "text-anchor": "end", text: "575" }, svg);
    const liveDot = h("circle", { cx: 13, cy: 31, r: 2.6, fill: STATUS.move }, svg);
    const updated = h("text", { x: 19, y: 34, "font-size": 7.5, class: "d-tx3", text: `${t.live} · 2 ${t.ago}` }, svg);
    h("rect", { x: 8, y: 41, width: 108, height: 18, rx: 5, class: "d-card2" }, svg);
    h("circle", { cx: 18, cy: 49.5, r: 3, fill: "none", class: "s-tx3", "stroke-width": 1.1 }, svg);
    h("path", { d: "M20.2 51.8l2.2 2.2", class: "s-tx3", "stroke-width": 1.1, "stroke-linecap": "round" }, svg);
    const query = h("text", { x: 27, y: 53, "font-size": 8, class: "d-tx3", text: t.search }, svg);
    [["move", "412"], ["idle", "131"], ["fault", "32"]].forEach(([k, n], i) => {
      h("circle", { cx: 13 + i * 36, cy: 70, r: 2.6, fill: STATUS[k] }, svg);
      h("text", { x: 19 + i * 36, y: 73, "font-size": 8, class: "d-tx2 dm", text: n }, svg);
    });
    const rows = [
      ["#1112", "63 mph", "I-40 · Amarillo, TX", "fuel"],
      ["#1203", "58 mph", "I-35 · Waco, TX", "move"],
      ["#1150", "—", `${t.fault} · Tulsa, OK`, "fault"],
      ["#0967", "61 mph", "I-80 · Omaha, NE", "move"],
      ["#1088", "0 mph", `${t.idle} · Atlanta, GA`, "idle"],
    ].map(([unit, spd, where, st], i) => {
      const y = 82 + i * 32;
      const g = h("g", {}, svg);
      const bg = h("rect", { x: 4, y, width: 116, height: 29, rx: 5, fill: "transparent" }, g);
      h("circle", { cx: 12, cy: y + 10, r: 2.8, fill: STATUS[st] }, g);
      h("text", { x: 19, y: y + 13, "font-size": 9, class: "d-tx db dm", text: unit }, g);
      h("text", { x: 114, y: y + 13, "font-size": 8, class: "d-tx2 dm", "text-anchor": "end", text: spd }, g);
      h("text", { x: 19, y: y + 24, "font-size": 7.5, class: "d-tx3", text: where }, g);
      return { g, bg };
    });

    return { base, borders, labels, shields, clusters, trucks, target, fault, faultRing, popup, fuelBar, updated, liveDot, rows, query, scale };
  },

  async play(api, s, t) {
    const view = { z: 1, tx: 0, ty: 0 };
    const at = (x, y) => [view.tx + x * view.z, view.ty + y * view.z];
    const pointOf = (tr, pos) => {
      const a = tr.road.getPointAtLength(clamp01(pos) * tr.len);
      const b = tr.road.getPointAtLength(clamp01(pos + 0.004 * tr.dir) * tr.len);
      return { x: a.x, y: a.y, deg: (Math.atan2(b.y - a.y, b.x - a.x) * 180) / Math.PI + 90 };
    };
    s.trucks.forEach((tr) => { tr.from = tr.pos; tr.to = tr.pos; });
    let blend = 1;

    const render = () => {
      const z = view.z;
      s.base.style.transform = `translate(${view.tx.toFixed(2)}px, ${view.ty.toFixed(2)}px) scale(${z.toFixed(4)})`;
      s.borders.style.opacity = String(clamp01((z - 2) / 0.6));
      for (const l of s.labels) {
        const show = z >= (l.minZ || 0) && z < (l.maxZ || 99);
        l.el.style.display = show ? "" : "none";
        if (l.dot) l.dot.style.display = show ? "" : "none";
        if (!show) continue;
        const [x, y] = at(l.x, l.y);
        if (l.dot) { l.dot.setAttribute("cx", x.toFixed(1)); l.dot.setAttribute("cy", y.toFixed(1)); }
        l.el.setAttribute("x", (x + (l.dx || 0)).toFixed(1));
        l.el.setAttribute("y", (y + (l.dy || 0)).toFixed(1));
      }
      for (const sh of s.shields) {
        sh.el.style.display = z >= sh.minZ ? "" : "none";
        const [x, y] = at(sh.x, sh.y);
        sh.el.setAttribute("transform", `translate(${x.toFixed(1)} ${y.toFixed(1)})`);
      }
      // Clusters give way to single trucks as the map zooms in
      const cl = clamp01((2.6 - z) / 0.6), tk = clamp01((z - 2.0) / 0.6);
      for (const c of s.clusters) {
        const [x, y] = at(c.x, c.y);
        c.c.g.setAttribute("transform", `translate(${x.toFixed(1)} ${y.toFixed(1)})`);
        c.c.g.style.opacity = String(cl);
      }
      for (const tr of s.trucks) {
        const p = pointOf(tr, tr.from + (tr.to - tr.from) * blend);
        const [x, y] = at(p.x, p.y);
        tr.screen = [x, y];
        tr.v.g.setAttribute("transform", `translate(${x.toFixed(1)} ${y.toFixed(1)}) rotate(${p.deg.toFixed(0)})`);
        tr.v.g.style.opacity = String(tr.alert ? 1 : tk);
      }
      const [fx, fy] = s.fault.screen;
      s.faultRing.setAttribute("cx", fx.toFixed(1));
      s.faultRing.setAttribute("cy", fy.toFixed(1));
      // Scale bar for the current zoom (1° of longitude ≈ 54.5 mi at 38°N)
      const pxPerMile = (P.kx * z) / 54.5;
      const nice = [10, 20, 25, 50, 100, 200, 250, 500].find((m) => m * pxPerMile >= 28) || 500;
      s.scale.querySelector("path").setAttribute("d", `M132 236V240H${(132 + nice * pxPerMile).toFixed(1)}V236`);
      s.scale.querySelector("text").textContent = `${nice} mi`;
    };

    // One poll of the feed: trucks ease to their next reported positions, cluster counts move a little
    const poll = async () => {
      s.trucks.forEach((tr) => {
        tr.from = tr.from + (tr.to - tr.from) * blend;
        tr.to = Math.max(0.02, Math.min(0.98, tr.from + tr.step * tr.dir));
      });
      s.clusters.forEach((c, i) => { if (i % 3 === 0) c.c.t.textContent = String(c.n + (Math.random() > 0.5 ? 1 : -1)); });
      blend = 0;
      await api.tick(900, (p) => { blend = p; render(); }, "inOut");
    };
    const viewOn = (x, y, z, cx = 262, cy = 152) => ({ z, tx: cx - x * z, ty: cy - y * z });
    const flyTo = (to, dur) => {
      const from = { ...view };
      return api.tick(dur, (p) => {
        // zoom on a log scale so the move feels even, like Leaflet's flyTo
        const z = Math.exp(Math.log(from.z) + (Math.log(to.z) - Math.log(from.z)) * p);
        const fx = (262 - from.tx) / from.z, fy = (152 - from.ty) / from.z;
        const gx = (262 - to.tx) / to.z, gy = (152 - to.ty) / to.z;
        view.z = z;
        view.tx = 262 - (fx + (gx - fx) * p) * z;
        view.ty = 152 - (fy + (gy - fy) * p) * z;
        render();
      }, "inOut");
    };

    Object.assign(view, viewOn(P([-96, 38.5])[0], P([-96, 38.5])[1], 1, 262, 125));
    render();

    if (api.instant) {
      const p = pointOf(s.target, s.target.to);
      Object.assign(view, viewOn(p.x, p.y, 8.2));
      render();
      s.rows[0].bg.setAttribute("class", "d-card2");
      s.popup.style.opacity = "1";
      api.step(3);
      api.poster();
    }

    let since = 2;
    api.spawn(async () => {
      for (;;) { await api.wait(1000); since += 1; s.updated.textContent = `${t.live} · ${since} ${t.ago}`; }
    });
    api.loop(s.faultRing, [{ transform: "scale(0.8)", opacity: 0.9 }, { transform: "scale(2.6)", opacity: 0 }], { duration: 1500, easing: "ease-out" });
    api.loop(s.liveDot, [{ opacity: 1 }, { opacity: 0.35 }], { duration: 1000, direction: "alternate" });

    api.step(0);
    await api.wait(1400);

    api.step(1);
    for (let i = 0; i < 2; i++) {
      since = 0;
      s.updated.textContent = `${t.live} · 0 ${t.ago}`;
      await poll();
      await api.wait(900);
    }

    api.step(2);
    s.rows[2].bg.setAttribute("class", "d-card2");
    const tx = P([-98.2, 33.6]);
    await flyTo(viewOn(tx[0], tx[1], 3.3, 262, 140), 1600);
    since = 0;
    await poll();
    await api.wait(700);
    s.rows[2].bg.setAttribute("class", "");

    api.step(3);
    s.query.setAttribute("class", "d-tx dm");
    await api.type(s.query, "1112", 10);
    s.rows[0].bg.setAttribute("class", "d-card2");
    await api.wait(250);
    const p = pointOf(s.target, s.target.to);
    await flyTo(viewOn(p.x, p.y, 8.2), 1300);
    await api.show(s.popup, 320, "translateY(4px)");
    await api.tween(s.fuelBar, [{ transform: "scaleX(0)" }, { transform: "scaleX(1)" }], { dur: 500 });
    await api.wait(2000);
  },
};
