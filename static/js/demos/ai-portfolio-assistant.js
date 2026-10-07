/* AI assistant: a visitor asks in their own language, the agent calls its
   tools, the answer streams in, and a lead card lands in the owner's
   Telegram a moment later. */

export default {
  duration: 10300,
  rest: 1600,
  i18n: {
    en: {
      steps: [
        "A visitor asks in their own language",
        "The agent checks real projects through its tools",
        "The answer streams in, word by word",
        "The lead reaches my Telegram within seconds",
      ],
      sub: "answers in 3 languages", ph: "Ask about my work…",
      q: "Can you build a booking bot for my clinic?",
      a: "Yes. He built AI Kotib — a Telegram secretary for restaurants. I've sent him your request; expect a reply today.",
      lead: "New lead", need: "Clinic · booking bot", b1: "Contacted", b2: "Draft reply",
      today: "Today", rep1: "Daily report", rep2: "Visits 13 · Leads 0",
    },
    uz: {
      steps: [
        "Mehmon o'z tilida savol beradi",
        "Agent tool'lar orqali haqiqiy loyihalarni tekshiradi",
        "Javob so'zma-so'z oqib chiqadi",
        "Lead bir necha soniyada Telegram'imga tushadi",
      ],
      sub: "3 tilda javob beradi", ph: "Savol yozing…",
      q: "Klinikam uchun navbatga yozadigan bot qila olasizmi?",
      a: "Ha. U restoranlar uchun AI Kotib — Telegram kotibini qilgan. So'rovingizni unga yubordim, bugun javob beradi.",
      lead: "Yangi so'rov", need: "Klinika · navbat boti", b1: "Bog'landim", b2: "Javob tayyorla",
      today: "Bugun", rep1: "Kunlik hisobot", rep2: "Tashrif 13 · So'rov 0",
    },
    ru: {
      steps: [
        "Посетитель спрашивает на своём языке",
        "Агент проверяет реальные проекты через инструменты",
        "Ответ появляется слово за словом",
        "Заявка приходит мне в Telegram за секунды",
      ],
      sub: "отвечает на 3 языках", ph: "Задайте вопрос…",
      q: "Сделаете бот записи для моей клиники?",
      a: "Да. Он сделал AI Kotib — Telegram-секретаря для ресторанов. Я передал ему вашу заявку, ответ будет сегодня.",
      lead: "Новая заявка", need: "Клиника · бот записи", b1: "Связался", b2: "Черновик ответа",
      today: "Сегодня", rep1: "Отчёт за день", rep2: "Визиты 13 · Заявки 0",
    },
  },

  build(svg, { h, wrapText }, t) {
    const uid = "a" + Math.random().toString(36).slice(2, 8);
    const defs = h("defs", {}, svg);
    const g = h("linearGradient", { id: `${uid}g`, x1: 0, y1: 0, x2: 1, y2: 1 }, defs);
    h("stop", { offset: 0, class: "st-tq" }, g);
    h("stop", { offset: 1, class: "st-acc" }, g);
    const clip = h("clipPath", { id: `${uid}c` }, defs);
    h("rect", { x: 12, y: 57, width: 246, height: 145 }, clip);

    // ── Chat window ──
    h("rect", { x: 12, y: 12, width: 246, height: 226, rx: 14, class: "d-card" }, svg);
    h("circle", { cx: 34, cy: 34, r: 11, fill: `url(#${uid}g)` }, svg);
    h("text", { x: 34, y: 38, "font-size": 9.5, fill: "#fff", "text-anchor": "middle", class: "db", text: "AI" }, svg);
    h("text", { x: 52, y: 32, "font-size": 11.5, class: "d-tx db", text: "AI" }, svg);
    h("circle", { cx: 70, cy: 28.5, r: 3, class: "d-ok" }, svg);
    h("text", { x: 52, y: 45, "font-size": 9.5, class: "d-tx3", text: t.sub }, svg);
    h("line", { x1: 12, x2: 258, y1: 56, y2: 56, class: "d-line" }, svg);

    const view = h("g", { "clip-path": `url(#${uid}c)` }, svg);
    const body = h("g", {}, view);

    // Visitor bubble (right)
    const qG = h("g", { opacity: 0 }, body);
    const qRect = h("rect", { x: 92, y: 66, width: 156, height: 40, rx: 12, class: "d-acc" }, qG);
    const qText = h("text", { x: 102, y: 82, "font-size": 11, fill: "#fff" }, qG);
    const qLines = wrapText(qText, t.q, 26, 14);
    qRect.setAttribute("height", qLines * 14 + 12);
    const qBottom = 66 + qLines * 14 + 12;

    // Tool calls
    const tools = ["projects()", "save_lead()"].map((name, i) => {
      const x = 20 + i * 88;
      const gg = h("g", { opacity: 0 }, body);
      h("rect", { x, y: qBottom + 10, width: 84, height: 18, rx: 9, class: "d-card2", style: "stroke: var(--border)" }, gg);
      const mark = h("circle", { cx: x + 10, cy: qBottom + 19, r: 3, class: "d-tx3" }, gg);
      h("text", { x: x + 18, y: qBottom + 22.5, "font-size": 9.5, class: "d-tx2 dm", text: name }, gg);
      return { g: gg, mark };
    });

    // Typing dots
    const dots = h("g", { opacity: 0 }, body);
    h("rect", { x: 22, y: qBottom + 36, width: 44, height: 22, rx: 11, class: "d-card2" }, dots);
    const dotEls = [0, 1, 2].map((i) => h("circle", { cx: 34 + i * 10, cy: qBottom + 47, r: 2.6, class: "d-tx3" }, dots));

    // Assistant bubble (left)
    const aG = h("g", { opacity: 0 }, body);
    const aRect = h("rect", { x: 22, y: qBottom + 36, width: 204, height: 40, rx: 12, class: "d-card2" }, aG);
    const aText = h("text", { x: 32, y: qBottom + 52, "font-size": 11, class: "d-tx" }, aG);
    const aLines = wrapText(aText, t.a, 32, 14);
    aRect.setAttribute("height", aLines * 14 + 12);
    // When the answer does not fit, the chat scrolls up like a real one
    const scroll = Math.max(0, qBottom + 36 + aLines * 14 + 12 - 196);
    const aSpans = [...aText.querySelectorAll("tspan")];
    const aFull = aSpans.map((s) => s.textContent);
    aSpans.forEach((s) => { s.textContent = ""; });

    // Input bar
    h("rect", { x: 20, y: 206, width: 230, height: 24, rx: 12, class: "d-card2" }, svg);
    const input = h("text", { x: 32, y: 222, "font-size": 10.5, class: "d-tx3", text: t.ph }, svg);
    const send = h("circle", { cx: 238, cy: 218, r: 8, fill: `url(#${uid}g)` }, svg);
    h("path", { d: "M234.5 218h7m-3-3 3 3-3 3", stroke: "#fff", "stroke-width": 1.4, fill: "none", "stroke-linecap": "round", "stroke-linejoin": "round" }, svg);

    // ── Owner's Telegram (day theme on light, night theme on dark) ──
    const PX = 268, PW = 120;
    const tclip = h("clipPath", { id: `${uid}t` }, defs);
    h("rect", { x: PX, y: 12, width: PW, height: 226, rx: 16 }, tclip);
    const tg = h("g", { "clip-path": `url(#${uid}t)` }, svg);
    h("rect", { x: PX, y: 12, width: PW, height: 226, fill: "var(--tg-bg)" }, tg);
    h("rect", { x: PX, y: 12, width: PW, height: 28, fill: "var(--tg-head)" }, tg);
    h("line", { x1: PX, x2: PX + PW, y1: 40, y2: 40, stroke: "var(--tg-line)" }, tg);
    h("circle", { cx: PX + 15, cy: 26, r: 8, fill: "var(--tg-avatar)" }, tg);
    h("text", { x: PX + 15, y: 29, "font-size": 7, fill: "#fff", "text-anchor": "middle", class: "db", text: "NX" }, tg);
    h("text", { x: PX + 28, y: 24.5, "font-size": 9, fill: "var(--tg-text)", class: "db", text: "Portfolio bot" }, tg);
    h("text", { x: PX + 28, y: 34, "font-size": 7, fill: "var(--tg-faint)", text: "bot" }, tg);
    const badge = h("g", { opacity: 0 }, tg);
    h("circle", { cx: PX + 106, cy: 26, r: 6.5, fill: "#3fcf8e" }, badge);
    h("text", { x: PX + 106, y: 29, "font-size": 8, fill: "#0e1621", "text-anchor": "middle", class: "db", text: "1" }, badge);

    const chat = h("g", {}, tg);
    // Earlier conversation, so the screen is a real chat, not an empty box
    h("rect", { x: PX + 44, y: 47, width: 32, height: 12, rx: 6, fill: "var(--tg-faint)", opacity: 0.35 }, chat);
    h("text", { x: PX + 60, y: 55.5, "font-size": 6.5, fill: "#fff", "text-anchor": "middle", text: t.today }, chat);
    h("rect", { x: PX + 6, y: 64, width: 96, height: 34, rx: 8, fill: "var(--tg-bubble)" }, chat);
    h("text", { x: PX + 12, y: 76, "font-size": 8, fill: "var(--tg-text)", class: "db", text: t.rep1 }, chat);
    h("text", { x: PX + 12, y: 88, "font-size": 7.5, fill: "var(--tg-soft)", text: t.rep2 }, chat);
    h("text", { x: PX + 98, y: 94.5, "font-size": 5.5, fill: "var(--tg-faint)", "text-anchor": "end", class: "dm", text: "08:30" }, chat);
    h("rect", { x: PX + 62, y: 103, width: 52, height: 18, rx: 8, fill: "var(--tg-me)" }, chat);
    h("text", { x: PX + 68, y: 115, "font-size": 7.5, fill: "var(--tg-me-text)", class: "dm", text: "/leads" }, chat);
    h("text", { x: PX + 110, y: 117.5, "font-size": 5.5, fill: "var(--tg-me-meta)", "text-anchor": "end", class: "dm", text: "✓✓" }, chat);

    const lead = h("g", { opacity: 0 }, chat);
    h("rect", { x: PX + 6, y: 127, width: 104, height: 70, rx: 8, fill: "var(--tg-bubble)" }, lead);
    h("text", { x: PX + 12, y: 140, "font-size": 8.5, fill: "var(--tg-text)", class: "db", text: t.lead }, lead);
    const need = h("text", { x: PX + 12, y: 152, "font-size": 7.5, fill: "var(--tg-soft)" }, lead);
    wrapText(need, t.need, 22, 10);
    h("text", { x: PX + 12, y: 177, "font-size": 7.5, fill: "var(--tg-link)", class: "dm", text: "+998 90 ··· 1234" }, lead);
    h("text", { x: PX + 104, y: 192.5, "font-size": 5.5, fill: "var(--tg-faint)", "text-anchor": "end", class: "dm", text: "12:04" }, lead);
    const btns = [t.b1, t.b2].map((label, i) => {
      const y = 200 + i * 18;
      const gg = h("g", { opacity: 0 }, chat);
      h("rect", { x: PX + 6, y, width: 104, height: 16, rx: 6, fill: "var(--tg-btn)", opacity: 0.92 }, gg);
      h("text", { x: PX + 58, y: y + 11, "font-size": 7.5, fill: "var(--tg-btn-text)", "text-anchor": "middle", class: "db", text: label }, gg);
      return gg;
    });

    return { body, scroll, qG, tools, dots, dotEls, aG, aSpans, aFull, input, send, badge, lead, btns, chat, ph: t.ph };
  },

  async play(api, s, t) {
    api.step(0);
    await api.wait(400);
    s.input.setAttribute("class", "d-tx");
    await api.type(s.input, t.q.length > 30 ? t.q.slice(0, 29) + "…" : t.q, 30);
    await api.tween(s.send, [{ transform: "scale(1)" }, { transform: "scale(0.92)" }, { transform: "scale(1)" }], { dur: 260 });
    s.input.textContent = s.ph;
    s.input.setAttribute("class", "d-tx3");
    await api.show(s.qG, 420, "translateY(10px)");

    api.step(1);
    api.show(s.dots, 250);
    s.dotEls.forEach((d, i) => api.loop(d, [{ opacity: 0.25 }, { opacity: 1 }, { opacity: 0.25 }], { duration: 900, delay: i * 150 }));
    for (const tool of s.tools) {
      await api.show(tool.g, 300, "translateX(-6px)");
      await api.wait(420);
      tool.mark.setAttribute("class", "d-ok");
    }
    await api.wait(250);

    api.step(2);
    await api.hide(s.dots, 160);
    s.aG.style.opacity = "1";
    for (let i = 0; i < s.aSpans.length; i++) {
      if (i === Math.min(2, s.aSpans.length - 1) && s.scroll) api.tween(s.body, [{ transform: "translateY(0px)" }, { transform: `translateY(${-s.scroll}px)` }], { dur: 600 });
      await api.type(s.aSpans[i], s.aFull[i], 46);
    }
    await api.wait(350);

    api.step(3);
    await api.tween(s.badge, [{ opacity: 0 }, { opacity: 1 }], { dur: 220 });
    await api.show(s.lead, 480, "translateY(10px)");
    for (const b of s.btns) await api.show(b, 300, "translateY(6px)");
    api.poster();
    await api.wait(2000);
  },
};
