/* Prostate cancer detection, shown as the desktop tool it is: a Tkinter
   window with the biopsy image on the left and the model panel on the
   right. The tissue is rendered once on a canvas to look like an H&E
   stain — eosin-pink stroma, glands lined with hematoxylin-purple
   nuclei, crowded Grade 3 glands and fused Grade 4 sheets. */

const COL = { g4: "#ff6b3d", g3: "#ffc23c", benign: "#36d39a" };
const VIEW = { x: 8, y: 26, w: 248, h: 214 };

let tissueURL = null;
function tissue() {
  if (tissueURL) return tissueURL;
  const W = 496, H = 428, c = document.createElement("canvas");
  c.width = W; c.height = H;
  const g = c.getContext("2d");
  let seed = 42;
  const R = () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; };

  // Eosin background with uneven staining
  g.fillStyle = "#f2d3e2"; g.fillRect(0, 0, W, H);
  for (let i = 0; i < 260; i++) {
    g.fillStyle = R() > 0.5 ? "rgba(236,186,210,0.35)" : "rgba(250,232,241,0.35)";
    g.beginPath(); g.ellipse(R() * W, R() * H, 10 + R() * 40, 6 + R() * 25, R() * 3, 0, Math.PI * 2); g.fill();
  }
  // Stroma fibres
  g.lineCap = "round";
  for (let i = 0; i < 1400; i++) {
    const x = R() * W, y = R() * H, a = R() * Math.PI, l = 6 + R() * 18;
    g.strokeStyle = `rgba(214,140,180,${0.25 + R() * 0.35})`;
    g.lineWidth = 0.6 + R() * 1.1;
    g.beginPath(); g.moveTo(x, y);
    g.quadraticCurveTo(x + Math.cos(a) * l * 0.5 + (R() - 0.5) * 4, y + Math.sin(a) * l * 0.5 + (R() - 0.5) * 4, x + Math.cos(a) * l, y + Math.sin(a) * l);
    g.stroke();
  }
  const nucleus = (x, y, ang, s = 1, alpha = 0.85) => {
    g.fillStyle = `rgba(${78 + R() * 30},${34 + R() * 20},${120 + R() * 30},${alpha})`;
    g.beginPath(); g.ellipse(x, y, (2.4 + R() * 1.4) * s, (1.4 + R() * 0.7) * s, ang, 0, Math.PI * 2); g.fill();
  };
  // A gland: irregular lumen, pink cytoplasm band, ring of nuclei
  const gland = (cx, cy, r, squash = 0.75) => {
    const pts = [], n = 22;
    for (let i = 0; i < n; i++) {
      const a = (i / n) * Math.PI * 2, rr = r * (0.82 + R() * 0.3);
      pts.push([cx + Math.cos(a) * rr, cy + Math.sin(a) * rr * squash]);
    }
    const poly = (scale, fill) => {
      g.fillStyle = fill; g.beginPath();
      pts.forEach(([x, y], i) => { const px = cx + (x - cx) * scale, py = cy + (y - cy) * scale; i ? g.lineTo(px, py) : g.moveTo(px, py); });
      g.closePath(); g.fill();
    };
    poly(1.18, "rgba(240,190,214,0.95)");
    poly(1.0, "rgba(252,244,248,1)");
    const m = Math.round(r * 1.7);
    for (let i = 0; i < m; i++) {
      const a = (i / m) * Math.PI * 2 + R() * 0.1;
      nucleus(cx + Math.cos(a) * r * 1.08, cy + Math.sin(a) * r * 1.08 * squash, a + Math.PI / 2);
    }
  };
  // Benign glands, large and regular
  [[70, 86, 34], [210, 60, 28], [440, 70, 32], [430, 250, 30], [300, 260, 22], [60, 400, 26], [240, 410, 30], [350, 352, 38], [470, 400, 24]]
    .forEach(([x, y, r]) => gland(x, y, r, 0.62 + R() * 0.25));
  // Grade 3: small, crowded, still separate
  for (let i = 0; i < 16; i++) gland(356 + (R() - 0.5) * 100, 144 + (R() - 0.5) * 80, 7 + R() * 6, 0.8);
  // Grade 4: fused sheet with small punched-out lumens, dense nuclei
  g.fillStyle = "rgba(228,160,196,0.95)";
  g.beginPath(); g.ellipse(156, 276, 74, 58, 0.3, 0, Math.PI * 2); g.fill();
  for (let i = 0; i < 520; i++) {
    const a = R() * Math.PI * 2, r = Math.sqrt(R());
    nucleus(156 + Math.cos(a) * r * 72, 276 + Math.sin(a) * r * 54, R() * 3, 1.05, 0.9);
  }
  for (let i = 0; i < 12; i++) {
    g.fillStyle = "rgba(252,244,248,0.95)";
    g.beginPath(); g.ellipse(120 + R() * 74, 246 + R() * 62, 3 + R() * 4, 2 + R() * 3, R() * 3, 0, Math.PI * 2); g.fill();
  }
  // Scattered stromal nuclei
  for (let i = 0; i < 420; i++) nucleus(R() * W, R() * H, R() * 3, 0.75, 0.7);
  tissueURL = c.toDataURL("image/jpeg", 0.86);
  return tissueURL;
}

