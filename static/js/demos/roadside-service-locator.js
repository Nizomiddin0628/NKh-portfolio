/* Roadside: a truck breaks down on I-40. A 150-mile radius opens, shops
   appear, the list first sorts by distance, then re-sorts once past
   outcomes are weighed in. The route is drawn to the winner and the job's
   result feeds back into its score. */

export default {
  duration: 12000,
  rest: 1500,
  i18n: {
    en: {
      steps: [
        "A truck breaks down on the interstate",
        "Shops within 150 miles are found",
        "Ranking weighs distance and past outcomes",
        "Every call-out is scored afterwards",
      ],
      broke: "Breakdown", byDist: "By distance", byBoth: "Distance + outcome", done: "fixed in 2 h",
    },
    uz: {
      steps: [
        "Yuk mashinasi trassada buzilib qoladi",
        "150 mil radiusdagi ustaxonalar topiladi",
        "Reyting masofa va oldingi natijalar asosida tuziladi",
        "Har bir chaqiruvdan keyin natija baholanadi",
      ],
      broke: "Nosozlik", byDist: "Masofa bo'yicha", byBoth: "Masofa + natija", done: "2 soatda tuzatildi",
    },
    ru: {
      steps: [
        "Тягач ломается на трассе",
        "Находятся сервисы в радиусе 150 миль",
        "Рейтинг учитывает расстояние и прошлые итоги",
        "Каждый вызов потом оценивается",
      ],
      broke: "Поломка", byDist: "По расстоянию", byBoth: "Расстояние + итог", done: "починили за 2 ч",
    },
  },

  build(svg, { h, rng }, t) {
    const R = rng(3);
    const uid = "r" + Math.random().toString(36).slice(2, 8);
    const clip = h("clipPath", { id: `${uid}c` }, h("defs", {}, svg));
    h("rect", { x: 12, y: 12, width: 240, height: 226, rx: 12 }, clip);

    // ── Map ──
    h("rect", { x: 12, y: 12, width: 240, height: 226, rx: 12, class: "d-card" }, svg);
    const map = h("g", { "clip-path": `url(#${uid}c)` }, svg);
    let grid = "";
    for (let i = 0; i < 9; i++) {
      const y = 20 + i * 28 + R() * 8;
      grid += `M12 ${y.toFixed(1)}C80 ${(y + R() * 30 - 15).toFixed(1)} 170 ${(y + R() * 30 - 15).toFixed(1)} 252 ${(y + R() * 16 - 8).toFixed(1)}`;
      const x = 20 + i * 28 + R() * 8;
      grid += `M${x.toFixed(1)} 12C${(x + R() * 30 - 15).toFixed(1)} 90 ${(x + R() * 30 - 15).toFixed(1)} 170 ${(x + R() * 16 - 8).toFixed(1)} 238`;
    }
    h("path", { d: grid, fill: "none", class: "s-line", "stroke-width": 0.8, opacity: 0.55 }, map);
    h("path", { d: "M4 196 C70 180 110 150 150 120 S220 70 262 58", fill: "none", class: "s-tx3", "stroke-width": 5, "stroke-linecap": "round", opacity: 0.35 }, map);
    h("path", { d: "M4 196 C70 180 110 150 150 120 S220 70 262 58", fill: "none", style: "stroke: var(--surface)", "stroke-width": 1, "stroke-dasharray": "6 6", opacity: 0.9 }, map);
    h("rect", { x: 198, y: 64, width: 28, height: 16, rx: 4, class: "d-acc" }, map);
    h("text", { x: 212, y: 75.5, "font-size": 9, fill: "#fff", "text-anchor": "middle", class: "dm db", text: "I-40" }, map);

    const T = { x: 98, y: 160 };
    const radius = h("circle", { cx: T.x, cy: T.y, r: 92, class: "d-acc s-acc", "fill-opacity": 0.06, "stroke-width": 1.2, "stroke-dasharray": "4 4", style: "transform: scale(0)" }, map);
    const rLabel = h("text", { x: T.x - 78, y: T.y - 66, "font-size": 10, class: "d-acc dm db", opacity: 0, text: "150 mi" }, map);

    // Shops: A is closest but often fails, B is the reliable one
    const shops = [
      { key: "A", name: "Mesa Diesel", mi: 12, score: 41, x: 70, y: 118 },
      { key: "B", name: "Big Rig Pros", mi: 18, score: 92, x: 150, y: 176 },
      { key: "C", name: "Desert Truck Care", mi: 25, score: 67, x: 40, y: 206 },
    ];
    const extra = [[160, 96], [128, 222], [26, 150]];
    const route = h("path", { d: `M${T.x} ${T.y} C120 172 132 186 ${shops[1].x} ${shops[1].y - 8}`, fill: "none", class: "s-acc", "stroke-width": 2.4, "stroke-linecap": "round", opacity: 0 }, map);
    const pin = (x, y, label, faint) => {
      const g = h("g", { opacity: 0 }, map);
      h("path", { d: `M${x} ${y}c-6-7-9-10-9-14a9 9 0 0 1 18 0c0 4-3 7-9 14z`, class: faint ? "d-tx3" : "d-tq" }, g);
      if (label) h("text", { x, y: y - 11, "font-size": 8.5, fill: "#fff", "text-anchor": "middle", class: "dm db", text: label }, g);
      return g;
    };
    shops.forEach((s) => { s.pin = pin(s.x, s.y, s.key); });
    const extras = extra.map(([x, y]) => pin(x, y, "", true));

    // Broken truck
    const truck = h("g", {}, map);
    h("rect", { x: T.x - 9, y: T.y - 6, width: 18, height: 12, rx: 3, class: "d-tx" }, truck);
    const hazard = h("circle", { cx: T.x, cy: T.y, r: 12, fill: "none", class: "s-bad", "stroke-width": 2, opacity: 0 }, map);
    const tag = h("g", { opacity: 0 }, map);
    h("rect", { x: T.x - 40, y: T.y + 12, width: 80, height: 18, rx: 9, class: "d-bad" }, tag);
    h("text", { x: T.x, y: T.y + 24.5, "font-size": 9.5, fill: "#fff", "text-anchor": "middle", class: "db", text: t.broke }, tag);

    // ── Ranking list ──
    const LX = 262;
    h("rect", { x: LX, y: 12, width: 126, height: 226, rx: 12, class: "d-card" }, svg);
    const mode = h("text", { x: LX + 12, y: 32, "font-size": 9.5, class: "d-tx3 dm", text: t.byDist.toUpperCase() }, svg);
    const ROW = 52, TOP = 44;
    shops.forEach((s, i) => {
      const g = h("g", { opacity: 0 }, svg);
      h("rect", { x: LX + 8, y: TOP + i * ROW, width: 110, height: 44, rx: 8, class: "d-card2" }, g);
      h("text", { x: LX + 16, y: TOP + i * ROW + 17, "font-size": 10, class: "d-tx db", text: s.name.length > 15 ? s.name.slice(0, 14) + "…" : s.name }, g);
      h("text", { x: LX + 16, y: TOP + i * ROW + 34, "font-size": 9.5, class: "d-tx2 dm", text: `${s.mi} mi` }, g);
      const chip = h("g", { opacity: 0 }, g);
      const good = s.score >= 80, mid = s.score >= 60;
      h("rect", { x: LX + 72, y: TOP + i * ROW + 24, width: 40, height: 15, rx: 7.5, class: good ? "d-ok" : mid ? "d-warn" : "d-bad", opacity: 0.16 }, chip);
      const score = h("text", { x: LX + 92, y: TOP + i * ROW + 34.5, "font-size": 9, class: `${good ? "d-ok" : mid ? "d-warn" : "d-bad"} dm db`, "text-anchor": "middle", text: `${s.score}%` }, chip);
      s.row = g; s.chip = chip; s.scoreEl = score; s.rank = i;
    });
    const doneChip = h("g", { opacity: 0 }, svg);
    h("rect", { x: LX + 8, y: 206, width: 110, height: 22, rx: 11, class: "d-ok", opacity: 0.16 }, doneChip);
    h("text", { x: LX + 63, y: 220.5, "font-size": 9.5, class: "d-ok db", "text-anchor": "middle", text: `✓ ${t.done}` }, doneChip);

    return { shops, extras, radius, rLabel, truck, hazard, tag, route, mode, doneChip, ROW };
  },

  async play(api, s, t) {
    api.step(0);
    await api.wait(300);
    await api.tween(s.truck, [{ transform: "translateX(-60px)" }, { transform: "translateX(0px)" }], { dur: 900, ease: "cubic-bezier(0.2, 0.7, 0.3, 1)" });
    const pulse = api.loop(s.hazard, [{ transform: "scale(0.6)", opacity: 0.9 }, { transform: "scale(1.8)", opacity: 0 }], { duration: 1200, easing: "ease-out" });
    s.hazard.style.opacity = "0.9";
    await api.show(s.tag, 320, "translateY(-4px)");
    await api.wait(500);

    api.step(1);
    await api.tween(s.radius, [{ transform: "scale(0)" }, { transform: "scale(1)" }], { dur: 900 });
    api.show(s.rLabel, 300);
    for (const p of [...s.shops.map((x) => x.pin), ...s.extras]) await api.show(p, 220, "translateY(-6px)");
    for (const sh of s.shops) await api.show(sh.row, 280, "translateX(8px)");
    await api.wait(500);

    api.step(2);
    s.mode.textContent = t.byBoth.toUpperCase();
    for (const sh of s.shops) await api.show(sh.chip, 220, "scale(0.6)");
    await api.wait(300);
    // Re-rank: B, C, A
    const order = ["B", "C", "A"];
    await Promise.all(s.shops.map((sh) => {
      const to = order.indexOf(sh.key);
      const dy = (to - sh.rank) * s.ROW;
      return api.tween(sh.row, [{ transform: "translateY(0px)" }, { transform: `translateY(${dy}px)` }], { dur: 700, ease: "cubic-bezier(0.65, 0, 0.35, 1)" });
    }));
    s.route.style.opacity = "1";
    await api.draw(s.route, 700);
    api.poster();

    api.step(3);
    await api.wait(900);
    api.unloop(pulse);
    s.hazard.style.opacity = "0";
    await api.show(s.doneChip, 360, "translateY(6px)");
    const B = s.shops[1];
    await api.count(B.scoreEl, 92, 93, 500, (v) => `${Math.round(v)}%`);
    await api.wait(1400);
  },
};
