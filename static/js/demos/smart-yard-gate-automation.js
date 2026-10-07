/* Smart Yard as the camera sees it: a gate camera looking down the
   entry lane. A tractor approaches in perspective, the detector tracks
   it, OCR reads plate / USDOT / unit from two cameras, FMCSA confirms the
   carrier, the barrier lifts and the truck rolls past the camera.
   CCTV look: muted daylight palette, sensor grain, vignette, burned-in
   timestamp. The palette ignores the site theme on purpose. */

const VP = { x: 170, y: 84 };          // vanishing point of the lane
const STOP_Y = 200;                      // where the bumper stops, ground line
const S_STOP = 0.86;
const BOX = "#39e58c";

let grain = null;                        // three noise frames, made once
function grainFrames() {
  if (grain) return grain;
  grain = [];
  for (let f = 0; f < 3; f++) {
    const c = document.createElement("canvas");
    c.width = 200; c.height = 125;
    const ctx = c.getContext("2d");
    const img = ctx.createImageData(200, 125);
    for (let i = 0; i < img.data.length; i += 4) {
      const v = Math.random() * 255;
      img.data[i] = img.data[i + 1] = img.data[i + 2] = v;
      img.data[i + 3] = 255;
    }
    ctx.putImageData(img, 0, 0);
    grain.push(c.toDataURL("image/png"));
  }
  return grain;
}

const sAt = (y) => ((y - VP.y) / (STOP_Y - VP.y)) * S_STOP;

