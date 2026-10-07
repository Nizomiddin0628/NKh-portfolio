/* AI Kotib: the clock reaches 08:30 and the morning report arrives in
   Telegram. The manager answers with a voice note, the secretary turns it
   into a change and waits for ✔ before touching the database. */

const TG = {
  bg: "#0e1621", head: "#17212b", bot: "#182533", me: "#2b5278", text: "#e8edf3",
  soft: "#9fb0c3", faint: "#6d7f92", link: "#7fb6e8", ok: "#3fcf8e", warn: "#e2a54b", btn: "#1f3448",
};

export default {
  duration: 11200,
  rest: 1600,
  i18n: {
    en: {
      steps: [
        "08:30 — the morning report arrives on its own",
        "The manager replies with a voice note",
        "AI Kotib prepares the change",
        "It is applied only after ✔",
      ],
      morning: "Morning report", evening: "Evening summary",
      title: "Yesterday · 06.10", l1: "Sales 12.4M · 96 checks", l2: "Today: 3 bookings, 19:00", l3: "Low: rice — 2 days left",
      heard: "“Make osh 45 000”", change: "Osh price", ok: "Confirm", no: "Cancel", done: "Done",
    },
    uz: {
      steps: [
        "08:30 — ertalabki hisobot o'zi keladi",
        "Menejer ovozli xabar bilan javob beradi",
        "AI Kotib o'zgarishni tayyorlaydi",
        "U faqat ✔ bosilgandan keyin bajariladi",
      ],
      morning: "Ertalabki hisobot", evening: "Kechki xulosa",
      title: "Kecha · 06.10", l1: "Tushum 12,4 mln · 96 chek", l2: "Bugun: 3 ta bron, 19:00", l3: "Tugayapti: guruch — 2 kunga",
      heard: "«Oshning narxini 45 000 qil»", change: "Osh narxi", ok: "Tasdiqlash", no: "Bekor", done: "Bajarildi",
    },
    ru: {
      steps: [
        "08:30 — утренний отчёт приходит сам",
        "Менеджер отвечает голосовым",
        "AI Kotib готовит изменение",
        "Оно применяется только после ✔",
      ],
      morning: "Утренний отчёт", evening: "Вечерняя сводка",
      title: "Вчера · 06.10", l1: "Выручка 12,4 млн · 96 чеков", l2: "Сегодня: 3 брони, 19:00", l3: "Мало: рис — на 2 дня",
      heard: "«Поставь плов 45 000»", change: "Цена плова", ok: "Подтвердить", no: "Отмена", done: "Выполнено",
    },
  },

  build(svg, { h, wrapText }, t) {
    const uid = "k" + Math.random().toString(36).slice(2, 8);

    // ── Schedule column ──
    const clockCard = h("g", {}, svg);
    h("rect", { x: 12, y: 12, width: 104, height: 112, rx: 12, class: "d-card" }, clockCard);
    h("circle", { cx: 64, cy: 50, r: 22, fill: "none", class: "s-line", "stroke-width": 2 }, clockCard);
    const clockArc = h("circle", { cx: 64, cy: 50, r: 22, fill: "none", class: "s-tq", "stroke-width": 2.4, "stroke-linecap": "round",
      "stroke-dasharray": `${2 * Math.PI * 22}`, "stroke-dashoffset": `${2 * Math.PI * 22 * 0.04}`, style: "transform: rotate(-90deg)" }, clockCard);
    const time = h("text", { x: 64, y: 54, "font-size": 11.5, class: "d-tx dm db", "text-anchor": "middle", text: "08:29" }, clockCard);
    const mLabel = h("text", { x: 64, y: 92, "font-size": 9.5, class: "d-tx2", "text-anchor": "middle" }, clockCard);
    wrapText(mLabel, t.morning, 14, 12);
    h("rect", { x: 12, y: 132, width: 104, height: 52, rx: 12, class: "d-card", opacity: 0.55 }, svg);
    h("text", { x: 24, y: 154, "font-size": 11.5, class: "d-tx3 dm db", text: "18:00" }, svg);
    const eLabel = h("text", { x: 24, y: 171, "font-size": 9.5, class: "d-tx3" }, svg);
    wrapText(eLabel, t.evening, 16, 12);
    h("rect", { x: 12, y: 192, width: 104, height: 46, rx: 12, class: "d-card", opacity: 0.55 }, svg);
    h("text", { x: 24, y: 212, "font-size": 9, class: "d-tx3 dm", text: "Gemini · tools" }, svg);
    h("text", { x: 24, y: 226, "font-size": 9, class: "d-tx3 dm", text: "ERP database" }, svg);

    // ── Telegram chat ──
    const CX = 124, CW = 264;
    h("rect", { x: CX, y: 12, width: CW, height: 226, rx: 14, fill: TG.bg }, svg);
    h("path", { d: `M${CX} 40V26q0-14 14-14h${CW - 28}q14 0 14 14v14z`, fill: TG.head }, svg);
    h("circle", { cx: CX + 18, cy: 26, r: 8, fill: "#2b5278" }, svg);
    h("text", { x: CX + 18, y: 29.5, "font-size": 8.5, fill: "#fff", "text-anchor": "middle", class: "db", text: "AI" }, svg);
    h("text", { x: CX + 32, y: 24, "font-size": 10.5, fill: TG.text, class: "db", text: "AI Kotib" }, svg);
    h("text", { x: CX + 32, y: 35, "font-size": 8.5, fill: TG.faint, text: "bot" }, svg);

    const clip = h("clipPath", { id: `${uid}c` }, h("defs", {}, svg));
    h("rect", { x: CX, y: 41, width: CW, height: 197 }, clip);
    const view = h("g", { "clip-path": `url(#${uid}c)` }, svg);
    const msgs = h("g", {}, view);

    // 1. Report
    const rep = h("g", { opacity: 0 }, msgs);
    h("rect", { x: CX + 10, y: 50, width: 196, height: 74, rx: 10, fill: TG.bot }, rep);
    h("text", { x: CX + 20, y: 67, "font-size": 10.5, fill: TG.text, class: "db", text: t.title }, rep);
    const lines = [[t.l1, TG.ok], [t.l2, TG.link], [t.l3, TG.warn]].map(([txt, color], i) => {
      const g = h("g", { opacity: 0 }, rep);
      h("rect", { x: CX + 20, y: 77 + i * 15, width: 3, height: 9, rx: 1.5, fill: color }, g);
      h("text", { x: CX + 28, y: 85 + i * 15, "font-size": 9.8, fill: TG.soft, text: txt }, g);
      return g;
    });
    h("text", { x: CX + 198, y: 120, "font-size": 7.5, fill: TG.faint, "text-anchor": "end", class: "dm", text: "08:30" }, rep);

    // 2. Voice note from the manager
    const voice = h("g", { opacity: 0 }, msgs);
    const VX = CX + 110;
    h("rect", { x: VX, y: 132, width: 144, height: 34, rx: 10, fill: TG.me }, voice);
    h("circle", { cx: VX + 17, cy: 149, r: 10, fill: "#fff" }, voice);
    h("path", { d: `M${VX + 14} 144v10l8-5z`, fill: TG.me }, voice);
    const bars = [];
    for (let i = 0; i < 20; i++) {
      const hh = 4 + Math.abs(Math.sin(i * 1.7)) * 12;
      bars.push(h("rect", { x: VX + 33 + i * 4.3, y: 149 - hh / 2, width: 2.4, height: hh, rx: 1.2, fill: "#a8c7e6", opacity: 0.55 }, voice));
    }
    h("text", { x: VX + 136, y: 162, "font-size": 7.5, fill: "#cfe0f1", "text-anchor": "end", class: "dm", text: "0:04" }, voice);
    const heard = h("text", { x: VX + 144, y: 180, "font-size": 9.5, fill: TG.soft, "text-anchor": "end", "font-style": "italic", opacity: 0, text: t.heard }, msgs);

    // 3. Confirmation card
    const card = h("g", { opacity: 0 }, msgs);
    h("rect", { x: CX + 10, y: 190, width: 196, height: 70, rx: 10, fill: TG.bot }, card);
    h("text", { x: CX + 20, y: 207, "font-size": 9.5, fill: TG.faint, text: t.change }, card);
    h("text", { x: CX + 20, y: 224, "font-size": 12, fill: TG.text, class: "dm", text: "42 000 → 45 000" }, card);
    const okBtn = h("g", {}, card);
    const okBg = h("rect", { x: CX + 16, y: 232, width: 90, height: 22, rx: 7, fill: TG.btn }, okBtn);
    const okText = h("text", { x: CX + 61, y: 246.5, "font-size": 9.5, fill: TG.text, "text-anchor": "middle", text: `✔ ${t.ok}` }, okBtn);
    const noBtn = h("g", {}, card);
    h("rect", { x: CX + 110, y: 232, width: 90, height: 22, rx: 7, fill: TG.btn }, noBtn);
    h("text", { x: CX + 155, y: 246.5, "font-size": 9.5, fill: TG.soft, "text-anchor": "middle", text: `✖ ${t.no}` }, noBtn);
    const ripple = h("circle", { cx: CX + 61, cy: 243, r: 14, fill: "#ffffff", opacity: 0 }, card);

    return { time, clockArc, clockCard, rep, lines, voice, bars, heard, card, okBg, okText, noBtn, ripple, msgs };
  },

  async play(api, s, t) {
    const C = 2 * Math.PI * 22;
    api.step(0);
    await api.wait(500);
    await api.tween(s.clockArc, [{ strokeDashoffset: C * 0.04 }, { strokeDashoffset: 0 }], { dur: 700 });
    s.time.textContent = "08:30";
    await api.tween(s.clockCard, [{ transform: "scale(1)" }, { transform: "scale(1.02)" }, { transform: "scale(1)" }], { dur: 420 });
    await api.show(s.rep, 420, "translateY(10px)");
    for (const l of s.lines) await api.show(l, 300, "translateX(-6px)");
    await api.wait(700);

    api.step(1);
    await api.show(s.voice, 380, "translateY(10px)");
    // play the voice note: bars light up left to right
    await api.tick(1300, (p) => {
      const n = Math.round(p * s.bars.length);
      s.bars.forEach((b, i) => b.setAttribute("opacity", i < n ? 1 : 0.55));
    });
    await api.show(s.heard, 380, "translateY(4px)");
    await api.wait(400);

    api.step(2);
    await api.tween(s.msgs, [{ transform: "translateY(0px)" }, { transform: "translateY(-30px)" }], { dur: 600 });
    await api.show(s.card, 420, "translateY(10px)");
    await api.wait(900);
    api.poster();

    api.step(3);
    await api.tween(s.ripple, [{ opacity: 0.35, transform: "scale(0.2)" }, { opacity: 0, transform: "scale(2.6)" }], { dur: 520 });
    s.okBg.setAttribute("fill", TG.ok);
    s.okText.setAttribute("fill", "#0e1621");
    s.okText.textContent = `✔ ${t.done}`;
    await api.hide(s.noBtn, 300);
    await api.wait(1800);
  },
};