export default {
  duration: 6700,
  rest: 1600,
  i18n: {
    en: {
      steps: [
        "A biopsy image is opened in the tool",
        "YOLOv5 looks at the whole tissue in one pass",
        "Suspicious regions are boxed and graded",
        "A Gleason score for the pathologist, in about 0.1 s",
      ],
      model: "MODEL", image: "IMAGE", detect: "Detect", results: "RESULTS", ready: "Ready", found: "3 regions · 0.10 s",
    },
    uz: {
      steps: [
        "Biopsiya tasviri dasturda ochiladi",
        "YOLOv5 to'qimani bir o'tishda to'liq ko'rib chiqadi",
        "Shubhali sohalar ramkaga olinib, darajasi aniqlanadi",
        "Patolog uchun Gleason bali — taxminan 0.1 s da",
      ],
      model: "MODEL", image: "TASVIR", detect: "Aniqlash", results: "NATIJA", ready: "Tayyor", found: "3 ta soha · 0.10 s",
    },
    ru: {
      steps: [
        "Снимок биопсии открывается в программе",
        "YOLOv5 просматривает всю ткань за один проход",
        "Подозрительные участки выделяются и получают степень",
        "Балл Глисона для патолога — примерно за 0,1 с",
      ],
      model: "МОДЕЛЬ", image: "СНИМОК", detect: "Найти", results: "РЕЗУЛЬТАТ", ready: "Готово", found: "3 участка · 0,10 с",
    },
  },

  build(svg, { h }, t) {
    const uid = "md" + Math.random().toString(36).slice(2, 8);
    const defs = h("defs", {}, svg);
    const clip = h("clipPath", { id: `${uid}c` }, defs);
    h("rect", { x: VIEW.x, y: VIEW.y, width: VIEW.w, height: VIEW.h, rx: 4 }, clip);
    const scanG = h("linearGradient", { id: `${uid}s`, x1: 0, x2: 1, y1: 0, y2: 0 }, defs);
    h("stop", { offset: 0, "stop-color": "#35d6dd", "stop-opacity": 0 }, scanG);
    h("stop", { offset: 0.9, "stop-color": "#35d6dd", "stop-opacity": 0.22 }, scanG);
    h("stop", { offset: 1, "stop-color": "#ffffff", "stop-opacity": 0.8 }, scanG);

    // ── Window chrome ──
    h("rect", { x: 0, y: 0, width: 400, height: 250, class: "d-card" }, svg);
    h("rect", { x: 0, y: 0, width: 400, height: 19, class: "d-card2" }, svg);
    h("rect", { x: 6, y: 5, width: 9, height: 9, rx: 2, fill: "#d1477a" }, svg);
    h("text", { x: 20, y: 13, "font-size": 8, class: "d-tx2", text: "Gleason Detector — biopsy_0412.png" }, svg);
    h("path", { d: "M352 10h7M369 6.5h6v6h-6zM385 6.5l6 6m0-6-6 6", class: "s-tx3", fill: "none", "stroke-width": 1 }, svg);
    h("line", { x1: 0, x2: 400, y1: 19, y2: 19, class: "d-line" }, svg);

    // ── Image viewer ──
    h("rect", { x: VIEW.x - 1, y: VIEW.y - 1, width: VIEW.w + 2, height: VIEW.h + 2, rx: 5, class: "d-card2" }, svg);
    const view = h("g", { "clip-path": `url(#${uid}c)` }, svg);
    const img = h("image", { href: tissue(), x: VIEW.x, y: VIEW.y, width: VIEW.w, height: VIEW.h, preserveAspectRatio: "xMidYMid slice", opacity: 0 }, view);
    const scan = h("rect", { x: VIEW.x - 60, y: VIEW.y, width: 60, height: VIEW.h, fill: `url(#${uid}s)`, opacity: 0 }, view);

    const box = (x, y, w, hh, color, label) => {
      const g = h("g", { opacity: 0 }, svg);
      h("rect", { x, y, width: w, height: hh, fill: "none", stroke: color, "stroke-width": 1.4 }, g);
      const tw = label.length * 5 + 6;
      h("rect", { x, y: y - 11, width: tw, height: 11, fill: color }, g);
      h("text", { x: x + 3, y: y - 2.6, "font-size": 8, fill: "#1a1a1a", class: "dm db", text: label }, g);
      return { g, x };
    };
    const boxes = [
      box(VIEW.x + 38, VIEW.y + 106, 76, 62, COL.g4, "G4 0.91"),
      box(VIEW.x + 150, VIEW.y + 46, 56, 50, COL.g3, "G3 0.87"),
      box(VIEW.x + 148, VIEW.y + 152, 54, 44, COL.benign, "benign 0.95"),
    ];

    // ── Model panel ──
    const X = 264;
    h("text", { x: X, y: 36, "font-size": 7, class: "d-tx3 dm", text: t.model }, svg);
    h("text", { x: X, y: 47, "font-size": 8.5, class: "d-tx dm", text: "YOLOv5s · best.pt" }, svg);
    h("text", { x: X, y: 62, "font-size": 7, class: "d-tx3 dm", text: t.image }, svg);
    h("text", { x: X, y: 73, "font-size": 8.5, class: "d-tx dm", text: "2048 × 1536" }, svg);
    const btn = h("g", {}, svg);
    h("rect", { x: X, y: 81, width: 128, height: 19, rx: 4, class: "d-acc" }, btn);
    h("text", { x: X + 64, y: 93.5, "font-size": 8.5, fill: "#fff", "text-anchor": "middle", class: "db", text: `▶ ${t.detect}` }, btn);
    h("rect", { x: X, y: 106, width: 128, height: 3, rx: 1.5, class: "d-card2" }, svg);
    const bar = h("rect", { x: X, y: 106, width: 128, height: 3, rx: 1.5, class: "d-tq o-l", style: "transform: scaleX(0)" }, svg);
    h("text", { x: X, y: 124, "font-size": 7, class: "d-tx3 dm", text: t.results }, svg);
    const rows = [["Grade 4", "0.91", COL.g4], ["Grade 3", "0.87", COL.g3], ["Benign", "0.95", COL.benign]].map(([n, c, col], i) => {
      const y = 138 + i * 15;
      const g = h("g", { opacity: 0 }, svg);
      h("rect", { x: X, y: y - 6.5, width: 7, height: 7, rx: 1.5, fill: col }, g);
      h("text", { x: X + 11, y, "font-size": 8.5, class: "d-tx", text: n }, g);
      h("text", { x: X + 128, y, "font-size": 8, class: "d-tx2 dm", "text-anchor": "end", text: c }, g);
      return g;
    });
    h("line", { x1: X, x2: X + 128, y1: 182, y2: 182, class: "d-line" }, svg);
    h("text", { x: X, y: 197, "font-size": 7, class: "d-tx3 dm", text: "GLEASON" }, svg);
    const score = h("text", { x: X, y: 220, "font-size": 18, class: "d-tx dd", opacity: 0, text: "3 + 4 = 7" }, svg);

    // Status bar
    h("line", { x1: 0, x2: 400, y1: 242, y2: 242, class: "d-line" }, svg);
    const status = h("text", { x: 264, y: 248.5, "font-size": 6.5, class: "d-tx3 dm", text: t.ready }, svg);

    return { img, scan, boxes, btn, bar, rows, score, status };
  },

  async play(api, s, t) {
    api.step(0);
    await api.tween(s.img, [{ opacity: 0 }, { opacity: 1 }], { dur: 700 });
    await api.wait(500);

    api.step(1);
    await api.tween(s.btn, [{ transform: "scale(1)" }, { transform: "scale(0.96)" }, { transform: "scale(1)" }], { dur: 220 });
    s.scan.style.opacity = "1";
    const shown = new Set();
    await Promise.all([
      api.tween(s.bar, [{ transform: "scaleX(0)" }, { transform: "scaleX(1)" }], { dur: 1700, ease: "linear" }),
      api.tick(1700, (p) => {
        const x = VIEW.x - 60 + p * (VIEW.w + 60);
        s.scan.setAttribute("x", x.toFixed(1));
        s.boxes.forEach((b, i) => {
          if (!shown.has(i) && x + 60 > b.x + 30) {
            shown.add(i);
            if (i === 0) api.step(2);
            api.tween(b.g, [{ opacity: 0 }, { opacity: 1 }], { dur: 200 }).catch(() => {});
          }
        });
      }, "inOut"),
    ]);
    s.boxes.forEach((b) => { b.g.style.opacity = "1"; });
    api.step(2);
    await api.tween(s.scan, [{ opacity: 1 }, { opacity: 0 }], { dur: 250 });
    s.status.textContent = t.found;
    for (const r of s.rows) await api.tween(r, [{ opacity: 0 }, { opacity: 1 }], { dur: 220 });

    api.step(3);
    await api.tween(s.score, [{ opacity: 0 }, { opacity: 1 }], { dur: 400 });
    api.poster();
    await api.wait(2400);
  },
};
