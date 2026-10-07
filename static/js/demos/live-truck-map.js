/* Live Truck Map, drawn like the dispatch screen it is: a fleet list on the
   left, a real map of the Texas–Oklahoma corridor on the right. Positions
   arrive in steps (the feed is polled, not streamed), alerts stand out,
   and picking a unit flies the map to it with a Leaflet-style popup.

   Only the base map scales on zoom (strokes stay hairline); labels,
   markers and clusters live in an overlay that is re-projected each
   frame, so they keep their size exactly like a real web map. */

import { cluster, controls, attribution, pathOf, projector, road, scaleBar, shield, vehicle } from "./map-kit.js";

const MAP = { x: 124, w: 276 };
const P = projector({ lon0: -108.6, lon1: -91.4, lat1: 39.6, latMid: 33, x: MAP.x, y: 0, w: MAP.w });

const GULF = [[-97.17, 26.4], [-97.3, 27.6], [-97.0, 28.0], [-96.4, 28.4], [-95.0, 29.2], [-94.4, 29.55], [-93.8, 29.72],
  [-92.6, 29.6], [-91.3, 29.4], [-91.3, 26.4]];
const MEXICO = [[-108.7, 31.33], [-106.53, 31.78], [-106.0, 31.4], [-104.9, 30.6], [-104.5, 29.6], [-103.3, 28.98],
  [-102.7, 29.75], [-101.4, 29.77], [-100.9, 29.3], [-99.5, 27.5], [-99.1, 26.4], [-97.2, 26.0], [-108.7, 26.0]];
const BORDERS = [
  [[-106.6, 32.0], [-103.06, 32.0], [-103.04, 37.0]],
  [[-103.04, 36.5], [-100.0, 36.5], [-100.0, 34.56], [-99.2, 34.35], [-98.1, 34.13], [-97.2, 33.85], [-96.3, 33.75],
    [-95.2, 33.9], [-94.48, 33.64], [-94.04, 33.55], [-94.04, 31.0], [-93.6, 30.0], [-93.8, 29.72]],
  [[-94.48, 33.64], [-94.43, 35.4], [-94.62, 36.5], [-94.62, 39.7]],
  [[-108.7, 37.0], [-94.62, 37.0]],
  [[-94.04, 33.02], [-91.3, 33.0]],
  [[-94.62, 36.5], [-91.3, 36.5]],
];
const LAKES = [[-96.7, 33.86, 0.32, 0.07], [-93.8, 31.4, 0.07, 0.42], [-95.6, 35.28, 0.18, 0.08], [-94.2, 31.1, 0.12, 0.2], [-107.2, 33.2, 0.05, 0.25]];
const HWY = {
  "40": [[-108.7, 35.08], [-106.65, 35.08], [-104.68, 34.94], [-103.72, 35.17], [-101.83, 35.22], [-100.2, 35.22], [-97.52, 35.47], [-95.6, 35.45], [-94.4, 35.39], [-92.29, 34.75], [-91.3, 34.85]],
  "35": [[-98.49, 29.42], [-97.74, 30.27], [-97.15, 31.55], [-97.05, 32.8], [-97.2, 33.9], [-97.52, 35.47], [-97.4, 36.5], [-97.33, 37.69], [-96.6, 38.5], [-95.7, 39.6]],
  "20": [[-106.49, 31.76], [-103.49, 31.42], [-102.08, 31.99], [-99.73, 32.45], [-97.33, 32.75], [-96.8, 32.78], [-95.3, 32.35], [-93.75, 32.52], [-91.3, 32.4]],
  "10": [[-108.7, 32.3], [-106.49, 31.76], [-104.83, 31.04], [-102.88, 30.89], [-100.0, 30.4], [-98.49, 29.42], [-95.37, 29.76], [-94.1, 30.08], [-91.3, 30.4]],
  "45": [[-96.8, 32.78], [-96.0, 31.3], [-95.37, 29.76], [-94.9, 29.3]],
  "44": [[-98.49, 33.91], [-97.52, 35.47], [-95.99, 36.15], [-94.6, 37.1], [-93.3, 37.2]],
  "27": [[-101.85, 33.58], [-101.71, 34.18], [-101.83, 35.22]],
  "25": [[-106.78, 32.31], [-106.65, 35.08], [-105.94, 35.69], [-104.44, 36.9], [-104.6, 38.3], [-104.8, 39.6]],
  "30": [[-96.8, 32.78], [-95.6, 33.15], [-94.05, 33.43], [-92.29, 34.75]],
  "37": [[-98.49, 29.42], [-97.9, 28.4], [-97.4, 27.8]],
};
const CITIES = [
  ["Albuquerque", -106.65, 35.08, 1], ["El Paso", -106.49, 31.76, 1], ["Amarillo", -101.83, 35.22, 0], ["Lubbock", -101.85, 33.58, 0],
  ["Midland", -102.08, 31.99, 0], ["Oklahoma City", -97.52, 35.47, 1], ["Tulsa", -95.99, 36.15, 0], ["Wichita", -97.33, 37.69, 0],
  ["Dallas", -96.8, 32.78, 1], ["Austin", -97.74, 30.27, 0], ["San Antonio", -98.49, 29.42, 1], ["Houston", -95.37, 29.76, 1],
["Little Rock", -92.29, 34.75, 0], ["Corpus Christi", -97.4, 27.8, 0],
];
const STATES = [["TEXAS", -99.6, 31.2], ["OKLAHOMA", -98.2, 36.15], ["NEW MEXICO", -106.0, 34.0], ["KANSAS", -98.6, 38.6], ["ARKANSAS", -92.9, 35.95], ["LOUISIANA", -92.5, 31.4]];

