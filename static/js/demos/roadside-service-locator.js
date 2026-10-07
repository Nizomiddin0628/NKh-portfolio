/* Roadside Service Locator, drawn like a maps app: unit #1182 breaks down
   on I-40 west of Amarillo. The map pulls back to the 150-mile radius,
   shops drop in, the list first sorts by distance and then re-ranks by
   past outcomes, a route is drawn to the winner, and the closed job feeds
   its score back. Base map scales on zoom; labels, pins and cards are
   re-projected so they keep their size. */

import { attribution, controls, pathOf, pin, projector, road, scaleBar, shield, usShield } from "./map-kit.js";

const MW = 246;                                     // map width; the result list is on the right
const TRUCK = [-102.18, 35.235];
const P = projector({ lon0: TRUCK[0] - 123 / 53.5, lon1: TRUCK[0] - 123 / 53.5 + MW / 53.5, lat1: 35.235 + 125 / 65.5, latMid: 35.2, x: 0, y: 0, w: MW });

const ROADS = {
  i40: [[-106.7, 35.08], [-105.6, 34.98], [-104.68, 34.94], [-103.72, 35.17], [-103.33, 35.11], [-102.43, 35.24], [-101.83, 35.2], [-101.11, 35.2], [-100.25, 35.22], [-99.4, 35.25], [-97.5, 35.47]],
  i27: [[-101.83, 35.2], [-101.92, 34.98], [-101.76, 34.54], [-101.71, 34.18], [-101.85, 33.58], [-101.9, 32.4]],
  us287n: [[-101.83, 35.2], [-101.97, 35.86], [-102.07, 36.43], [-102.4, 37.3], [-102.6, 38.4]],
  us287s: [[-101.83, 35.2], [-101.36, 35.11], [-100.89, 34.94], [-100.54, 34.72], [-100.2, 34.43], [-99.3, 34.15], [-98.5, 33.9]],
  us60: [[-101.83, 35.2], [-102.4, 34.82], [-102.72, 34.64], [-103.2, 34.4], [-104.2, 34.47], [-105.8, 34.5]],
  us54: [[-103.72, 35.17], [-103.42, 35.36], [-102.52, 36.06], [-101.48, 36.5], [-100.9, 37.04], [-100.2, 37.8]],
  us87: [[-101.97, 35.86], [-102.52, 36.06], [-103.18, 36.45], [-104.44, 36.9], [-105.2, 37.6]],
  us84: [[-101.85, 33.58], [-102.6, 33.9], [-103.2, 34.4]],
  us70: [[-103.2, 34.4], [-103.33, 34.19], [-104.52, 33.39], [-105.6, 33.1]],
  us83: [[-100.25, 35.22], [-100.3, 36.2], [-100.6, 37.4]],
  us60e: [[-101.83, 35.2], [-100.96, 35.54], [-99.8, 36.1], [-98.6, 36.4]],
};
const PARKS = [
  [[-101.78, 35.0], [-101.62, 35.02], [-101.55, 34.94], [-101.6, 34.86], [-101.72, 34.88]],
  [[-101.12, 34.5], [-100.98, 34.48], [-100.96, 34.38], [-101.1, 34.36]],
  [[-102.9, 36.55], [-102.3, 36.6], [-102.2, 36.25], [-102.8, 36.2]],
  [[-103.9, 36.8], [-103.3, 36.85], [-103.2, 36.55], [-103.8, 36.5]],
];
const LAKES = [[-101.55, 35.66, 0.13, 0.05], [-103.5, 35.37, 0.09, 0.025], [-104.19, 35.39, 0.08, 0.035], [-102.1, 34.92, 0.03, 0.02]];
const BORDERS = [[[-103.04, 32.0], [-103.04, 37.0]], [[-103.04, 36.5], [-100.0, 36.5], [-100.0, 34.56], [-99.2, 34.35], [-98.1, 34.13]], [[-106.7, 37.0], [-94.0, 37.0]]];
const CITIES = [
  ["Amarillo", -101.83, 35.2, 1, "above"], ["Canyon", -101.92, 34.98, 0], ["Hereford", -102.4, 34.82, 0], ["Dumas", -101.97, 35.86, 0],
  ["Dalhart", -102.52, 36.06, 0], ["Tucumcari", -103.72, 35.17, 0], ["Clovis", -103.2, 34.4, 0], ["Vega", -102.43, 35.24, 0, "end"],
  ["Plainview", -101.71, 34.18, 0], ["Lubbock", -101.85, 33.58, 1], ["Childress", -100.2, 34.43, 0], ["Pampa", -100.96, 35.54, 0],
  ["Clarendon", -100.89, 34.94, 0], ["Santa Rosa", -104.68, 34.94, 0],
];
const STATES = [["TEXAS", -101.0, 34.05], ["NEW MEXICO", -104.4, 34.15], ["OKLAHOMA", -101.6, 36.78]];

