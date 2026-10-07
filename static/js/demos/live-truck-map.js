/* Live Truck Map: a dot-matrix map of the US with trucks moving along the
   interstates. The feed refreshes, nearby trucks sit in clusters, a unit is
   searched and the map flies to it: speed, road and a low-fuel warning. */

const OUTLINE = [
  [-124.7, 48.4], [-122.8, 49.0], [-95.2, 49.0], [-94.8, 49.4], [-89.6, 48.0], [-84.8, 46.6], [-83.4, 45.8],
  [-82.4, 43.0], [-79.0, 43.3], [-76.5, 44.2], [-74.7, 45.0], [-71.5, 45.0], [-69.2, 47.4], [-67.8, 47.1],
  [-67.0, 44.8], [-70.6, 43.0], [-70.0, 41.7], [-71.9, 41.3], [-74.0, 40.6], [-74.9, 38.9], [-75.9, 37.3],
  [-75.5, 35.2], [-77.9, 33.9], [-80.8, 32.0], [-81.4, 30.4], [-80.1, 26.9], [-80.4, 25.2], [-81.8, 26.1],
  [-82.8, 27.9], [-83.6, 29.9], [-85.3, 29.7], [-87.6, 30.3], [-89.6, 30.2], [-89.4, 29.1], [-91.4, 29.4],
  [-93.8, 29.7], [-95.0, 29.2], [-97.2, 27.6], [-97.4, 25.9], [-99.1, 26.4], [-101.4, 29.8], [-103.1, 29.0],
  [-104.5, 29.6], [-106.5, 31.8], [-108.2, 31.3], [-111.1, 31.3], [-114.8, 32.5], [-117.1, 32.5], [-118.5, 34.0],
  [-120.6, 34.6], [-121.9, 36.6], [-122.5, 37.8], [-123.8, 39.8], [-124.2, 41.9], [-124.1, 43.7], [-124.0, 46.3],
];
const ROADS = {
  "I-5": [[-117.16, 32.72], [-118.24, 34.05], [-121.49, 38.58], [-122.68, 45.52], [-122.33, 47.61]],
  "I-10": [[-118.24, 34.05], [-112.07, 33.45], [-106.49, 31.76], [-98.49, 29.42], [-95.37, 29.76], [-90.07, 29.95], [-81.66, 30.33]],
  "I-40": [[-118.24, 34.05], [-117.0, 34.9], [-111.65, 35.2], [-106.65, 35.08], [-101.83, 35.22], [-97.52, 35.47], [-92.29, 34.75], [-90.05, 35.15], [-86.78, 36.16], [-78.64, 35.78]],
  "I-80": [[-122.42, 37.77], [-119.81, 39.53], [-111.89, 40.76], [-104.82, 41.14], [-95.94, 41.26], [-87.63, 41.88], [-81.69, 41.5], [-74.0, 40.71]],
  "I-35": [[-99.5, 27.5], [-98.49, 29.42], [-97.74, 30.27], [-96.8, 32.78], [-97.52, 35.47], [-94.58, 39.1], [-93.6, 41.59], [-93.27, 44.98]],
  "I-95": [[-80.19, 25.76], [-81.66, 30.33], [-81.1, 32.08], [-77.44, 37.54], [-76.61, 39.29], [-74.0, 40.71], [-71.06, 42.36]],
  "I-70": [[-104.99, 39.74], [-94.58, 39.1], [-90.2, 38.63], [-86.16, 39.77], [-82.99, 39.96], [-76.61, 39.29]],
};

const K = 8.1;
const px = ([lon, lat]) => [14 + (lon + 125) * 0.79 * K, 30 + (49.6 - lat) * K];

function inside([x, y], poly) {
  let ins = false;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const [xi, yi] = poly[i], [xj, yj] = poly[j];
    if ((yi > y) !== (yj > y) && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) ins = !ins;
  }
  return ins;
}

