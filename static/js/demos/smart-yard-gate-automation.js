/* Smart Yard: a camera frame. The truck rolls in, YOLO locks on, OCR reads
   USDOT / unit / plate, FMCSA confirms the carrier, the barrier lifts and
   the event is written to the log. The camera view keeps its own dark
   palette in both themes: it stands for a video feed. */

const C = {
  bg: "#0a111f", ground: "#0f192c", wire: "#1b2943", lane: "#2a3858",
  hud: "#8ea0c6", hudDim: "#56658a", tq: "#35d6dd", ok: "#3fcf8e", red: "#ff5d62",
  panel: "rgba(6,11,22,0.82)", panelLine: "#25324c", white: "#e9eef8",
};

export default {
  duration: 10200,
  rest: 1200,
  i18n: {
    en: {
      steps: [
        "A truck enters the lane — seven cameras watch the yard",
        "YOLO detects the vehicle and its type",
        "OCR reads USDOT, unit number and plate",
        "The carrier is checked against FMCSA",
        "The barrier lifts and the event is logged",
      ],
      wait: "waiting for vehicle", opened: "OPENED", active: "ACTIVE",
    },
    uz: {
      steps: [
        "Yuk mashinasi yo'lakka kiradi — hovlini 7 ta kamera kuzatadi",
        "YOLO transportni va uning turini aniqlaydi",
        "OCR USDOT, unit raqami va davlat raqamini o'qiydi",
        "Tashuvchi FMCSA reyestrida tekshiriladi",
        "To'siq ko'tariladi, hodisa jurnalga yoziladi",
      ],
      wait: "transport kutilmoqda", opened: "OCHILDI", active: "FAOL",
    },
    ru: {
      steps: [
        "Тягач въезжает на полосу — двор видят семь камер",
        "YOLO находит транспорт и определяет тип",
        "OCR читает USDOT, номер юнита и госномер",
        "Перевозчик проверяется по реестру FMCSA",
        "Шлагбаум поднимается, событие пишется в журнал",
      ],
      wait: "ожидание транспорта", opened: "ОТКРЫТ", active: "АКТИВЕН",
    },
  },

  build(svg, { h }, t) {
    h("rect", { x: 0, y: 0, width: 400, height: 250, fill: C.bg }, svg);
    h("rect", { x: 0, y: 186, width: 400, height: 64, fill: C.ground }, svg);
    // Back fence
    const fence = h("g", { stroke: C.wire, "stroke-width": 1 }, svg);
    for (let x = 6; x < 400; x += 22) h("line", { x1: x, y1: 112, x2: x, y2: 186 }, fence);
    h("line", { x1: 0, y1: 120, x2: 400, y2: 120 }, fence);
    h("line", { x1: 0, y1: 150, x2: 400, y2: 150 }, fence);
    // Lane marking
    h("line", { x1: 0, y1: 214, x2: 400, y2: 214, stroke: C.lane, "stroke-width": 2, "stroke-dasharray": "16 12" }, svg);

    // Truck (drawn at its parked position, moved with transform)
    const truck = h("g", { style: "transform: translateX(-300px)" }, svg);
    h("rect", { x: 70, y: 112, width: 156, height: 66, rx: 3, fill: "#c3ccde" }, truck);
    for (let x = 96; x < 226; x += 26) h("line", { x1: x, y1: 116, x2: x, y2: 174, stroke: "#aab4c9", "stroke-width": 1 }, truck);
    h("rect", { x: 70, y: 164, width: 156, height: 5, fill: "#18b7be", opacity: 0.85 }, truck);
    h("rect", { x: 66, y: 178, width: 228, height: 5, rx: 2, fill: "#1d2638" }, truck);
    h("path", { d: "M230 178 V132 Q230 124 238 124 H268 Q276 124 280 132 L292 152 Q295 157 295 163 V178 Z", fill: "#3a4fd8" }, truck);
    h("path", { d: "M262 130 H272 Q276 130 278 134 L286 150 H262 Z", fill: "#a9bbff", opacity: 0.75 }, truck);
    h("text", { x: 238, y: 146, fill: "#dfe6ff", "font-size": 6.5, class: "dm", text: "USDOT 3412875" }, truck);
    h("text", { x: 238, y: 166, fill: "#ffffff", "font-size": 12, class: "dm db", text: "1182" }, truck);
    h("rect", { x: 280, y: 168, width: 16, height: 8, rx: 1.5, fill: "#f1f4fa" }, truck);
    for (const cx of [92, 116, 196, 246, 276]) {
      h("circle", { cx, cy: 186, r: 9.5, fill: "#0c1322", stroke: "#3b4867", "stroke-width": 2.5 }, truck);
    }

    // Gate: post, signal light, striped arm
    h("rect", { x: 318, y: 126, width: 9, height: 66, rx: 2, fill: "#2a3754" }, svg);
    const light = h("circle", { cx: 322.5, cy: 134, r: 3.5, fill: C.red }, svg);
    const arm = h("g", { class: "o-l" }, svg);
    h("rect", { x: 324, y: 150, width: 76, height: 7, rx: 3.5, fill: C.white }, arm);
    for (let x = 334; x < 400; x += 16) h("rect", { x, y: 150, width: 8, height: 7, fill: C.red }, arm);

    // Detection box around the parked truck
    const det = h("g", { opacity: 0 }, svg);
    h("rect", { x: 76, y: 108, width: 240, height: 88, fill: C.tq, "fill-opacity": 0.07, stroke: C.tq, "stroke-width": 1.2 }, det);
    const k = 12;
    h("path", {
      d: `M76 ${108 + k} V108 H${76 + k} M${316 - k} 108 H316 V${108 + k} M316 ${196 - k} V196 H${316 - k} M${76 + k} 196 H76 V${196 - k}`,
      fill: "none", stroke: C.tq, "stroke-width": 3, "stroke-linecap": "round",
    }, det);
    h("rect", { x: 76, y: 92, width: 136, height: 16, fill: C.tq }, det);
    h("text", { x: 82, y: 104, "font-size": 10.5, fill: "#04282b", class: "dm db", text: "tractor+trailer 0.97" }, det);

    // Read-out panel
    const panel = h("g", { opacity: 0 }, svg);
    h("rect", { x: 268, y: 28, width: 124, height: 76, rx: 7, fill: C.panel, stroke: C.panelLine }, panel);
    const rows = [["USDOT", "3412875"], ["UNIT", "1182"], ["PLATE", "TX 4KL2290"], ["FMCSA", ""]];
    const vals = rows.map(([label], i) => {
      const y = 45 + i * 17;
      h("text", { x: 277, y, "font-size": 8.5, fill: C.hudDim, class: "dm", text: label }, panel);
      return h("text", { x: 385, y, "font-size": 11, fill: C.white, class: "dm db", "text-anchor": "end" }, panel);
    });

    // Reticles on the truck where the text is read
    const ret = (x, y, w, hh) => h("rect", { x, y, width: w, height: hh, rx: 2, fill: "none", stroke: C.tq, "stroke-width": 1.4, opacity: 0 }, svg);
    const reticles = [ret(251, 137, 57, 13), ret(250, 154, 36, 16), ret(293, 165, 22, 14)];  // parked truck: drawing + 16 px

    // HUD
    h("text", { x: 12, y: 20, "font-size": 10, fill: C.hud, class: "dm", text: "CAM 03 · YARD-IN" }, svg);
    const rec = h("circle", { cx: 304, cy: 16.5, r: 3.5, fill: C.red }, svg);
    h("text", { x: 311, y: 20, "font-size": 10, fill: C.hud, class: "dm", text: "REC" }, svg);
    const clock = h("text", { x: 388, y: 20, "font-size": 10, fill: C.hud, class: "dm", "text-anchor": "end", text: "08:42:17" }, svg);
    const scan = h("rect", { x: 0, y: 0, width: 400, height: 2, fill: C.tq, opacity: 0.08, class: "vb" }, svg);

    // Event log
    h("rect", { x: 0, y: 226, width: 400, height: 24, fill: "rgba(4,8,16,0.88)" }, svg);
    const logDot = h("circle", { cx: 14, cy: 238, r: 3.5, fill: C.hudDim }, svg);
    const log = h("text", { x: 24, y: 242, "font-size": 11, fill: C.hud, class: "dm", text: t.wait }, svg);

    return { truck, det, panel, vals, reticles, arm, light, rec, clock, scan, log, logDot };
  },

  async play(api, s, t) {
    // Ambient: REC blink, running clock, slow scanline
    api.loop(s.rec, [{ opacity: 1 }, { opacity: 0.2 }], { duration: 1100, direction: "alternate" });
    api.loop(s.scan, [{ transform: "translateY(0px)" }, { transform: "translateY(248px)" }], { duration: 3800, easing: "linear" });
    let sec = 17;
    api.spawn(async () => {
      for (;;) { await api.wait(1000); sec += 1; s.clock.textContent = `08:42:${String(sec).padStart(2, "0")}`; }
    });

    api.step(0);
    await api.wait(350);
    await api.tween(s.truck, [{ transform: "translateX(-300px)" }, { transform: "translateX(16px)" }], { dur: 2300, ease: "cubic-bezier(0.2, 0.7, 0.25, 1)" });

    api.step(1);
    await api.tween(s.det, [{ opacity: 0, transform: "scale(1.12)" }, { opacity: 1, transform: "scale(1)" }], { dur: 420 });
    await api.tween(s.det, [{ opacity: 1 }, { opacity: 0.45 }, { opacity: 1 }], { dur: 300, ease: "linear" });

    api.step(2);
    await api.show(s.panel, 380, "translateX(8px)");
    for (let i = 0; i < 3; i++) {
      api.tween(s.reticles[i], [{ opacity: 0, transform: "scale(1.6)" }, { opacity: 1, transform: "scale(1)" }], { dur: 260 });
      await api.type(s.vals[i], ["3412875", "1182", "TX 4KL2290"][i], 26);
      await api.wait(140);
    }

    api.step(3);
    for (let k = 0; k < 6; k++) { s.vals[3].textContent = "·".repeat((k % 3) + 1); await api.wait(130); }
    s.vals[3].textContent = `${t.active} ✓`;
    s.vals[3].setAttribute("fill", C.ok);
    s.reticles.forEach((r) => r.setAttribute("stroke", C.ok));
    await api.wait(250);
    api.poster();

    api.step(4);
    s.light.setAttribute("fill", C.ok);
    await api.tween(s.arm, [{ transform: "rotate(0deg)" }, { transform: "rotate(-80deg)" }], { dur: 900, ease: "cubic-bezier(0.5, 0, 0.2, 1)" });
    s.logDot.setAttribute("fill", C.ok);
    s.log.setAttribute("fill", C.white);
    const line = `08:42:${String(sec).padStart(2, "0")}  IN  UNIT 1182  ${t.opened}`;
    api.type(s.log, line, 40);
    s.reticles.forEach((r) => api.hide(r, 200));
    api.hide(s.det, 260);
    await api.hide(s.panel, 400);
    await api.tween(s.truck, [{ transform: "translateX(16px)" }, { transform: "translateX(420px)" }], { dur: 1700, ease: "cubic-bezier(0.55, 0, 0.75, 0.6)" });
    s.light.setAttribute("fill", C.red);
    await api.tween(s.arm, [{ transform: "rotate(-80deg)" }, { transform: "rotate(0deg)" }], { dur: 800, ease: "cubic-bezier(0.5, 0, 0.2, 1)" });
    await api.wait(700);
  },
};