const SHOPS = [
  { key: "A", name: "Mesa Diesel", ll: [-102.02, 35.125], mi: 12, stars: 3.6, n: 88, fix: 41, open: 0 },
  { key: "B", name: "Big Rig Pros", ll: [-101.74, 35.185], mi: 24, stars: 4.8, n: 212, fix: 92, open: 1 },
  { key: "C", name: "Desert Truck Care", ll: [-102.4, 34.83], mi: 31, stars: 4.3, n: 64, fix: 67, open: 1 },
];
const EXTRA = [[-102.43, 35.26], [-101.97, 35.86], [-103.72, 35.19], [-103.2, 34.42], [-100.2, 34.45], [-101.71, 34.2]];
const ROUTE = [TRUCK, [-102.06, 35.226], [-101.95, 35.212], [-101.83, 35.2], [-101.76, 35.2], SHOPS[1].ll];
const MI = 150 / 69;                                // 150 miles in degrees of latitude

export default {
  duration: 13500,
  rest: 1600,
  i18n: {
    en: {
      steps: [
        "Unit #1182 breaks down on I-40",
        "Shops within 150 miles are found",
        "Ranking weighs distance and past outcomes",
        "Every call-out is scored afterwards",
      ],
      q: "Truck repair", fault: "#1182 · Engine fault", dist: "Distance", best: "Best match", type: "Truck repair",
      open24: "Open 24 hours", closes: "Closes 6 PM", fix: "fixed", done: "Job closed · fixed in 2 h", min: "min",
    },
    uz: {
      steps: [
        "#1182 mashinasi I-40 trassasida buziladi",
        "150 mil radiusdagi ustaxonalar topiladi",
        "Reyting masofa va oldingi natijalarni hisobga oladi",
        "Har bir chaqiruvdan keyin natija baholanadi",
      ],
      q: "Yuk mashinasi ta'miri", fault: "#1182 · Dvigatel nosozligi", dist: "Masofa", best: "Eng mos", type: "Ta'mirlash",
      open24: "24 soat ochiq", closes: "18:00 da yopiladi", fix: "tuzatgan", done: "Ish yopildi · 2 soatda tuzatildi", min: "daq",
    },
    ru: {
      steps: [
        "Тягач #1182 ломается на I-40",
        "Находятся сервисы в радиусе 150 миль",
        "Рейтинг учитывает расстояние и прошлые итоги",
        "Каждый вызов потом оценивается",
      ],
      q: "Ремонт грузовиков", fault: "#1182 · Отказ двигателя", dist: "Расстояние", best: "Лучшее", type: "Ремонт",
      open24: "Круглосуточно", closes: "До 18:00", fix: "починили", done: "Заявка закрыта · за 2 ч", min: "мин",
    },
  },

  build(svg, { h }, t) {
    const uid = "rs" + Math.random().toString(36).slice(2, 8);
    const clip = h("clipPath", { id: `${uid}c` }, h("defs", {}, svg));
    h("rect", { x: 0, y: 0, width: MW, height: 250 }, clip);

    // ── Base map ──
    const frame = h("g", { "clip-path": `url(#${uid}c)` }, svg);
    const base = h("g", { class: "vb" }, frame);
    h("rect", { x: -900, y: -900, width: 2400, height: 2400, class: "m-land" }, base);
    PARKS.forEach((pg) => h("path", { d: pathOf(pg, P, true), class: "m-park" }, base));
    LAKES.forEach(([lon, lat, rx, ry]) => { const [x, y] = P([lon, lat]); h("ellipse", { cx: x, cy: y, rx: rx * P.kx, ry: ry * P.ky, class: "m-water" }, base); });
    BORDERS.forEach((b) => h("path", { d: pathOf(b, P), class: "m-border", "stroke-width": 0.8 }, base));
    Object.entries(ROADS).forEach(([k, pts]) => road(h, base, pathOf(pts, P), k === "i40" || k === "i27" ? "hwy" : "major"));
    const route = h("g", { opacity: 0 }, base);
    const routeD = pathOf(ROUTE, P);
    h("path", { d: routeD, fill: "none", stroke: "#fff", "stroke-width": 6, "stroke-linecap": "round", "stroke-linejoin": "round", opacity: 0.9 }, route);
    const routeLine = h("path", { d: routeD, class: "m-route", "stroke-width": 3.6 }, route);
    base.querySelectorAll("path").forEach((el) => el.setAttribute("vector-effect", "non-scaling-stroke"));

    // ── Overlay ──
    const over = h("g", { "clip-path": `url(#${uid}c)` }, svg);
    const ring = h("circle", { r: 1, class: "m-routef", "fill-opacity": 0.07, style: "stroke: var(--map-route)", "stroke-width": 1.2, "stroke-dasharray": "4 3", opacity: 0 }, over);
    const ringLabel = h("g", { opacity: 0 }, over);
    h("rect", { x: -24, y: -8, width: 48, height: 15, rx: 7.5, class: "m-ui", "stroke-width": 0.8 }, ringLabel);
    h("text", { x: 0, y: 2.8, "font-size": 8, class: "d-tx dm db", "text-anchor": "middle", text: "150 mi" }, ringLabel);

    const marks = [];   // everything that follows the map: { ll, el, dx, dy }
    STATES.forEach(([name, lon, lat]) => marks.push({ ll: [lon, lat], el: h("text", { "font-size": 7, class: "m-label", "text-anchor": "middle", "letter-spacing": 2.2, "font-weight": 600, opacity: 0.55, text: name }, over), text: true }));
    CITIES.forEach(([name, lon, lat, big, side]) => {
      const left = side === "end", above = side === "above";
      const minZ = big ? 0 : 0.8;                    // small towns appear only when zoomed in
      marks.push({ ll: [lon, lat], minZ, el: h("circle", { r: big ? 2.3 : 1.7, style: "fill: var(--map-label); stroke: var(--map-halo)", "stroke-width": 0.9 }, over), dot: true });
      marks.push({ ll: [lon, lat], minZ, el: h("text", { "font-size": big ? 8.5 : 7.5, class: "m-label", "font-weight": big ? 600 : 500, "text-anchor": above ? "middle" : left ? "end" : "start", text: name }, over), text: true, dx: above ? 0 : left ? -4 : 4, dy: above ? -6 : 3 });
    });
    [["40", -103.0, 35.13, shield], ["27", -101.74, 34.75, shield], ["287", -101.93, 35.55, usShield], ["60", -102.62, 34.69, usShield]]
      .forEach(([n, lon, lat, fn]) => marks.push({ ll: [lon, lat], el: fn(h, over, 0, 0, n), g: true, minZ: n === "40" ? 0 : 0.8 }));

    const extras = EXTRA.map((ll) => { const p = pin(h, over, 0, 0, { color: "#9aa0a6", edge: "#70757a" }); p.g.style.opacity = "0"; marks.push({ ll, el: p.g, g: true }); return p; });
    SHOPS.forEach((s) => { s.pin = pin(h, over, 0, 0, {}); s.pin.g.style.opacity = "0"; marks.push({ ll: s.ll, el: s.pin.g, g: true }); });

    // Broken-down truck
    const truck = h("g", {}, over);
    const halo = h("circle", { r: 7, fill: "#d93025", opacity: 0.25 }, truck);
    h("circle", { r: 6.5, fill: "#d93025", stroke: "#fff", "stroke-width": 1.6 }, truck);
    h("path", { d: "M-3.4 -1.6h3.6v3.4h-3.6zM0.2 -0.4h1.8l1.2 1.3v0.9h-3z", fill: "#fff" }, truck);
    marks.push({ ll: TRUCK, el: truck, g: true });
    const tip = h("g", {}, over);
    h("rect", { x: -54, y: -31, width: 108, height: 17, rx: 5, class: "m-ui", "stroke-width": 0.8, style: "filter: drop-shadow(0 2px 4px rgba(0,0,0,0.15))" }, tip);
    h("text", { x: 0, y: -19.5, "font-size": 8, fill: "#d93025", "text-anchor": "middle", class: "db", text: t.fault }, tip);
    marks.push({ ll: TRUCK, el: tip, g: true });

    const eta = h("g", { opacity: 0 }, over);
    h("rect", { x: -30, y: -22, width: 60, height: 17, rx: 8.5, class: "m-routef", style: "filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2))" }, eta);
    h("text", { x: 0, y: -10.5, "font-size": 8, fill: "#fff", "text-anchor": "middle", class: "db", text: `26 ${t.min} · 24 mi` }, eta);
    marks.push({ ll: [-101.93, 35.262], el: eta, g: true });

    controls(h, svg, 222, 8);
    attribution(h, svg, MW, 250, "© OpenStreetMap");
    const scale = scaleBar(h, svg, 8, 240, 37, "25 mi");

    // ── Results panel ──
    const X = MW;
    h("rect", { x: X, y: 0, width: 400 - X, height: 250, class: "d-card" }, svg);
    h("rect", { x: X + 8, y: 8, width: 138, height: 22, rx: 11, class: "d-card2" }, svg);
    h("circle", { cx: X + 20, cy: 18.5, r: 3.4, fill: "none", class: "s-tx3", "stroke-width": 1.2 }, svg);
    h("path", { d: `M${X + 22.6} 21.1l2.4 2.4`, class: "s-tx3", "stroke-width": 1.2, "stroke-linecap": "round" }, svg);
    h("text", { x: X + 30, y: 22.5, "font-size": 8.5, class: "d-tx", text: t.q }, svg);
    h("rect", { x: X + 8, y: 36, width: 42, height: 15, rx: 7.5, fill: "none", class: "s-line", "stroke-width": 1 }, svg);
    h("text", { x: X + 29, y: 46.5, "font-size": 7.5, class: "d-tx2 dm", "text-anchor": "middle", text: "150 mi" }, svg);
    h("rect", { x: X + 55, y: 36, width: 91, height: 15, rx: 7.5, class: "d-acc", opacity: 0.12 }, svg);
    const sort = h("text", { x: X + 100, y: 46.5, "font-size": 7.5, class: "d-acc db", "text-anchor": "middle", text: `${t.dist} ▾` }, svg);

    const ROW = 56, TOP = 58;
    const star = (x, y, on, parent) => h("path", {
      d: `M${x} ${y - 3}l0.9 1.9 2 0.25-1.5 1.4 0.4 2-1.8-1-1.8 1 0.4-2-1.5-1.4 2-0.25z`,
      fill: on ? "#fbbc04" : "none", stroke: on ? "#fbbc04" : "#c4c7c5", "stroke-width": 0.6,
    }, parent);
    SHOPS.forEach((s, i) => {
      const y = TOP + i * ROW;
      const g = h("g", { opacity: 0 }, svg);
      const sel = h("rect", { x: X + 2, y: y - 2, width: 3, height: ROW - 6, rx: 1.5, class: "m-routef", opacity: 0 }, g);
      h("text", { x: X + 12, y: y + 10, "font-size": 9.5, class: "d-tx db", text: s.name }, g);
      h("text", { x: X + 12, y: y + 22, "font-size": 8, class: "d-tx2", text: s.stars.toFixed(1) }, g);
      for (let k = 0; k < 5; k++) star(X + 30 + k * 7.5, y + 19.5, k < Math.round(s.stars), g);
      h("text", { x: X + 68, y: y + 22, "font-size": 7.5, class: "d-tx3", text: `(${s.n})` }, g);
      h("text", { x: X + 12, y: y + 33, "font-size": 7.5, class: "d-tx3", text: `${t.type} · ${s.mi} mi` }, g);
      h("text", { x: X + 12, y: y + 44, "font-size": 7.5, fill: s.open ? "#188038" : "#b06000", text: s.open ? t.open24 : t.closes }, g);
      const chip = h("g", { opacity: 0 }, g);
      const col = s.fix >= 80 ? "#188038" : s.fix >= 60 ? "#b06000" : "#d93025";
      h("rect", { x: X + 100, y: y + 35, width: 46, height: 13, rx: 6.5, fill: col, opacity: 0.12 }, chip);
      s.fixEl = h("text", { x: X + 123, y: y + 44.3, "font-size": 7.5, fill: col, "text-anchor": "middle", class: "dm db", text: `${s.fix}% ${t.fix}` }, chip);
      h("line", { x1: X + 10, x2: 392, y1: y + ROW - 5, y2: y + ROW - 5, class: "d-line" }, g);
      Object.assign(s, { row: g, chip, sel, rank: i });
    });
    const toast = h("g", { opacity: 0 }, svg);
    h("rect", { x: X + 6, y: 216, width: 142, height: 26, rx: 6, fill: "#202124" }, toast);
    h("text", { x: X + 14, y: 232.5, "font-size": 8, fill: "#e8eaed", text: `✓ ${t.done}` }, toast);

    return { base, marks, ring, ringLabel, extras, truck, halo, tip, route, routeLine, eta, sort, toast, scale, ROW };
  },

  async play(api, s, t) {
    const view = { z: 1, tx: 0, ty: 0 };
    const centre = (ll, z, cx = 123, cy = 125) => { const [x, y] = P(ll); return { z, tx: cx - x * z, ty: cy - y * z }; };
    const at = (ll) => { const [x, y] = P(ll); return [view.tx + x * view.z, view.ty + y * view.z]; };
    const render = () => {
      s.base.style.transform = `translate(${view.tx.toFixed(2)}px, ${view.ty.toFixed(2)}px) scale(${view.z.toFixed(4)})`;
      for (const m of s.marks) {
        if (m.minZ !== undefined) m.el.style.display = view.z < m.minZ ? "none" : "";
        const [x, y] = at(m.ll);
        if (m.g) m.el.setAttribute("transform", `translate(${x.toFixed(1)} ${y.toFixed(1)})`);
        else if (m.dot) { m.el.setAttribute("cx", x.toFixed(1)); m.el.setAttribute("cy", y.toFixed(1)); }
        else { m.el.setAttribute("x", (x + (m.dx || 0)).toFixed(1)); m.el.setAttribute("y", (y + (m.dy || 0)).toFixed(1)); }
      }
      const [tx, ty] = at(TRUCK);
      const r = MI * P.ky * view.z;
      s.ring.setAttribute("cx", tx.toFixed(1)); s.ring.setAttribute("cy", ty.toFixed(1)); s.ring.setAttribute("r", r.toFixed(1));
      s.ringLabel.setAttribute("transform", `translate(${tx.toFixed(1)} ${(ty - r + 12).toFixed(1)})`);
      // Scale bar follows the zoom, like a real map
      const pxPerMile = (P.kx * view.z) / 56.6;
      const nice = [5, 10, 20, 25, 50, 100, 200].find((m) => m * pxPerMile >= 28) || 200;
      const w = nice * pxPerMile;
      s.scale.querySelector("path").setAttribute("d", `M8 236V240H${(8 + w).toFixed(1)}V236`);
      s.scale.querySelector("text").textContent = `${nice} mi`;
    };
    const fly = (to, dur) => {
      const from = { ...view };
      return api.tick(dur, (p) => {
        // pull back a little in the middle of the move, like a maps app
        const bump = Math.sin(Math.PI * p) * 0.12 * Math.min(from.z, to.z);
        view.z = from.z + (to.z - from.z) * p - bump;
        const cx = 123, cy = 125;
        const fx = (cx - from.tx) / from.z, fy = (cy - from.ty) / from.z;
        const gx = (cx - to.tx) / to.z, gy = (cy - to.ty) / to.z;
        const mx = fx + (gx - fx) * p, my = fy + (gy - fy) * p;
        view.tx = cx - mx * view.z; view.ty = cy - my * view.z;
        render();
      }, "inOut");
    };
    const rerank = async (order) => Promise.all(SHOPS.map((sh) => {
      const dy = (order.indexOf(sh.key) - sh.rank) * s.ROW;
      return api.tween(sh.row, [{ transform: "translateY(0px)" }, { transform: `translateY(${dy}px)` }], { dur: 650, ease: "cubic-bezier(0.65, 0, 0.35, 1)" });
    }));

    Object.assign(view, centre(TRUCK, 1));
    render();

    if (api.instant) {
      Object.assign(view, centre([-102.02, 35.215], 3.2, 123, 135));
      render();
      SHOPS.forEach((sh) => { sh.pin.g.style.opacity = "1"; sh.row.style.opacity = "1"; sh.chip.style.opacity = "1"; });
      s.extras.forEach((p) => { p.g.style.opacity = "1"; });
      const order = ["B", "C", "A"];
      SHOPS.forEach((sh) => { sh.row.style.transform = `translateY(${(order.indexOf(sh.key) - sh.rank) * s.ROW}px)`; });
      SHOPS[1].sel.style.opacity = "1";
      s.sort.textContent = `${t.best} ▾`;
      s.route.style.opacity = "1"; s.eta.style.opacity = "1";
      api.step(2);
      api.poster();
    }

    api.loop(s.halo, [{ transform: "scale(1)", opacity: 0.45 }, { transform: "scale(2.6)", opacity: 0 }], { duration: 1400, easing: "ease-out" });

    api.step(0);
    await api.wait(1300);
    await api.hide(s.tip, 250);

    api.step(1);
    await fly(centre(TRUCK, 0.5, 123, 128), 1300);
    s.ring.style.opacity = "1";
    await api.tween(s.ring, [{ opacity: 0 }, { opacity: 1 }], { dur: 400 });
    api.tween(s.ringLabel, [{ opacity: 0 }, { opacity: 1 }], { dur: 300 });
    const pins = [...s.extras.map((p) => p.g), ...SHOPS.map((sh) => sh.pin.g)];
    for (const g of pins) await api.tween(g, [{ opacity: 0 }, { opacity: 1 }], { dur: 140 });
    for (const sh of SHOPS) await api.show(sh.row, 240, "translateY(6px)");
    await api.wait(500);

    api.step(2);
    for (const sh of SHOPS) api.show(sh.chip, 240);
    await api.wait(500);
    s.sort.textContent = `${t.best} ▾`;
    await rerank(["B", "C", "A"]);
    SHOPS[1].sel.style.opacity = "1";
    await fly(centre([-102.02, 35.215], 3.2, 123, 135), 1300);
    s.route.style.opacity = "1";
    await api.draw(s.routeLine, 800);
    await api.tween(s.eta, [{ opacity: 0 }, { opacity: 1 }], { dur: 300 });
    await api.wait(900);

    api.step(3);
    await api.show(s.toast, 320, "translateY(8px)");
    await api.count(SHOPS[1].fixEl, 92, 93, 500, (v) => `${Math.round(v)}% ${t.fix}`);
    await api.wait(1800);
  },
};