export default {
  duration: 11300,
  rest: 1400,
  i18n: {
    en: {
      steps: [
        "575 trucks, positions pulled from the Motive API",
        "The map refreshes every ~10 seconds",
        "Nearby trucks group into clusters",
        "Find a unit: speed, fuel and faults at a glance",
      ],
      find: "Find unit", trucks: "trucks", updated: "updated", fuel: "Fuel", low: "Low fuel",
    },
    uz: {
      steps: [
        "575 ta mashina, joylashuvi Motive API'dan olinadi",
        "Xarita har ~10 soniyada yangilanadi",
        "Yaqin mashinalar klasterlarga birlashadi",
        "Mashinani toping: tezlik, yoqilg'i va nosozlik bir qarashda",
      ],
      find: "Mashina raqami", trucks: "ta mashina", updated: "yangilandi", fuel: "Yoqilg'i", low: "Yoqilg'i kam",
    },
    ru: {
      steps: [
        "575 тягачей, координаты из Motive API",
        "Карта обновляется каждые ~10 секунд",
        "Соседние машины собираются в кластеры",
        "Найдите юнит: скорость, топливо и неисправности сразу",
      ],
      find: "Найти юнит", trucks: "машин", updated: "обновлено", fuel: "Топливо", low: "Мало топлива",
    },
  },

  build(svg, { h, rng }, t) {
    const R = rng(5);
    const poly = OUTLINE.map(px);
    const map = h("g", { class: "vb" }, svg);

    // Dot-matrix land: one path, one draw call
    let dots = "";
    for (let y = 30; y < 236; y += 6.2) {
      for (let x = 10; x < 392; x += 6.2) {
        if (inside([x, y], poly)) dots += `M${x.toFixed(1)} ${y.toFixed(1)}h0`;
      }
    }
    const land = h("path", { d: dots, class: "s-line", "stroke-width": 2.6, "stroke-linecap": "round", opacity: 0.9 }, map);

    // Interstates
    const roads = {};
    for (const [name, pts] of Object.entries(ROADS)) {
      const d = pts.map((p, i) => `${i ? "L" : "M"}${px(p).map((v) => v.toFixed(1)).join(" ")}`).join("");
      roads[name] = h("path", { d, fill: "none", class: "s-tx3", "stroke-width": 1.1, "stroke-linejoin": "round", opacity: 0.45 }, map);
    }

    // Clusters
    const cluster = (lon, lat, n) => {
      const [x, y] = px([lon, lat]);
      const g = h("g", { opacity: 0 }, map);
      h("circle", { cx: x, cy: y, r: 13, class: "d-acc", opacity: 0.18 }, g);
      h("circle", { cx: x, cy: y, r: 9.5, class: "d-acc" }, g);
      const label = h("text", { x, y: y + 3.4, "font-size": 9, fill: "#fff", "text-anchor": "middle", class: "dm db", text: n }, g);
      return { g, label };
    };
    const clusters = [cluster(-96.8, 32.78, "42"), cluster(-87.63, 41.88, "37"), cluster(-118.24, 34.05, "29")];

    // Trucks
    const names = Object.keys(ROADS);
    const trucks = [];
    for (let i = 0; i < 26; i++) {
      const road = roads[names[i % names.length]];
      trucks.push({
        road, len: road.getTotalLength(), pos: R(), speed: (0.012 + R() * 0.02) * (R() > 0.5 ? 1 : -1),
        el: h("circle", { r: 2.7, class: "d-tq" }, map),
      });
    }
    const fault = trucks[3];                                  // on I-80
    fault.el.setAttribute("class", "d-bad");
    const ring = h("circle", { r: 3, class: "s-bad", fill: "none", "stroke-width": 1.2 }, map);
    const target = { road: roads["I-40"], len: roads["I-40"].getTotalLength(), pos: 0.36, speed: 0.016 };
    target.el = h("circle", { r: 3.1, class: "d-warn" }, map);
    trucks.push(target);

    // ── HUD (outside the zoomed group) ──
    const search = h("g", {}, svg);
    h("rect", { x: 12, y: 10, width: 128, height: 24, rx: 12, class: "d-card" }, search);
    h("circle", { cx: 27, cy: 21.5, r: 4.2, fill: "none", class: "s-tx3", "stroke-width": 1.4 }, search);
    h("path", { d: "M30 24.5l3 3", class: "s-tx3", "stroke-width": 1.4, "stroke-linecap": "round" }, search);
    const q = h("text", { x: 39, y: 26, "font-size": 10.5, class: "d-tx3", text: t.find }, search);

    const hud = h("g", {}, svg);
    h("rect", { x: 268, y: 10, width: 120, height: 24, rx: 12, class: "d-card" }, hud);
    h("text", { x: 280, y: 26, "font-size": 10.5, class: "d-tx dm db", text: "575" }, hud);
    const hudLabel = h("text", { x: 304, y: 26, "font-size": 9.5, class: "d-tx2", text: t.trucks }, hud);
    const C = 2 * Math.PI * 6;
    h("circle", { cx: 374, cy: 22, r: 6, fill: "none", class: "s-line", "stroke-width": 2 }, hud);
    const arc = h("circle", { cx: 374, cy: 22, r: 6, fill: "none", class: "s-tq", "stroke-width": 2, "stroke-dasharray": C, "stroke-dashoffset": C, style: "transform: rotate(-90deg)" }, hud);

    // Tooltip card for the found truck
    const tip = h("g", { opacity: 0 }, svg);
    h("rect", { x: 222, y: 136, width: 164, height: 92, rx: 12, class: "d-card" }, tip);
    h("text", { x: 236, y: 158, "font-size": 13, class: "d-tx dd", text: "#1112" }, tip);
    h("rect", { x: 300, y: 146, width: 76, height: 17, rx: 8.5, class: "d-warn", opacity: 0.18 }, tip);
    h("text", { x: 338, y: 158, "font-size": 9, class: "d-warn db", "text-anchor": "middle", text: t.low }, tip);
    h("text", { x: 236, y: 180, "font-size": 10.5, class: "d-tx2 dm", text: "63 mph · I-40 W" }, tip);
    h("text", { x: 236, y: 203, "font-size": 9.5, class: "d-tx3", text: t.fuel }, tip);
    h("rect", { x: 236, y: 210, width: 136, height: 5, rx: 2.5, class: "d-card2" }, tip);
    const fuel = h("rect", { x: 236, y: 210, width: 136 * 0.12, height: 5, rx: 2.5, class: "d-warn o-l" }, tip);
    h("text", { x: 372, y: 203, "font-size": 9.5, class: "d-warn dm db", "text-anchor": "end", text: "12%" }, tip);
    const leader = h("path", { fill: "none", class: "s-acc", "stroke-width": 1, "stroke-dasharray": "3 3", opacity: 0 }, svg);

    return { map, land, roads, clusters, trucks, fault, ring, target, q, arc, C, hudLabel, tip, fuel, leader, t };
  },

  async play(api, s, t) {
    const place = (tr) => {
      const pt = tr.road.getPointAtLength(tr.pos * tr.len);
      tr.el.setAttribute("cx", pt.x.toFixed(1));
      tr.el.setAttribute("cy", pt.y.toFixed(1));
      return pt;
    };
    s.trucks.forEach(place);
    const placeRing = () => {
      s.ring.setAttribute("cx", s.fault.el.getAttribute("cx"));
      s.ring.setAttribute("cy", s.fault.el.getAttribute("cy"));
    };
    placeRing();

    const zoomTo = (pt, z) => `translate(${(200 - pt.x * z).toFixed(1)}px, ${(120 - pt.y * z).toFixed(1)}px) scale(${z})`;
    // After the zoom the found truck sits at the stage centre (200, 120)
    const showTip = () => s.leader.setAttribute("d", "M205 124 L222 150");

    if (api.instant) {
      s.clusters.forEach((c) => { c.g.style.opacity = "1"; });
      const pt = place(s.target);
      s.map.style.transform = zoomTo(pt, 2.3);
      showTip();
      s.tip.style.opacity = "1";
      s.leader.style.opacity = "0.8";
      s.q.textContent = "1112";
      s.q.setAttribute("class", "d-tx dm");
      api.step(3);
      api.poster();
    }

    let frozen = false;
    api.spawn(() => api.tick(Infinity, () => {
      for (const tr of s.trucks) {
        if (frozen && tr === s.target) continue;
        tr.pos = (tr.pos + tr.speed * 0.016 + 1) % 1;
        place(tr);
      }
      placeRing();
    }));
    api.loop(s.ring, [{ transform: "scale(1)", opacity: 0.9 }, { transform: "scale(3.4)", opacity: 0 }], { duration: 1400, easing: "ease-out" });

    api.step(0);
    await api.tween(s.land, [{ opacity: 0 }, { opacity: 0.9 }], { dur: 700 });
    await Promise.all(Object.values(s.roads).map((r, i) => api.draw(r, 900 + i * 60)));

    api.step(1);
    await api.tween(s.arc, [{ strokeDashoffset: s.C }, { strokeDashoffset: 0 }], { dur: 2200, ease: "linear" });
    const old = s.hudLabel.textContent;
    s.hudLabel.textContent = s.t.updated;
    s.hudLabel.setAttribute("class", "d-tq");
    s.arc.style.strokeDashoffset = String(s.C);
    await api.wait(700);
    s.hudLabel.textContent = old;
    s.hudLabel.setAttribute("class", "d-tx2");

    api.step(2);
    for (const c of s.clusters) await api.show(c.g, 360, "scale(0.4)");
    await api.wait(700);

    api.step(3);
    s.q.setAttribute("class", "d-tx dm");
    s.q.textContent = "";
    await api.type(s.q, "1112", 9);
    frozen = true;
    const pt = place(s.target);
    await api.tween(s.map, [{ transform: "translate(0px, 0px) scale(1)" }, { transform: zoomTo(pt, 2.3) }], { dur: 1100, ease: "cubic-bezier(0.65, 0, 0.35, 1)" });
    showTip();
    api.tween(s.leader, [{ opacity: 0 }, { opacity: 0.8 }], { dur: 300 }).catch(() => {});
    await api.show(s.tip, 420, "translateY(8px)");
    await api.tween(s.fuel, [{ transform: "scaleX(0)" }, { transform: "scaleX(1)" }], { dur: 600 });
    await api.wait(2000);
  },
};
