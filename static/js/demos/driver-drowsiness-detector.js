/* Drowsiness detector, shown as the Python tool actually looks: an
   OpenCV window with the MediaPipe face mesh over a dim cabin camera,
   cv2.putText overlays, and a matplotlib window plotting EAR live.
   Two normal blinks pass; a long closure crosses 0.21, the alarm fires. */

const THR = 0.21;
const N = 70;
const PLOT = { x: 262, y: 66, w: 124, h: 120 };
const FACE = { cx: 122, cy: 132, rx: 56, ry: 74 };
const EYES = [{ cx: 100, cy: 118 }, { cx: 145, cy: 118 }];

// Bowyer–Watson Delaunay, enough for ~150 points
function delaunay(pts) {
  const big = [[-1000, -1000], [2000, -1000], [500, 2000]];
  const all = pts.concat(big);
  const n = pts.length;
  let tris = [[n, n + 1, n + 2]];
  const circum = ([a, b, c]) => {
    const [ax, ay] = all[a], [bx, by] = all[b], [cx, cy] = all[c];
    const d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by));
    const ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d;
    const uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d;
    return [ux, uy, (ax - ux) ** 2 + (ay - uy) ** 2];
  };
  for (let i = 0; i < n; i++) {
    const [px, py] = all[i];
    const bad = tris.filter((t) => { const [ux, uy, r2] = circum(t); return (px - ux) ** 2 + (py - uy) ** 2 < r2; });
    const edges = [];
    bad.forEach((t) => [[t[0], t[1]], [t[1], t[2]], [t[2], t[0]]].forEach((e) => {
      const k = edges.findIndex((f) => (f[0] === e[1] && f[1] === e[0]) || (f[0] === e[0] && f[1] === e[1]));
      if (k >= 0) edges.splice(k, 1); else edges.push(e);
    }));
    tris = tris.filter((t) => !bad.includes(t));
    edges.forEach(([a, b]) => tris.push([a, b, i]));
  }
  return tris.filter((t) => t.every((v) => v < n));
}

let MESH = null;
function mesh() {
  if (MESH) return MESH;
  let seed = 7;
  const R = () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; };
  const pts = [];
  // contour: oval with a narrower jaw
  for (let i = 0; i < 36; i++) {
    const a = (i / 36) * Math.PI * 2;
    const jaw = Math.sin(a) > 0 ? 1 - 0.18 * Math.sin(a) ** 3 : 1;
    pts.push([FACE.cx + Math.cos(a) * FACE.rx * jaw, FACE.cy + Math.sin(a) * FACE.ry]);
  }
  // interior with jitter, denser around eyes, nose and mouth
  for (let y = FACE.cy - FACE.ry + 10; y < FACE.cy + FACE.ry - 6; y += 11) {
    for (let x = FACE.cx - FACE.rx + 8; x < FACE.cx + FACE.rx - 6; x += 11) {
      const dx = (x - FACE.cx) / FACE.rx, dy = (y - FACE.cy) / FACE.ry;
      if (dx * dx + dy * dy < 0.82) pts.push([x + (R() - 0.5) * 5, y + (R() - 0.5) * 5]);
    }
  }
  [[122, 140], [116, 150], [128, 150], [122, 154], [104, 172], [140, 172], [122, 168], [122, 178], [112, 176], [132, 176],
    [86, 104], [98, 101], [112, 104], [132, 104], [146, 101], [158, 104]].forEach((p) => pts.push(p));
  MESH = { pts, tris: delaunay(pts) };
  return MESH;
}

