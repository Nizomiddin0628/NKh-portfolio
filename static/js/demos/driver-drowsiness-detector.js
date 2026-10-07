/* Drowsiness: a face mesh in a webcam frame. Eye Aspect Ratio is plotted
   live; two normal blinks pass without a word, a long closure crosses the
   threshold, the alarm fires, the eyes open again. */

const C = {
  bg: "#0a111f", mesh: "#35d6dd", dim: "#2a3956", face: "#3a4a6c", red: "#ff5d62", ok: "#3fcf8e",
};
const THR = 0.21;
const N = 64;               // samples on the graph
const GX = 242, GW = 136, GY = 76, GH = 76;

export default {
  duration: 8800,
  rest: 1200,
  i18n: {
    en: {
      steps: [
        "MediaPipe tracks 468 landmarks on the face",
        "Eye Aspect Ratio is computed on every frame",
        "A normal blink is ignored",
        "Eyes closed too long — the alarm goes off",
      ],
      open: "Eyes open", blink: "Blink — ignored", closed: "Closed", alert: "WAKE UP", s: "s",
    },
    uz: {
      steps: [
        "MediaPipe yuzdagi 468 ta nuqtani kuzatadi",
        "Har kadrda Eye Aspect Ratio hisoblanadi",
        "Oddiy ko'z qirpish e'tiborga olinmaydi",
        "Ko'z uzoq yumilib qolsa — signal chalinadi",
      ],
      open: "Ko'zlar ochiq", blink: "Qirpish — o'tkazildi", closed: "Yumuq", alert: "DIQQAT", s: "s",
    },
    ru: {
      steps: [
        "MediaPipe отслеживает 468 точек лица",
        "Eye Aspect Ratio считается на каждом кадре",
        "Обычное моргание игнорируется",
        "Глаза закрыты слишком долго — срабатывает сигнал",
      ],
      open: "Глаза открыты", blink: "Моргание — пропуск", closed: "Закрыты", alert: "ВНИМАНИЕ", s: "с",
    },
  },

  build(svg, { h }, t) {
    // ── Webcam frame ──
    h("rect", { x: 12, y: 12, width: 210, height: 226, rx: 12, fill: C.bg }, svg);
    const frame = h("rect", { x: 12.5, y: 12.5, width: 209, height: 225, rx: 12, fill: "none", stroke: C.red, "stroke-width": 3, opacity: 0 }, svg);
    h("text", { x: 24, y: 30, "font-size": 9.5, fill: "#7f90b6", class: "dm", text: "CAM · 30 fps" }, svg);

    // Head and mesh
    const cx = 117, cy = 128;
    h("ellipse", { cx, cy, rx: 62, ry: 80, fill: "none", stroke: C.face, "stroke-width": 1.5 }, svg);
    let mesh = "", lines = "";
    const pts = [];
    for (let i = 0; i <= 26; i++) {           // jaw and forehead contour
      const a = Math.PI * (0.05 + (i / 26) * 1.9) + Math.PI / 2;
      pts.push([cx + Math.cos(a) * 58, cy + Math.sin(a) * 75]);
    }
    pts.forEach(([x, y], i) => {
      mesh += `M${x.toFixed(1)} ${y.toFixed(1)}h0`;
      if (i) lines += `L${x.toFixed(1)} ${y.toFixed(1)}`; else lines += `M${x.toFixed(1)} ${y.toFixed(1)}`;
    });
    // brows, nose, lips
    const extra = [[78, 92], [88, 88], [100, 89], [133, 89], [146, 88], [156, 92],
      [117, 108], [117, 122], [117, 136], [108, 142], [126, 142],
      [98, 168], [108, 164], [117, 166], [126, 164], [136, 168], [117, 174], [106, 172], [128, 172]];
    extra.forEach(([x, y]) => { mesh += `M${x} ${y}h0`; });
    lines += "M78 92L88 88L100 89M133 89L146 88L156 92M117 108L117 136L108 142M117 136L126 142";
    lines += "M98 168L108 164L117 166L126 164L136 168L128 172L117 174L106 172Z";
    h("path", { d: lines, fill: "none", stroke: C.mesh, "stroke-width": 0.8, opacity: 0.35 }, svg);
    h("path", { d: mesh, stroke: C.mesh, "stroke-width": 3, "stroke-linecap": "round", opacity: 0.8 }, svg);

    // Eyes: 6 landmarks each
    const eye = (ex) => {
      const g = h("g", {}, svg);
      const shape = h("path", { fill: "rgba(53,214,221,0.08)", stroke: C.mesh, "stroke-width": 1.3 }, g);
      const iris = h("ellipse", { cx: ex, cy: 112, rx: 6, ry: 6, fill: "#9fb4ff", opacity: 0.85 }, g);
      const dots = h("path", { stroke: "#ffffff", "stroke-width": 3.2, "stroke-linecap": "round" }, g);
      const ruler = h("path", { stroke: "#e2c48b", "stroke-width": 1, "stroke-dasharray": "2 2", fill: "none" }, g);
      return { ex, shape, iris, dots, ruler };
    };
    const eyes = [eye(93), eye(141)];

    // ── EAR panel ──
    h("rect", { x: 232, y: 12, width: 156, height: 226, rx: 12, class: "d-card" }, svg);
    h("text", { x: 244, y: 32, "font-size": 10, class: "d-tx3 dm", text: "EYE ASPECT RATIO" }, svg);
    const val = h("text", { x: 244, y: 60, "font-size": 22, class: "d-tx dd", text: "0.31" }, svg);
    h("rect", { x: GX, y: GY, width: GW, height: GH, rx: 6, class: "d-card2" }, svg);
    const thrY = GY + GH - (THR / 0.4) * GH;
    h("line", { x1: GX, x2: GX + GW, y1: thrY, y2: thrY, class: "s-bad", "stroke-width": 1, "stroke-dasharray": "4 3" }, svg);
    h("text", { x: GX + GW - 4, y: thrY - 4, "font-size": 9, class: "d-bad dm", "text-anchor": "end", text: "0.21" }, svg);
    const graph = h("polyline", { fill: "none", class: "s-tq", "stroke-width": 1.8, "stroke-linejoin": "round", points: "" }, svg);

    const statusDot = h("circle", { cx: 248, cy: 176, r: 4, class: "d-ok" }, svg);
    const status = h("text", { x: 258, y: 180, "font-size": 11, class: "d-tx", text: t.open }, svg);

    const alert = h("g", { opacity: 0 }, svg);
    h("rect", { x: 242, y: 196, width: 136, height: 30, rx: 8, class: "d-bad" }, alert);
    h("path", { d: "M254 207h4l5-4v14l-5-4h-4z", fill: "#fff" }, alert);
    const waves = h("path", { d: "M267 206q3 4 0 8M271 203q5 7 0 14", stroke: "#fff", "stroke-width": 1.4, fill: "none", "stroke-linecap": "round" }, alert);
    h("text", { x: 282, y: 215.5, "font-size": 12, fill: "#fff", class: "dd", text: t.alert }, alert);

    return { frame, eyes, val, graph, statusDot, status, alert, waves };
  },

  async play(api, s, t) {
    const st = { o: 1, target: 1, samples: Array(N).fill(0.31), closedFor: 0, alert: false };
    const ear = (o) => 0.02 + 0.29 * o;

    const drawEye = (e, o) => {
      const x1 = e.ex - 18, x4 = e.ex + 18, y = 112;
      const up = 9.5 * o + 0.6, dn = 6 * o + 0.6;
      const p = [[x1, y], [e.ex - 7, y - up], [e.ex + 7, y - up], [x4, y], [e.ex + 7, y + dn], [e.ex - 7, y + dn]];
      e.shape.setAttribute("d", `M${p[0]}Q${e.ex - 11} ${y - up * 1.2} ${p[1]}L${p[2]}Q${e.ex + 11} ${y - up * 1.2} ${p[3]}Q${e.ex + 11} ${y + dn * 1.2} ${p[4]}L${p[5]}Q${e.ex - 11} ${y + dn * 1.2} ${p[0]}Z`);
      e.dots.setAttribute("d", p.map(([a, b]) => `M${a} ${b}h0`).join(""));
      e.ruler.setAttribute("d", `M${p[1][0]} ${p[1][1]}V${p[5][1]}M${p[2][0]} ${p[2][1]}V${p[4][1]}`);
      e.iris.setAttribute("ry", Math.max(0.1, 6 * Math.min(1, o * 1.15)).toFixed(2));
      e.iris.setAttribute("opacity", o < 0.15 ? 0 : 0.85);
    };
    const render = () => {
      s.eyes.forEach((e) => drawEye(e, st.o));
      const pts = st.samples.map((v, i) => `${(GX + (i / (N - 1)) * GW).toFixed(1)},${(GY + GH - (v / 0.4) * GH).toFixed(1)}`);
      s.graph.setAttribute("points", pts.join(" "));
      s.val.textContent = ear(st.o).toFixed(2);
      s.val.setAttribute("class", ear(st.o) < THR ? "d-bad dd" : "d-tx dd");
    };
    const setStatus = (text, cls) => { s.status.textContent = text; s.statusDot.setAttribute("class", cls); };

    if (api.instant) {
      // Poster: the moment the alarm fires
      const hist = [];
      for (let i = 0; i < N; i++) {
        const blink = i === 14 || i === 15 || i === 30 || i === 31;
        hist.push(i > 44 ? 0.05 : blink ? 0.07 : 0.3 + Math.sin(i) * 0.01);
      }
      st.samples = hist; st.o = 0.08; render();
      setStatus(`${t.closed} 1.6 ${t.s}`, "d-bad");
      s.alert.style.opacity = "1"; s.frame.style.opacity = "1";
      api.step(3);
      api.poster();
    }

    // Simulation: eyes chase their target, a sample every 60 ms
    let acc = 0;
    api.spawn(() => api.tick(Infinity, (elapsed) => {
      const k = 0.28;
      st.o += (st.target - st.o) * k;
      if (elapsed - acc > 60) {
        acc = elapsed;
        st.samples.push(ear(st.o) + (Math.random() - 0.5) * 0.008);
        st.samples.shift();
      }
      render();
    }));

    const blink = async () => { st.target = 0; await api.wait(150); st.target = 1; await api.wait(260); };

    api.step(0);
    render();
    await api.wait(900);
    api.step(1);
    await api.wait(700);
    await blink();
    await api.wait(900);
    api.step(2);
    setStatus(t.blink, "d-tx3");
    await blink();
    await api.wait(700);
    setStatus(t.open, "d-ok");
    await api.wait(500);

    // Drowsy: eyes drift shut
    st.target = 0.05;
    await api.wait(300);
    for (let i = 0; i < 16; i++) {
      await api.wait(100);
      const sec = ((i + 1) / 10).toFixed(1);
      setStatus(`${t.closed} ${sec} ${t.s}`, "d-bad");
    }
    api.step(3);
    await api.show(s.alert, 260, "scale(0.92)");
    const flash = api.loop(s.frame, [{ opacity: 0.2 }, { opacity: 1 }], { duration: 420, direction: "alternate" });
    api.loop(s.waves, [{ opacity: 1 }, { opacity: 0.2 }], { duration: 380, direction: "alternate" });
    await api.wait(1500);
    st.target = 1;
    await api.wait(500);
    api.unloop(flash);
    s.frame.style.opacity = "0";
    await api.hide(s.alert, 300);
    setStatus(t.open, "d-ok");
    await api.wait(900);
  },
};
