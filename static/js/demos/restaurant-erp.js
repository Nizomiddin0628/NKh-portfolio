/* Restaurant ERP: one receipt is paid, and six modules update at once —
   kitchen ticket, stock, cash, staff, loyalty, reports. Pulses travel
   from the till to every module the payment touches. */

export default {
  duration: 8500,
  rest: 1600,
  i18n: {
    en: {
      steps: [
        "A cashier rings up the order",
        "One payment…",
        "…updates kitchen, stock, cash, staff, loyalty and reports at once",
        "The owner sees the day live, for every branch",
      ],
      till: "Till · Chilonzor", total: "Total", pay: "Pay", paid: "Paid", today: "today",
      mods: ["KITCHEN", "STOCK", "REVENUE", "STAFF", "LOYALTY", "REPORTS"],
      rice: "Rice", checks: "checks", margin: "margin",
    },
    uz: {
      steps: [
        "Kassir buyurtmani kiritadi",
        "Bitta to'lov…",
        "…oshxona, ombor, kassa, xodimlar, bonus va hisobotni birdaniga yangilaydi",
        "Egasi kunni har bir filial bo'yicha jonli ko'radi",
      ],
      till: "Kassa · Chilonzor", total: "Jami", pay: "To'lash", paid: "To'landi", today: "bugun",
      mods: ["OSHXONA", "OMBOR", "TUSHUM", "XODIMLAR", "BONUS", "HISOBOT"],
      rice: "Guruch", checks: "chek", margin: "marja",
    },
    ru: {
      steps: [
        "Кассир пробивает заказ",
        "Одна оплата…",
        "…сразу обновляет кухню, склад, кассу, персонал, бонусы и отчёты",
        "Владелец видит день вживую, по каждому филиалу",
      ],
      till: "Касса · Чиланзар", total: "Итого", pay: "Оплатить", paid: "Оплачено", today: "сегодня",
      mods: ["КУХНЯ", "СКЛАД", "ВЫРУЧКА", "ПЕРСОНАЛ", "БОНУСЫ", "ОТЧЁТЫ"],
      rice: "Рис", checks: "чеков", margin: "маржа",
    },
  },

  build(svg, { h }, t) {
    const sum = (v) => v.toLocaleString("ru-RU").replace(/ /g, " ");

    // ── Receipt ──
    h("rect", { x: 12, y: 12, width: 140, height: 226, rx: 12, class: "d-card" }, svg);
    h("text", { x: 24, y: 33, "font-size": 10.5, class: "d-tx db", text: t.till }, svg);
    h("text", { x: 24, y: 47, "font-size": 9.5, class: "d-tx3 dm", text: "#1044 · Dilnoza" }, svg);
    h("line", { x1: 24, x2: 140, y1: 57, y2: 57, class: "d-line", "stroke-dasharray": "3 3" }, svg);
    const items = [["Osh ×2", 84000], ["Somsa ×3", 27000], ["Choy", 6000]].map(([name, price], i) => {
      const y = 76 + i * 20;
      const g = h("g", { opacity: 0 }, svg);
      h("text", { x: 24, y, "font-size": 11, class: "d-tx", text: name }, g);
      h("text", { x: 140, y, "font-size": 10.5, class: "d-tx2 dm", "text-anchor": "end", text: sum(price) }, g);
      return { g, price };
    });
    h("line", { x1: 24, x2: 140, y1: 140, y2: 140, class: "d-line", "stroke-dasharray": "3 3" }, svg);
    h("text", { x: 24, y: 160, "font-size": 10, class: "d-tx3", text: t.total }, svg);
    const total = h("text", { x: 140, y: 180, "font-size": 16, class: "d-tx dd", "text-anchor": "end", text: "0" }, svg);
    const btn = h("g", {}, svg);
    const btnBg = h("rect", { x: 24, y: 196, width: 116, height: 30, rx: 9, class: "d-acc" }, btn);
    const btnText = h("text", { x: 82, y: 215.5, "font-size": 11.5, fill: "#fff", "text-anchor": "middle", class: "db", text: t.pay }, btn);

    // ── Module tiles ──
    const W = 106, H = 70, X = [168, 282], Y = [12, 90, 168];
    const from = { x: 140, y: 211 };
    const wires = h("g", {}, svg);
    const tiles = t.mods.map((label, i) => {
      const x = X[i % 2], y = Y[Math.floor(i / 2)];
      const to = { x, y: y + H / 2 };
      const d = `M${from.x} ${from.y} C${from.x + 22} ${from.y} ${to.x - 26} ${to.y} ${to.x} ${to.y}`;
      const wire = h("path", { d, class: "d-line", opacity: 0.55 }, wires);
      const pulse = h("circle", { r: 3.2, class: "d-tq", opacity: 0, cx: from.x, cy: from.y }, svg);
      const g = h("g", { opacity: 0.5 }, svg);
      const bg = h("rect", { x, y, width: W, height: H, rx: 10, class: "d-card" }, g);
      const ring = h("rect", { x: x + 0.5, y: y + 0.5, width: W - 1, height: H - 1, rx: 10, fill: "none", class: "s-tq", "stroke-width": 1.6, opacity: 0 }, g);
      h("text", { x: x + 10, y: y + 18, "font-size": 8.5, class: "d-tx3 dm", text: label }, g);
      const value = h("text", { x: x + 10, y: y + 40, "font-size": 13.5, class: "d-tx dd" }, g);
      const sub = h("text", { x: x + 10, y: y + 57, "font-size": 9.5, class: "d-tx2" }, g);
      return { g, bg, ring, value, sub, wire, pulse, x, y };
    });

    const [kit, stock, rev, staff, loy, rep] = tiles;
    kit.value.textContent = "#1043"; kit.sub.textContent = "Lag'mon ×1";
    stock.value.textContent = t.rice; stock.sub.textContent = "18.6 kg";
    rev.value.textContent = "8 420 000"; rev.sub.textContent = t.today;
    staff.value.textContent = "Dilnoza"; staff.sub.textContent = `18 ${t.checks}`;
    loy.value.textContent = "Aziz K."; loy.sub.textContent = "2 340";
    rep.value.textContent = "33.6%"; rep.sub.textContent = t.margin;
    // Tiny sales bars in the report tile
    const bars = [10, 14, 9, 17, 13, 20].map((v, i) =>
      h("rect", { x: rep.x + 62 + i * 6.5, y: rep.y + 60 - v, width: 4, height: v, rx: 1, class: "d-acc o-b", opacity: 0.55 }, rep.g));

    return { items, total, btn, btnBg, btnText, tiles, bars, sum };
  },

  async play(api, s, t) {
    api.step(0);
    let running = 0;
    for (const it of s.items) {
      await api.show(it.g, 320, "translateX(-8px)");
      const before = running;
      running += it.price;
      await api.count(s.total, before, running, 380, (v) => s.sum(Math.round(v / 1000) * 1000));
      await api.wait(120);
    }
    await api.wait(300);

    api.step(1);
    await api.tween(s.btn, [{ transform: "scale(1)" }, { transform: "scale(0.94)" }, { transform: "scale(1)" }], { dur: 300 });
    s.btnBg.setAttribute("class", "d-ok");
    s.btnText.textContent = `✓ ${t.paid}`;
    await api.wait(250);

    api.step(2);
    const [kit, stock, rev, staff, loy, rep] = s.tiles;
    const travel = (tile, delay) => (async () => {
      await api.wait(delay);
      tile.pulse.style.opacity = "1";
      const len = tile.wire.getTotalLength();
      await api.tick(520, (p) => {
        const pt = tile.wire.getPointAtLength(p * len);
        tile.pulse.setAttribute("cx", pt.x.toFixed(1));
        tile.pulse.setAttribute("cy", pt.y.toFixed(1));
      }, "inOut");
      tile.pulse.style.opacity = "0";
      tile.g.style.opacity = "1";
      api.tween(tile.ring, [{ opacity: 0.9 }, { opacity: 0 }], { dur: 1100, delay: 200 }).catch(() => {});
      await api.tween(tile.g, [{ transform: "scale(1.04)" }, { transform: "scale(1)" }], { dur: 420 });
    })();

    const updates = [
      travel(kit, 0).then(() => { kit.value.textContent = "#1044"; kit.sub.textContent = "Osh ×2 · 0:00"; }),
      travel(stock, 90).then(() => api.count(stock.sub, 18.6, 18.0, 600, (v) => `${v.toFixed(1)} kg  −0.6`)),
      travel(rev, 180).then(() => api.count(rev.value, 8420000, 8537000, 900, (v) => s.sum(Math.round(v / 1000) * 1000))),
      travel(staff, 270).then(() => { staff.sub.textContent = `19 ${t.checks}`; }),
      travel(loy, 360).then(() => api.count(loy.sub, 2340, 3510, 700, (v) => `${s.sum(Math.round(v))}  +1 170`)),
      travel(rep, 450).then(async () => {
        await api.count(rep.value, 33.6, 34.1, 600, (v) => `${v.toFixed(1)}%`);
        api.tween(s.bars[5], [{ transform: "scaleY(1)" }, { transform: "scaleY(1.25)" }], { dur: 500 }).catch(() => {});
      }),
    ];
    await Promise.all(updates);

    api.step(3);
    api.poster();
    // Kitchen ticket timer starts running
    for (let sec = 1; sec <= 3; sec++) {
      await api.wait(1000);
      kit.sub.textContent = `Osh ×2 · 0:0${sec}`;
    }
  },
};