export default {
  duration: 8000,
  rest: 1200,
  i18n: {
    en: {
      steps: [
        "MediaPipe tracks 468 landmarks on the face",
        "Eye Aspect Ratio is computed on every frame",
        "A normal blink is ignored",
        "Eyes closed too long — the alarm goes off",
      ],
    },
    uz: {
      steps: [
        "MediaPipe yuzdagi 468 ta nuqtani kuzatadi",
        "Har kadrda Eye Aspect Ratio hisoblanadi",
        "Oddiy ko'z qirpish e'tiborga olinmaydi",
        "Ko'z uzoq yumilib qolsa — signal chalinadi",
      ],
    },
    ru: {
      steps: [
        "MediaPipe отслеживает 468 точек лица",
        "Eye Aspect Ratio считается на каждом кадре",
        "Обычное моргание игнорируется",
        "Глаза закрыты слишком долго — срабатывает сигнал",
      ],
    },
  },

  build(svg, { h }) {
    const uid = "dz" + Math.random().toString(36).slice(2, 8);
    const defs = h("defs", {}, svg);
    const bg = h("radialGradient", { id: `${uid}bg`, cx: 0.45, cy: 0.45, r: 0.8 }, defs);
    h("stop", { offset: 0, "stop-color": "#2b2f35" }, bg);
    h("stop", { offset: 1, "stop-color": "#0d0f12" }, bg);
    const skin = h("radialGradient", { id: `${uid}sk`, cx: 0.45, cy: 0.4, r: 0.7 }, defs);
    h("stop", { offset: 0, "stop-color": "#6a6662" }, skin);
    h("stop", { offset: 0.7, "stop-color": "#45423f" }, skin);
    h("stop", { offset: 1, "stop-color": "#25272a" }, skin);

    // ── OpenCV window ──
    const W = { x: 4, y: 4, w: 240, h: 242 };
    h("rect", { x: W.x, y: W.y, width: W.w, height: W.h, rx: 4, fill: "#f0f0f0", stroke: "#b9b9b9" }, svg);
    h("text", { x: W.x + 8, y: W.y + 12, "font-size": 7.5, fill: "#222", text: "Drowsiness Detector" }, svg);
    h("path", { d: `M${W.x + W.w - 44} ${W.y + 9}h6M${W.x + W.w - 28} ${W.y + 6}h5v5h-5zM${W.x + W.w - 13} ${W.y + 6}l5 5m0-5-5 5`, stroke: "#333", "stroke-width": 0.9, fill: "none" }, svg);
    const F = { x: W.x + 1, y: W.y + 17, w: W.w - 2, h: W.h - 18 };
    h("rect", { x: F.x, y: F.y, width: F.w, height: F.h, fill: `url(#${uid}bg)` }, svg);
    // the driver: shoulders, neck, head in low light
    h("path", { d: `M${F.x} ${F.y + F.h} C40 205 70 196 98 194 L146 194 C176 196 206 205 ${F.x + F.w} ${F.y + F.h} Z`, fill: "#1c1e21" }, svg);
    h("rect", { x: 104, y: 180, width: 36, height: 22, fill: "#3a3836" }, svg);
    h("ellipse", { cx: FACE.cx, cy: FACE.cy, rx: FACE.rx + 3, ry: FACE.ry + 3, fill: `url(#${uid}sk)` }, svg);
    h("path", { d: "M66 104 C70 50 176 50 178 104 C176 80 160 66 122 64 C86 66 70 80 66 104 Z", fill: "#1a1a1b" }, svg);

    const { pts, tris } = mesh();
    let d = "";
    tris.forEach(([a, b, c]) => { d += `M${pts[a][0].toFixed(1)} ${pts[a][1].toFixed(1)}L${pts[b][0].toFixed(1)} ${pts[b][1].toFixed(1)}L${pts[c][0].toFixed(1)} ${pts[c][1].toFixed(1)}Z`; });
    h("path", { d, fill: "none", stroke: "#c0c0c0", "stroke-width": 0.35, opacity: 0.45 }, svg);
    h("path", { d: pts.map(([x, y]) => `M${x.toFixed(1)} ${y.toFixed(1)}h0`).join(""), stroke: "#e8e8e8", "stroke-width": 1.2, "stroke-linecap": "round", opacity: 0.55 }, svg);

    const eyes = EYES.map((e) => ({
      ...e,
      shape: h("path", { fill: "none", stroke: "#30ff30", "stroke-width": 1 }, svg),
      dots: h("path", { stroke: "#30ff30", "stroke-width": 2.2, "stroke-linecap": "round" }, svg),
      iris: h("circle", { cx: e.cx, cy: e.cy, r: 3.6, fill: "none", stroke: "#ff3030", "stroke-width": 0.9 }, svg),
    }));

    // cv2.putText overlays
    const cv = (x, y, size, fill, text) => h("text", { x, y, "font-size": size, fill, "font-weight": 600, style: "font-family: Arial, Helvetica, sans-serif", text }, svg);
    const ear = cv(F.x + 8, F.y + 16, 11, "#30ff30", "EAR: 0.31");
    const blinks = cv(F.x + 8, F.y + 30, 9, "#30ff30", "Blinks: 0");
    h("text", { x: F.x + F.w - 6, y: F.y + 14, "font-size": 8, fill: "#30ff30", "text-anchor": "end", style: "font-family: Arial, Helvetica, sans-serif", text: "FPS: 30" }, svg);
    const alert = cv(F.x + 22, F.y + F.h - 14, 15, "#ff2d2d", "DROWSINESS ALERT!");
    alert.style.opacity = "0";
    const frame = h("rect", { x: F.x + 1.5, y: F.y + 1.5, width: F.w - 3, height: F.h - 3, fill: "none", stroke: "#ff2d2d", "stroke-width": 3, opacity: 0 }, svg);

    // ── matplotlib window ──
    const M = { x: 250, y: 30, w: 146, h: 190 };
    h("rect", { x: M.x, y: M.y, width: M.w, height: M.h, rx: 4, fill: "#ffffff", stroke: "#b9b9b9" }, svg);
    h("rect", { x: M.x, y: M.y, width: M.w, height: 16, rx: 4, fill: "#f0f0f0" }, svg);
    h("text", { x: M.x + 8, y: M.y + 11, "font-size": 7.5, fill: "#222", text: "Figure 1" }, svg);
    h("text", { x: PLOT.x + PLOT.w / 2, y: PLOT.y - 8, "font-size": 8, fill: "#111", "text-anchor": "middle", text: "Eye Aspect Ratio" }, svg);
    h("rect", { x: PLOT.x, y: PLOT.y, width: PLOT.w, height: PLOT.h, fill: "#fff", stroke: "#222", "stroke-width": 0.8 }, svg);
    [0, 0.1, 0.2, 0.3, 0.4].forEach((v) => {
      const y = PLOT.y + PLOT.h - (v / 0.4) * PLOT.h;
      h("line", { x1: PLOT.x - 3, x2: PLOT.x, y1: y, y2: y, stroke: "#222", "stroke-width": 0.7 }, svg);
      h("text", { x: PLOT.x - 5, y: y + 2.5, "font-size": 6.5, fill: "#222", "text-anchor": "end", text: v.toFixed(1) }, svg);
    });
    const ty = PLOT.y + PLOT.h - (THR / 0.4) * PLOT.h;
    h("line", { x1: PLOT.x, x2: PLOT.x + PLOT.w, y1: ty, y2: ty, stroke: "#d62728", "stroke-width": 1, "stroke-dasharray": "4 2" }, svg);
    h("text", { x: PLOT.x + PLOT.w - 3, y: ty - 3, "font-size": 6.5, fill: "#d62728", "text-anchor": "end", text: "threshold 0.21" }, svg);
    const line = h("polyline", { fill: "none", stroke: "#1f77b4", "stroke-width": 1.3, "stroke-linejoin": "round" }, svg);
    h("text", { x: PLOT.x + PLOT.w / 2, y: PLOT.y + PLOT.h + 14, "font-size": 6.5, fill: "#222", "text-anchor": "middle", text: "frames" }, svg);

    return { eyes, ear, blinks, alert, frame, line };
  },

  async play(api, s) {
    const st = { o: 1, target: 1, samples: Array(N).fill(0.31), blinks: 0 };
    const earOf = (o) => 0.03 + 0.28 * o;

    const drawEye = (e, o) => {
      const w = 15, up = 7 * o + 0.4, dn = 4.2 * o + 0.4, n = 16;
      const top = [], bot = [];
      for (let i = 0; i <= n / 2; i++) {
        const tt = i / (n / 2), x = e.cx - w + tt * 2 * w, k = Math.sin(Math.PI * tt);
        top.push([x, e.cy - up * k]);
        bot.push([x, e.cy + dn * k]);
      }
      const ring = top.concat(bot.slice(1, -1).reverse());
      e.shape.setAttribute("d", "M" + ring.map(([x, y]) => `${x.toFixed(1)} ${y.toFixed(1)}`).join("L") + "Z");
      e.dots.setAttribute("d", ring.map(([x, y]) => `M${x.toFixed(1)} ${y.toFixed(1)}h0`).join(""));
      e.iris.setAttribute("opacity", o < 0.25 ? 0 : 1);
      e.iris.setAttribute("r", (3.6 * Math.min(1, o + 0.2)).toFixed(2));
    };
    const render = () => {
      s.eyes.forEach((e) => drawEye(e, st.o));
      const pts = st.samples.map((v, i) => `${(PLOT.x + (i / (N - 1)) * PLOT.w).toFixed(1)},${(PLOT.y + PLOT.h - (v / 0.4) * PLOT.h).toFixed(1)}`);
      s.line.setAttribute("points", pts.join(" "));
      const e = earOf(st.o);
      s.ear.textContent = `EAR: ${e.toFixed(2)}`;
      s.ear.setAttribute("fill", e < THR ? "#ff2d2d" : "#30ff30");
      s.blinks.textContent = `Blinks: ${st.blinks}`;
    };

    if (api.instant) {
      st.samples = Array.from({ length: N }, (_, i) => (i > 50 ? 0.05 : (i === 16 || i === 17 || i === 34 || i === 35) ? 0.07 : 0.3 + Math.sin(i * 1.3) * 0.008));
      st.o = 0.06; st.blinks = 2;
      render();
      s.alert.style.opacity = "1"; s.frame.style.opacity = "1";
      api.step(3);
      api.poster();
    }

    let acc = 0;
    api.spawn(() => api.tick(Infinity, (elapsed) => {
      st.o += (st.target - st.o) * 0.3;
      if (elapsed - acc > 55) {
        acc = elapsed;
        st.samples.push(earOf(st.o) + (Math.random() - 0.5) * 0.01);
        st.samples.shift();
      }
      render();
    }));
    const blink = async () => { st.target = 0; await api.wait(140); st.target = 1; st.blinks += 1; await api.wait(260); };

    api.step(0);
    render();
    await api.wait(1000);
    api.step(1);
    await api.wait(600);
    await blink();
    await api.wait(900);
    api.step(2);
    await blink();
    await api.wait(1100);

    st.target = 0.04;                                   // eyes drift shut
    await api.wait(1500);
    api.step(3);
    s.alert.style.opacity = "1";
    const a1 = api.loop(s.alert, [{ opacity: 1 }, { opacity: 0.35 }], { duration: 380, direction: "alternate" });
    const a2 = api.loop(s.frame, [{ opacity: 0.15 }, { opacity: 1 }], { duration: 380, direction: "alternate" });
    await api.wait(1600);
    st.target = 1;
    await api.wait(500);
    api.unloop(a1); api.unloop(a2);
    s.alert.style.opacity = "0"; s.frame.style.opacity = "0";
    await api.wait(900);
  },
};
