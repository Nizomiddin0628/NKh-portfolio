/* Prostate biopsy: a procedural H&E tissue tile. A detection pass sweeps
   across it, regions are boxed and graded on the Gleason scale, and the
   panel sums the score. Tissue keeps its stain colours in both themes. */

const GRADE = { g3: "#e39a2d", g4: "#ef5b2a", benign: "#2aa872" };

export default {
  duration: 8300,
  rest: 1400,
  i18n: {
    en: {
      steps: [
        "A biopsy image is loaded",
        "The model looks at the whole tissue in one pass",
        "Suspicious regions are boxed and graded",
        "A Gleason score for the doctor — in about 0.1 s",
      ],
      found: "Regions", time: "Inference",
    },
    uz: {
      steps: [
        "Biopsiya tasviri yuklanadi",
        "Model to'qimani bir o'tishda to'liq ko'rib chiqadi",
        "Shubhali sohalar ramkaga olinib, darajasi aniqlanadi",
        "Shifokor uchun Gleason bali — taxminan 0.1 s da",
      ],
      found: "Sohalar", time: "Inference",
    },
    ru: {
      steps: [
        "Загружается снимок биопсии",
        "Модель просматривает всю ткань за один проход",
        "Подозрительные участки выделяются и получают степень",
        "Балл Глисона для врача — примерно за 0,1 с",
      ],
      found: "Участки", time: "Inference",
    },
  },

  build(svg, { h, rng }) {
    const uid = "m" + Math.random().toString(36).slice(2, 8);
    const R = rng(11);
    const defs = h("defs", {}, svg);
    const clip = h("clipPath", { id: `${uid}c` }, defs);
    h("rect", { x: 12, y: 12, width: 246, height: 226, rx: 12 }, clip);
    const grad = h("linearGradient", { id: `${uid}g`, x1: 0, x2: 1, y1: 0, y2: 0 }, defs);
    h("stop", { offset: 0, "stop-color": "#35d6dd", "stop-opacity": 0 }, grad);
    h("stop", { offset: 0.85, "stop-color": "#35d6dd", "stop-opacity": 0.32 }, grad);
    h("stop", { offset: 1, "stop-color": "#ffffff", "stop-opacity": 0.9 }, grad);

    // ── Tissue tile ──
    const tile = h("g", { "clip-path": `url(#${uid}c)` }, svg);
    const tissue = h("g", { opacity: 0 }, tile);
    h("rect", { x: 12, y: 12, width: 246, height: 226, fill: "#f3d6e4" }, tissue);
    // Stroma fibres
    let fib = "";
    for (let i = 0; i < 70; i++) {
      const x = 12 + R() * 246, y = 12 + R() * 226, a = R() * Math.PI, l = 6 + R() * 12;
      fib += `M${x.toFixed(1)} ${y.toFixed(1)}l${(Math.cos(a) * l).toFixed(1)} ${(Math.sin(a) * l).toFixed(1)}`;
    }
    h("path", { d: fib, stroke: "#e2a9c4", "stroke-width": 2.2, "stroke-linecap": "round", fill: "none" }, tissue);

    // Glands: lumen + a ring of nuclei
    let nuclei = "";
    const dot = (x, y) => { nuclei += `M${x.toFixed(1)} ${y.toFixed(1)}h0`; };
    const gland = (cx, cy, rx, ry) => {
      h("ellipse", { cx, cy, rx, ry, fill: "#fcf1f6", stroke: "#d898b8", "stroke-width": 1.2 }, tissue);
      const n = Math.round((rx + ry) * 0.55);
      for (let i = 0; i < n; i++) {
        const a = (i / n) * Math.PI * 2;
        dot(cx + Math.cos(a) * (rx + 2.2), cy + Math.sin(a) * (ry + 2.2));
      }
    };
    // Benign, regular glands spread over the tile
    [[40, 48, 20, 13], [112, 34, 17, 11], [232, 40, 16, 22], [230, 128, 19, 14], [150, 132, 15, 10],
     [36, 216, 15, 11], [120, 222, 18, 10], [176, 186, 22, 15], [236, 206, 13, 17]]
      .forEach((g) => gland(...g));
    // Grade 3: small, separate, crowded glands
    for (let i = 0; i < 9; i++) {
      gland(176 + (R() - 0.5) * 48, 78 + (R() - 0.5) * 42, 4 + R() * 4, 3 + R() * 3);
    }
    // Grade 4: fused glands, dense sheets of nuclei
    for (let i = 0; i < 95; i++) {
      const a = R() * Math.PI * 2, r = Math.sqrt(R()) * 34;
      dot(78 + Math.cos(a) * r * 1.15, 150 + Math.sin(a) * r);
    }
    for (let i = 0; i < 4; i++) {
      h("ellipse", { cx: 66 + R() * 26, cy: 138 + R() * 24, rx: 3 + R() * 3, ry: 2 + R() * 2, fill: "#fcf1f6" }, tissue);
    }
    // Scattered stromal nuclei
    for (let i = 0; i < 70; i++) dot(12 + R() * 246, 12 + R() * 226);
    h("path", { d: nuclei, stroke: "#6d3f93", "stroke-width": 3.4, "stroke-linecap": "round", fill: "none", opacity: 0.85 }, tissue);

    const scan = h("rect", { x: -70, y: 12, width: 70, height: 226, fill: `url(#${uid}g)`, opacity: 0 }, tile);
    h("rect", { x: 12.5, y: 12.5, width: 245, height: 225, rx: 12, fill: "none", class: "s-line", "stroke-width": 1 }, svg);

    // Detection boxes (tile coordinates)
    const box = (x, y, w, hh, color, label) => {
      const g = h("g", { opacity: 0 }, svg);
      h("rect", { x, y, width: w, height: hh, rx: 3, fill: color, "fill-opacity": 0.1, stroke: color, "stroke-width": 2 }, g);
      const tw = label.length * 6.3 + 10;
      h("rect", { x, y: y - 15, width: tw, height: 15, rx: 3, fill: color }, g);
      h("text", { x: x + 5, y: y - 4, "font-size": 10.5, fill: "#fff", class: "dm db", text: label }, g);
      return { g, x };
    };
    const boxes = [
      box(36, 112, 86, 76, GRADE.g4, "G4 0.91"),
      box(148, 52, 58, 52, GRADE.g3, "G3 0.87"),
      box(150, 166, 54, 42, GRADE.benign, "Benign 0.95"),
    ];

    // ── Result panel ──
    const P = 270;
    h("rect", { x: P, y: 12, width: 118, height: 226, rx: 12, class: "d-card" }, svg);
    h("text", { x: P + 12, y: 32, "font-size": 10, class: "d-tx3 dm", text: "YOLOv5" }, svg);
    const timer = h("text", { x: P + 12, y: 58, "font-size": 21, class: "d-tx dd", text: "0.00" }, svg);
    h("text", { x: P + 76, y: 58, "font-size": 11, class: "d-tx3 dm", text: "s" }, svg);
    h("line", { x1: P + 12, x2: P + 106, y1: 72, y2: 72, class: "d-line" }, svg);

    const rows = [["Grade 4", "0.91", GRADE.g4], ["Grade 3", "0.87", GRADE.g3], ["Benign", "0.95", GRADE.benign]].map(([name, conf, color], i) => {
      const y = 92 + i * 24;
      const g = h("g", { opacity: 0 }, svg);
      h("rect", { x: P + 12, y: y - 8, width: 8, height: 8, rx: 2, fill: color }, g);
      h("text", { x: P + 26, y, "font-size": 11.5, class: "d-tx", text: name }, g);
      h("text", { x: P + 106, y, "font-size": 10.5, class: "d-tx2 dm", "text-anchor": "end", text: conf }, g);
      const bar = h("rect", { x: P + 26, y: y + 5, width: 80 * Number(conf), height: 2.5, rx: 1.25, fill: color, class: "o-l", style: "transform: scaleX(0)" }, g);
      return { g, bar };
    });

    h("line", { x1: P + 12, x2: P + 106, y1: 172, y2: 172, class: "d-line" }, svg);
    h("text", { x: P + 12, y: 192, "font-size": 10, class: "d-tx3 dm", text: "GLEASON" }, svg);
    const score = h("text", { x: P + 12, y: 222, "font-size": 21, class: "d-tx dd", opacity: 0, text: "3+4 = 7" }, svg);

    return { tissue, scan, boxes, timer, rows, score };
  },

  async play(api, s) {
    api.step(0);
    await api.tween(s.tissue, [{ opacity: 0, transform: "scale(1.06)" }, { opacity: 1, transform: "scale(1)" }], { dur: 900 });
    await api.wait(300);

    api.step(1);
    s.scan.style.opacity = "1";
    const shown = new Set();
    await Promise.all([
      api.count(s.timer, 0, 0.1, 1900, (v) => v.toFixed(2)),
      api.tick(1900, (p) => {
        const x = -70 + p * 340;
        s.scan.setAttribute("x", x.toFixed(1));
        s.boxes.forEach((b, i) => {
          if (!shown.has(i) && x + 70 > b.x + 30) {
            shown.add(i);
            api.tween(b.g, [{ opacity: 0, transform: "scale(1.15)" }, { opacity: 1, transform: "scale(1)" }], { dur: 380 })
              .catch(() => {});
          }
        });
      }, "inOut"),
    ]);
    s.boxes.forEach((b) => { b.g.style.opacity = "1"; b.g.style.transform = "none"; });
    await api.hide(s.scan, 300);

    api.step(2);
    for (const r of s.rows) {
      api.show(r.g, 380, "translateX(-6px)");
      await api.tween(r.bar, [{ transform: "scaleX(0)" }, { transform: "scaleX(1)" }], { dur: 520 });
    }

    api.step(3);
    await api.show(s.score, 500, "translateY(8px)");
    api.poster();
    await api.wait(2400);
    await Promise.all(s.boxes.map((b) => api.hide(b.g, 400)));
  },
};