export default {
  duration: 10300,
  rest: 1200,
  i18n: {
    en: {
      steps: [
        "A truck approaches the gate — seven cameras watch the yard",
        "YOLO detects and tracks the vehicle",
        "OCR reads plate, USDOT and unit number from two cameras",
        "The carrier is checked against FMCSA",
        "The barrier lifts and the event is logged",
      ],
      entry: "YARD ENTRY", active: "ACTIVE", open: "GATE OPEN", wait: "WAITING",
    },
    uz: {
      steps: [
        "Yuk mashinasi darvozaga yaqinlashadi — hovlini 7 ta kamera kuzatadi",
        "YOLO transportni aniqlaydi va kuzatib boradi",
        "OCR ikki kameradan davlat raqami, USDOT va unit raqamini o'qiydi",
        "Tashuvchi FMCSA reyestrida tekshiriladi",
        "To'siq ko'tariladi, hodisa jurnalga yoziladi",
      ],
      entry: "KIRISH", active: "FAOL", open: "DARVOZA OCHIQ", wait: "KUTILMOQDA",
    },
    ru: {
      steps: [
        "Тягач подъезжает к воротам — двор видят семь камер",
        "YOLO находит и ведёт транспорт",
        "OCR читает номер, USDOT и юнит с двух камер",
        "Перевозчик проверяется по FMCSA",
        "Шлагбаум поднимается, событие пишется в журнал",
      ],
      entry: "ВЪЕЗД", active: "АКТИВЕН", open: "ВОРОТА ОТКРЫТЫ", wait: "ОЖИДАНИЕ",
    },
  },

  build(svg, { h }, t) {
    const uid = "sy" + Math.random().toString(36).slice(2, 8);
    const defs = h("defs", {}, svg);
    const grad = (id, stops, vertical = true) => {
      const g = h("linearGradient", { id: `${uid}${id}`, x1: 0, y1: 0, x2: vertical ? 0 : 1, y2: vertical ? 1 : 0 }, defs);
      stops.forEach(([o, c, a = 1]) => h("stop", { offset: o, "stop-color": c, "stop-opacity": a }, g));
      return `url(#${uid}${id})`;
    };
    const sky = grad("sky", [[0, "#9aa9b8"], [1, "#cfd6dc"]]);
    const asphalt = grad("asp", [[0, "#6a6f75"], [1, "#3b4046"]]);
    const body = grad("body", [[0, "#36588f"], [0.55, "#2a4677"], [1, "#1f3458"]]);
    const glass = grad("glass", [[0, "#7f91a5"], [0.5, "#3b4a5c"], [1, "#222c38"]]);
    const chrome = grad("chrome", [[0, "#e3e6ea"], [0.5, "#9aa1aa"], [1, "#d5d9de"]]);
    const vig = h("radialGradient", { id: `${uid}vig`, cx: 0.5, cy: 0.5, r: 0.75 }, defs);
    h("stop", { offset: 0.55, "stop-color": "#000", "stop-opacity": 0 }, vig);
    h("stop", { offset: 1, "stop-color": "#000", "stop-opacity": 0.55 }, vig);
    const glow = h("radialGradient", { id: `${uid}glow` }, defs);
    h("stop", { offset: 0, "stop-color": "#fff6d8", "stop-opacity": 0.9 }, glow);
    h("stop", { offset: 1, "stop-color": "#fff6d8", "stop-opacity": 0 }, glow);

    // ── Scene ──
    h("rect", { x: 0, y: 0, width: 400, height: 92, fill: sky }, svg);
    // warehouse and parked trailers on the horizon
    h("rect", { x: 210, y: 58, width: 190, height: 30, fill: "#7a8189" }, svg);
    h("rect", { x: 210, y: 55, width: 190, height: 4, fill: "#6b7178" }, svg);
    for (let x = 222; x < 396; x += 26) h("rect", { x, y: 70, width: 16, height: 18, fill: "#5d636a" }, svg);
    for (let i = 0; i < 6; i++) h("rect", { x: 10 + i * 24, y: 76, width: 21, height: 12, fill: i % 2 ? "#c9cdd1" : "#b3b9bf" }, svg);
    h("rect", { x: 0, y: 84, width: 400, height: 166, fill: asphalt }, svg);
    // lane edges and the dashed centre line, all toward the vanishing point
    h("path", { d: `M${VP.x - 6} ${VP.y} L-30 250 M${VP.x + 6} ${VP.y} L380 250`, stroke: "#d9dde0", "stroke-width": 1.4, opacity: 0.55, fill: "none" }, svg);
    let dash = "";
    for (let k = 0; k < 9; k++) {
      const y0 = VP.y + Math.pow(k / 9, 2) * 170, y1 = VP.y + Math.pow((k + 0.45) / 9, 2) * 170;
      dash += `M${VP.x + (y0 - VP.y) * 0.18} ${y0} L${VP.x + (y1 - VP.y) * 0.18} ${y1}`;
    }
    h("path", { d: dash, stroke: "#e8d98a", "stroke-width": 1.6, opacity: 0.6, fill: "none" }, svg);
    // stop line
    h("path", { d: "M18 214 L330 214", stroke: "#e9ecef", "stroke-width": 3, opacity: 0.55 }, svg);
    // fence on the left, light pole on the right
    for (let i = 0; i < 7; i++) {
      const y = 92 + i * i * 3.2, x = 90 - i * i * 2.2;
      h("line", { x1: x, y1: y - 26 - i * 4, x2: x, y2: y, stroke: "#4f565e", "stroke-width": 1 + i * 0.25 }, svg);
    }
    h("path", { d: "M90 66 L-10 20 M90 79 L-10 70", stroke: "#4f565e", "stroke-width": 0.8, fill: "none" }, svg);
    h("rect", { x: 352, y: 20, width: 4, height: 120, fill: "#4c535b" }, svg);
    h("rect", { x: 340, y: 18, width: 22, height: 5, rx: 2, fill: "#5a6169" }, svg);

    // ── Truck, front view, origin at the bottom centre ──
    const truck = h("g", { class: "vb", style: `transform: translate(${VP.x}px, ${VP.y + 8}px) scale(0.1)` }, svg);
    h("ellipse", { cx: 0, cy: 0, rx: 84, ry: 7, fill: "#000", opacity: 0.35 }, truck);
    h("rect", { x: -72, y: -28, width: 24, height: 28, rx: 5, fill: "#16191d" }, truck);
    h("rect", { x: 48, y: -28, width: 24, height: 28, rx: 5, fill: "#16191d" }, truck);
    h("path", { d: "M-63 -30 V-116 Q-63 -132 -48 -134 H48 Q63 -132 63 -116 V-30 Z", fill: body }, truck);
    h("path", { d: "M-53 -127 H53 L57 -100 H-57 Z", fill: glass }, truck);
    h("path", { d: "M-44 -126 L-30 -126 L-47 -101 L-56 -101 Z", fill: "#fff", opacity: 0.12 }, truck);
    h("line", { x1: 0, y1: -127, x2: 0, y2: -100, stroke: "#1b2430", "stroke-width": 2 }, truck);
    h("rect", { x: -56, y: -138, width: 112, height: 6, rx: 2, fill: "#1f3458" }, truck);
    for (let i = -2; i <= 2; i++) h("circle", { cx: i * 13, cy: -135, r: 2, fill: "#ffb13b" }, truck);
    h("rect", { x: -31, y: -94, width: 62, height: 62, rx: 3, fill: "#5b636d" }, truck);
    h("rect", { x: -28, y: -91, width: 56, height: 56, rx: 2, fill: chrome }, truck);
    for (let y = -86; y < -36; y += 5.5) h("line", { x1: -26, x2: 26, y1: y, y2: y, stroke: "#6e767f", "stroke-width": 1.6 }, truck);
    h("text", { x: 0, y: -103, "font-size": 9, fill: "#eef2f8", "text-anchor": "middle", class: "dm db", text: "1182" }, truck);
    [-1, 1].forEach((side) => {
      h("rect", { x: side < 0 ? -60 : 34, y: -62, width: 26, height: 12, rx: 2, fill: "#eceadf" }, truck);
      h("circle", { cx: side * 47, cy: -56, r: 18, fill: `url(#${uid}glow)`, opacity: 0.55 }, truck);
      h("line", { x1: side * 63, y1: -112, x2: side * 80, y2: -114, stroke: "#2a2f36", "stroke-width": 2 }, truck);
      h("rect", { x: side < 0 ? -90 : 80, y: -128, width: 10, height: 24, rx: 2, fill: "#2a2f36" }, truck);
    });
    h("rect", { x: -72, y: -32, width: 144, height: 14, rx: 3, fill: chrome }, truck);
    h("rect", { x: -15, y: -29, width: 30, height: 10, rx: 1.5, fill: "#f3f4f1", stroke: "#4a4f55", "stroke-width": 0.8 }, truck);
    h("text", { x: 0, y: -21.5, "font-size": 6, fill: "#1d2a50", "text-anchor": "middle", class: "dm db", text: "4KL2290" }, truck);

    // ── Barrier (in front of the truck) ──
    h("rect", { x: 300, y: 150, width: 12, height: 68, rx: 2, fill: "#3c434b" }, svg);
    h("rect", { x: 296, y: 214, width: 20, height: 6, rx: 1, fill: "#2c3238" }, svg);
    const light = h("circle", { cx: 306, cy: 160, r: 3.4, fill: "#ff4d4f" }, svg);
    const arm = h("g", { class: "vb", style: "transform-origin: 304px 168px; transform: rotate(0deg)" }, svg);
    h("rect", { x: 22, y: 164, width: 284, height: 8, rx: 4, fill: "#f2f3f4" }, arm);
    for (let x = 30; x < 296; x += 28) h("rect", { x, y: 164, width: 14, height: 8, fill: "#d8343a" }, arm);

    // ── CCTV grain and vignette ──
    const frames = grainFrames();
    const noise = h("image", { href: frames[0], x: 0, y: 0, width: 400, height: 250, preserveAspectRatio: "none", opacity: 0.09, style: "mix-blend-mode: overlay" }, svg);
    h("rect", { x: 0, y: 0, width: 400, height: 250, fill: `url(#${uid}vig)` }, svg);

    // ── AI overlay ──
    const det = h("g", { opacity: 0 }, svg);
    const detRect = h("rect", { fill: "none", stroke: BOX, "stroke-width": 1.5 }, det);
    const detTag = h("rect", { height: 13, fill: BOX }, det);
    const detText = h("text", { "font-size": 8.5, fill: "#062b16", class: "dm db" }, det);
    const plate = h("g", { opacity: 0 }, svg);
    const plateRect = h("rect", { fill: "none", stroke: "#ffd166", "stroke-width": 1.3 }, plate);

    // Read-out panel (top right, like the ANPR software's side panel)
    const panel = h("g", { opacity: 0 }, svg);
    h("rect", { x: 244, y: 30, width: 148, height: 98, rx: 6, fill: "rgba(8,12,20,0.78)", stroke: "rgba(255,255,255,0.12)" }, panel);
    const rows = [["PLATE", "TX 4KL2290", "CAM-03"], ["USDOT", "3412875", "CAM-05"], ["UNIT", "1182", "CAM-05"], ["FMCSA", "", ""]].map(([k, , cam], i) => {
      const y = 48 + i * 17;
      h("text", { x: 252, y, "font-size": 7.5, fill: "#7d8aa3", class: "dm", text: k }, panel);
      const v = h("text", { x: 286, y, "font-size": 9.5, fill: "#eef2f8", class: "dm db" }, panel);
      const c = h("text", { x: 386, y, "font-size": 6.5, fill: "#5d6b86", class: "dm", "text-anchor": "end", text: cam }, panel);
      return { v, c };
    });
    const gate = h("text", { x: 252, y: 120, "font-size": 9, fill: "#ffb84d", class: "dm db", text: `● ${t.wait}` }, panel);

    // HUD burned into the image
    const hud = { fill: "#f4f6f8", style: "paint-order: stroke; stroke: rgba(0,0,0,0.55); stroke-width: 2px" };
    h("text", { x: 10, y: 16, "font-size": 8.5, class: "dm db", text: `CAM-03 · ${t.entry}`, ...hud }, svg);
    const clock = h("text", { x: 10, y: 27, "font-size": 7.5, class: "dm", text: "2026-10-07 08:42:17", ...hud }, svg);
    h("text", { x: 10, y: 243, "font-size": 7, class: "dm", text: "1920×1080 · 25 fps · YOLOv11", ...hud }, svg);
    const rec = h("circle", { cx: 386, cy: 13, r: 3.2, fill: "#ff4d4f" }, svg);
    h("text", { x: 379, y: 16, "font-size": 7.5, class: "dm db", "text-anchor": "end", text: "REC", ...hud }, svg);

    return { truck, det, detRect, detTag, detText, plate, plateRect, panel, rows, gate, arm, light, noise, frames, clock, rec };
  },

  async play(api, s, t) {
    let conf = 0.6;
    const place = (y) => {
      const sc = Math.max(0.05, sAt(y));
      const x = VP.x;
      s.truck.style.transform = `translate(${x}px, ${y.toFixed(1)}px) scale(${sc.toFixed(4)})`;
      const bx = x - 92 * sc, by = y - 142 * sc, bw = 184 * sc, bh = 148 * sc;
      s.detRect.setAttribute("x", bx.toFixed(1)); s.detRect.setAttribute("y", by.toFixed(1));
      s.detRect.setAttribute("width", bw.toFixed(1)); s.detRect.setAttribute("height", bh.toFixed(1));
      s.detTag.setAttribute("x", bx.toFixed(1)); s.detTag.setAttribute("y", (by - 13).toFixed(1));
      s.detTag.setAttribute("width", "86");
      s.detText.setAttribute("x", (bx + 4).toFixed(1)); s.detText.setAttribute("y", (by - 3.5).toFixed(1));
      s.detText.textContent = `truck ${conf.toFixed(2)} #418`;
      s.plateRect.setAttribute("x", (x - 17 * sc).toFixed(1)); s.plateRect.setAttribute("y", (y - 31 * sc).toFixed(1));
      s.plateRect.setAttribute("width", (34 * sc).toFixed(1)); s.plateRect.setAttribute("height", (14 * sc).toFixed(1));
    };

    if (api.instant) {
      conf = 0.97;
      place(STOP_Y);
      s.det.style.opacity = "1"; s.plate.style.opacity = "1"; s.panel.style.opacity = "1";
      ["TX 4KL2290", "3412875", "1182", `${t.active} ✓`].forEach((v, i) => { s.rows[i].v.textContent = v; });
      s.rows[3].v.setAttribute("fill", BOX);
      api.step(3);
      api.poster();
    }

    // Ambient: sensor grain, ticking clock, blinking REC
    api.spawn(async () => {
      let f = 0;
      for (;;) { await api.wait(90); f = (f + 1) % s.frames.length; s.noise.setAttribute("href", s.frames[f]); }
    });
    let sec = 17;
    api.spawn(async () => {
      for (;;) { await api.wait(1000); sec += 1; s.clock.textContent = `2026-10-07 08:42:${String(sec).padStart(2, "0")}`; }
    });
    api.loop(s.rec, [{ opacity: 1 }, { opacity: 0.25 }], { duration: 900, direction: "alternate" });

    // 1. Approach: steady speed, braking at the end
    api.step(0);
    place(VP.y + 8);
    let shown = false;
    await api.tick(3000, (p) => {
      const e = 1 - Math.pow(1 - p, 2.2);
      const y = VP.y + 8 + (STOP_Y - VP.y - 8) * e;
      conf = Math.min(0.97, 0.55 + p * 0.45);
      place(y);
      if (!shown && sAt(y) > 0.28) {
        shown = true;
        api.step(1);
        api.tween(s.det, [{ opacity: 0 }, { opacity: 1 }], { dur: 250 }).catch(() => {});
      }
    });
    conf = 0.97;
    place(STOP_Y);
    await api.wait(300);

    // 2. OCR
    api.step(2);
    await api.tween(s.panel, [{ opacity: 0 }, { opacity: 1 }], { dur: 300 });
    api.tween(s.plate, [{ opacity: 0 }, { opacity: 1 }, { opacity: 0.4 }, { opacity: 1 }], { dur: 500 }).catch(() => {});
    for (let i = 0; i < 3; i++) {
      await api.type(s.rows[i].v, ["TX 4KL2290", "3412875", "1182"][i], 30);
      await api.wait(150);
    }

    // 3. FMCSA
    api.step(3);
    for (let k = 0; k < 6; k++) { s.rows[3].v.textContent = "·".repeat((k % 3) + 1); await api.wait(140); }
    s.rows[3].v.textContent = `${t.active} ✓`;
    s.rows[3].v.setAttribute("fill", BOX);
    await api.wait(350);
    api.poster();

    // 4. Gate opens, the truck rolls past the camera
    api.step(4);
    s.gate.textContent = `● ${t.open}`;
    s.gate.setAttribute("fill", BOX);
    s.light.setAttribute("fill", BOX);
    await api.tween(s.arm, [{ transform: "rotate(0deg)" }, { transform: "rotate(82deg)" }], { dur: 1100, ease: "cubic-bezier(0.45, 0, 0.2, 1)" });
    api.tween(s.det, [{ opacity: 1 }, { opacity: 0 }], { dur: 300 }).catch(() => {});
    api.tween(s.plate, [{ opacity: 1 }, { opacity: 0 }], { dur: 200 }).catch(() => {});
    await api.tick(1700, (p) => {
      place(STOP_Y + Math.pow(p, 2) * 150);
      s.truck.style.opacity = String(1 - Math.max(0, (p - 0.5) / 0.5));   // passes under the camera
    }, "lin");
    await api.wait(300);
    s.light.setAttribute("fill", "#ff4d4f");
    s.gate.textContent = `● ${t.wait}`;
    s.gate.setAttribute("fill", "#ffb84d");
    await api.tween(s.arm, [{ transform: "rotate(82deg)" }, { transform: "rotate(0deg)" }], { dur: 1000, ease: "cubic-bezier(0.45, 0, 0.2, 1)" });
    await api.wait(400);
  },
};