const STATUS = { move: "#34a853", idle: "#8a94a6", fuel: "#f29900", fault: "#d93025" };

export default {
  duration: 11100,
  rest: 1400,
  i18n: {
    en: {
      steps: [
        "575 trucks, positions from the Motive API",
        "The map refreshes every ~10 seconds",
        "Faults and low fuel stand out",
        "Pick a unit: speed, road and fuel at a glance",
      ],
      fleet: "Fleet", live: "Live", ago: "s ago", search: "Search unit", fuel: "Fuel", low: "Low fuel", idle: "Idle", fault: "Fault",
      heading: "heading W", near: "near",
    },
    uz: {
      steps: [
        "575 ta mashina, joylashuvi Motive API'dan",
        "Xarita har ~10 soniyada yangilanadi",
        "Nosozlik va kam yoqilg'i darrov ko'zga tashlanadi",
        "Mashinani tanlang: tezlik, yo'l va yoqilg'i bir qarashda",
      ],
      fleet: "Park", live: "Jonli", ago: "s oldin", search: "Mashina raqami", fuel: "Yoqilg'i", low: "Yoqilg'i kam", idle: "Turibdi", fault: "Nosozlik",
      heading: "g'arbga", near: "yaqinida",
    },
    ru: {
      steps: [
        "575 тягачей, координаты из Motive API",
        "Карта обновляется каждые ~10 секунд",
        "Неисправности и низкое топливо видны сразу",
        "Выберите юнит: скорость, трасса и топливо сразу",
      ],
      fleet: "Парк", live: "Онлайн", ago: "с назад", search: "Найти юнит", fuel: "Топливо", low: "Мало топлива", idle: "Стоит", fault: "Неисправность",
      heading: "на запад", near: "около",
    },
  },

  build(svg, { h, rng }, t) {
    const R = rng(9);
    const uid = "tm" + Math.random().toString(36).slice(2, 8);
    const defs = h("defs", {}, svg);
    const clip = h("clipPath", { id: `${uid}c` }, defs);
    h("rect", { x: MAP.x, y: 0, width: MAP.w, height: 250 }, clip);

    // ── Base map (this group zooms) ──
    const frame = h("g", { "clip-path": `url(#${uid}c)` }, svg);
    const base = h("g", { class: "vb" }, frame);
    h("rect", { x: MAP.x - 400, y: -400, width: 1200, height: 1200, class: "m-land" }, base);
    h("path", { d: pathOf(MEXICO, P, true), class: "m-land2" }, base);
    h("path", { d: pathOf(GULF, P, true), class: "m-water" }, base);
    LAKES.forEach(([lon, lat, rx, ry]) => {
      const [x, y] = P([lon, lat]);
      h("ellipse", { cx: x, cy: y, rx: rx * P.kx, ry: ry * P.ky, class: "m-water" }, base);
    });
    BORDERS.forEach((b) => h("path", { d: pathOf(b, P), class: "m-border", "stroke-width": 0.8, "vector-effect": "non-scaling-stroke" }, base));
    const roads = {};
    for (const [num, pts] of Object.entries(HWY)) {
      const d = pathOf(pts, P);
      road(h, base, d, "hwy");
      roads[num] = h("path", { d, fill: "none", stroke: "none" }, base);   // geometry for movement
    }
    base.querySelectorAll(".m-hwy, .m-hwyc").forEach((el) => el.setAttribute("vector-effect", "non-scaling-stroke"));

    // ── Overlay (re-projected, never scaled) ──
    const over = h("g", { "clip-path": `url(#${uid}c)` }, svg);
    const labels = [];
    STATES.forEach(([name, lon, lat]) => {
      const [x, y] = P([lon, lat]);
      labels.push({ x, y, el: h("text", { "font-size": 7, class: "m-label", "text-anchor": "middle", "letter-spacing": 2.2, "font-weight": 600, opacity: 0.55, text: name }, over) });
    });
    const LEFT = new Set(["Dallas", "Houston", "Oklahoma City", "San Antonio", "Little Rock"]);
    CITIES.forEach(([name, lon, lat, big]) => {
      const [x, y] = P([lon, lat]);
      const left = LEFT.has(name);
      const dot = h("circle", { r: big ? 2.3 : 1.7, style: "fill: var(--map-label); stroke: var(--map-halo)", "stroke-width": 0.9 }, over);
      const el = h("text", { "font-size": big ? 8.5 : 7.5, class: "m-label", "font-weight": big ? 600 : 500, "text-anchor": left ? "end" : "start", text: name }, over);
      labels.push({ x, y, el, dot, dx: left ? -4 : 4, dy: left ? -3 : 3 });
    });
    const shields = [["40", -94.9, 35.41], ["35", -97.1, 31.95], ["20", -100.9, 32.25], ["10", -103.9, 30.95], ["44", -96.8, 35.82], ["45", -96.0, 31.25], ["25", -106.3, 33.6]]
      .map(([n, lon, lat]) => { const [x, y] = P([lon, lat]); return { x, y, el: shield(h, over, 0, 0, n, 1) }; });

    // Clusters where the fleet is dense
    const clusters = [["48", -96.15, 32.95], ["36", -94.75, 29.95], ["21", -96.85, 35.2], ["17", -98.05, 29.05]]
      .map(([n, lon, lat]) => { const [x, y] = P([lon, lat]); return { x, y, c: cluster(h, over, 0, 0, Number(n)) }; });

    // Trucks on the roads
    const pick = ["40", "40", "35", "35", "20", "20", "10", "10", "44", "45", "27", "25", "30", "37", "40", "35", "20", "10", "25", "30", "40"];
    const trucks = pick.map((num, i) => {
      const status = i === 9 ? "fuel" : i % 6 === 3 ? "idle" : "move";
      const v = vehicle(h, over, STATUS[status]);
      return { road: roads[num], len: roads[num].getTotalLength(), pos: 0.06 + R() * 0.88, dir: R() > 0.5 ? 1 : -1, status, v, step: status === "idle" || status === "fault" ? 0 : 0.012 + R() * 0.01 };
    });
    const target = { road: roads["40"], len: roads["40"].getTotalLength(), pos: 0.37, dir: -1, status: "fuel", step: 0.006, v: vehicle(h, over, STATUS.fuel) };
    trucks.push(target);
    // #1150: stopped with a fault on I-44 near Tulsa
    const fault = { road: roads["44"], len: roads["44"].getTotalLength(), pos: 0.6, dir: 1, status: "fault", step: 0, v: vehicle(h, over, STATUS.fault) };
    trucks.push(fault);
    const faultRing = h("circle", { r: 6, fill: "none", stroke: STATUS.fault, "stroke-width": 1.4 }, over);

    // Map chrome
    controls(h, svg, 376, 8);
    attribution(h, svg, 400, 250);
    scaleBar(h, svg, 132, 240, 40, "100 mi");

    // Popup for the picked truck (screen coordinates; the truck is flown to 262,152)
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
      ["#0967", "61 mph", "I-20 · Abilene, TX", "move"],
      ["#1088", "0 mph", `${t.idle} · Dallas, TX`, "idle"],
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

    return { base, labels, shields, clusters, trucks, target, fault, faultRing, popup, fuelBar, updated, liveDot, rows, query };
  },

  async play(api, s, t) {
    const view = { z: 1, tx: 0, ty: 0 };
    const at = (x, y) => [view.tx + x * view.z, view.ty + y * view.z];
    const pointOf = (tr, pos) => {
      const len = tr.len;
      const a = tr.road.getPointAtLength(Math.max(0, Math.min(1, pos)) * len);
      const b = tr.road.getPointAtLength(Math.max(0, Math.min(1, pos + 0.004 * tr.dir)) * len);
      return { x: a.x, y: a.y, deg: (Math.atan2(b.y - a.y, b.x - a.x) * 180) / Math.PI + 90 };
    };
    s.trucks.forEach((tr) => { tr.from = tr.pos; tr.to = tr.pos; });
    let blend = 1;

    const render = () => {
      s.base.style.transform = `translate(${view.tx.toFixed(2)}px, ${view.ty.toFixed(2)}px) scale(${view.z.toFixed(4)})`;
      for (const l of s.labels) {
        const [x, y] = at(l.x, l.y);
        if (l.dot) { l.dot.setAttribute("cx", x.toFixed(1)); l.dot.setAttribute("cy", y.toFixed(1)); }
        l.el.setAttribute("x", (x + (l.dx || 0)).toFixed(1));
        l.el.setAttribute("y", (y + (l.dy || 0)).toFixed(1));
      }
      for (const sh of s.shields) { const [x, y] = at(sh.x, sh.y); sh.el.setAttribute("transform", `translate(${x.toFixed(1)} ${y.toFixed(1)})`); }
      for (const c of s.clusters) { const [x, y] = at(c.x, c.y); c.c.g.setAttribute("transform", `translate(${x.toFixed(1)} ${y.toFixed(1)})`); }
      for (const tr of s.trucks) {
        const p = pointOf(tr, tr.from + (tr.to - tr.from) * blend);
        const [x, y] = at(p.x, p.y);
        tr.screen = [x, y];
        tr.v.g.setAttribute("transform", `translate(${x.toFixed(1)} ${y.toFixed(1)}) rotate(${p.deg.toFixed(0)})`);
      }
      const [fx, fy] = s.fault.screen;
      s.faultRing.setAttribute("cx", fx.toFixed(1));
      s.faultRing.setAttribute("cy", fy.toFixed(1));
    };

    // One poll of the feed: every truck eases to its next reported position
    const poll = async () => {
      s.trucks.forEach((tr) => {
        tr.from = tr.from + (tr.to - tr.from) * blend;
        tr.to = Math.max(0.02, Math.min(0.98, tr.from + tr.step * tr.dir));
      });
      blend = 0;
      await api.tick(900, (p) => { blend = p; render(); }, "inOut");
    };

    const flyTo = (tr, z) => {
      const p = pointOf(tr, tr.to);
      return { z, tx: 262 - p.x * z, ty: 152 - p.y * z };
    };

    render();

    if (api.instant) {
      Object.assign(view, flyTo(s.target, 2.4));
      render();
      s.rows[0].bg.setAttribute("class", "d-card2");
      s.popup.style.opacity = "1";
      api.step(3);
      api.poster();
    }

    // "Updated N s ago" ticks every second, resets on each poll
    let since = 2;
    api.spawn(async () => {
      for (;;) { await api.wait(1000); since += 1; s.updated.textContent = `${t.live} · ${since} ${t.ago}`; }
    });
    api.loop(s.faultRing, [{ transform: "scale(0.8)", opacity: 0.9 }, { transform: "scale(2.6)", opacity: 0 }], { duration: 1500, easing: "ease-out" });
    api.loop(s.liveDot, [{ opacity: 1 }, { opacity: 0.35 }], { duration: 1000, direction: "alternate" });

    api.step(0);
    await api.wait(900);

    api.step(1);
    for (let i = 0; i < 2; i++) {
      since = 0;
      s.updated.textContent = `${t.live} · 0 ${t.ago}`;
      await poll();
      await api.wait(1300);
    }

    api.step(2);
    s.rows[2].bg.setAttribute("class", "d-card2");
    await api.wait(1200);
    s.rows[2].bg.setAttribute("class", "");

    api.step(3);
    s.query.setAttribute("class", "d-tx dm");
    await api.type(s.query, "1112", 10);
    s.rows[0].bg.setAttribute("class", "d-card2");
    await api.wait(250);
    const from = { ...view };
    const to = flyTo(s.target, 2.4);
    await api.tick(1300, (p) => {
      // zoom out a touch mid-flight, like Leaflet's flyTo
      const z = from.z + (to.z - from.z) * p;
      view.z = z;
      view.tx = from.tx + (to.tx - from.tx) * p;
      view.ty = from.ty + (to.ty - from.ty) * p;
      render();
    }, "inOut");
    await api.show(s.popup, 320, "translateY(4px)");
    await api.tween(s.fuelBar, [{ transform: "scaleX(0)" }, { transform: "scaleX(1)" }], { dur: 500 });
    await api.wait(2200);
  },
};
