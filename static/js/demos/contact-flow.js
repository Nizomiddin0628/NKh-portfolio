/* Contact: what happens to a message after "Send". The visitor's form,
   the server log, my phone, and the reply landing back in their inbox. */

const TG = { bg: "var(--tg-bg)", head: "var(--tg-head)", bubble: "var(--tg-bubble)", me: "var(--tg-me)", text: "var(--tg-text)", soft: "var(--tg-soft)", faint: "var(--tg-faint)", link: "var(--tg-link)", meText: "var(--tg-me-text)", meMeta: "var(--tg-me-meta)", avatar: "var(--tg-avatar)" };
const TERM = { bg: "#0b1120", bar: "#141c2e", text: "#c9d4e6", dim: "#5d6b86", ok: "#3fcf8e", key: "#7fb6e8" };

export default {
  duration: 10100,
  rest: 1800,
  i18n: {
    en: {
      steps: [
        "You write what you are building",
        "The server saves it and filters spam",
        "It reaches my Telegram at once",
        "You get a personal reply within one working day",
      ],
      name: "Name", msg: "Message", send: "Send", sent: "Sent",
      text: "We need a Telegram bot that books clinic appointments. Can you help?",
      fresh: "New message", inbox: "Inbox", re: "Re: clinic booking bot", reply: "Hi Aziz — yes. Let's talk tomorrow at 11:00?",
      replied: "Replied",
    },
    uz: {
      steps: [
        "Nima qurmoqchi ekaningizni yozasiz",
        "Server xabarni saqlaydi va spamdan tekshiradi",
        "Xabar shu zahoti Telegram'imga tushadi",
        "Bir ish kuni ichida shaxsan javob olasiz",
      ],
      name: "Ism", msg: "Xabar", send: "Yuborish", sent: "Yuborildi",
      text: "Klinikamiz uchun navbatga yozadigan Telegram bot kerak. Yordam bera olasizmi?",
      fresh: "Yangi xabar", inbox: "Pochta", re: "Re: klinika uchun bot", reply: "Salom, Aziz — ha. Ertaga 11:00 da gaplashamizmi?",
      replied: "Javob berildi",
    },
    ru: {
      steps: [
        "Вы пишете, что хотите построить",
        "Сервер сохраняет сообщение и отсекает спам",
        "Оно сразу приходит мне в Telegram",
        "В течение рабочего дня — личный ответ",
      ],
      name: "Имя", msg: "Сообщение", send: "Отправить", sent: "Отправлено",
      text: "Нужен Telegram-бот для записи в клинику. Сможете помочь?",
      fresh: "Новое сообщение", inbox: "Почта", re: "Re: бот для клиники", reply: "Здравствуйте, Азиз — да. Созвонимся завтра в 11:00?",
      replied: "Ответ отправлен",
    },
  },

  build(svg, { h, wrapText }, t) {
    // Wires between the three panels
    const wires = [
      h("path", { d: "M132 196 C150 196 148 64 166 64", class: "d-line", fill: "none", opacity: 0.6 }, svg),
      h("path", { d: "M266 92 C280 92 278 64 292 64", class: "d-line", fill: "none", opacity: 0.6 }, svg),
      h("path", { d: "M292 200 C250 236 120 240 80 226", class: "d-line", fill: "none", opacity: 0, "stroke-dasharray": "3 4" }, svg),
    ];
    const packet = h("circle", { r: 3, class: "d-tq", opacity: 0 }, svg);

    // ── Visitor: browser with the contact form ──
    h("rect", { x: 10, y: 12, width: 132, height: 226, rx: 10, class: "d-card" }, svg);
    h("rect", { x: 10, y: 12, width: 132, height: 22, rx: 10, class: "d-card2" }, svg);
    h("rect", { x: 10, y: 26, width: 132, height: 8, class: "d-card2" }, svg);
    h("path", { d: "M20 22.5h3.5v-2a1.75 1.75 0 0 1 3.5 0v2h0", class: "s-tx3", fill: "none", "stroke-width": 1 }, svg);
    h("text", { x: 31, y: 26, "font-size": 8.5, class: "d-tx3 dm", text: "khalilovn.uz/contact" }, svg);

    const form = h("g", {}, svg);
    h("text", { x: 20, y: 52, "font-size": 8.5, class: "d-tx3", text: t.name }, form);
    h("rect", { x: 20, y: 57, width: 112, height: 20, rx: 5, class: "d-card2", style: "stroke: var(--border)" }, form);
    const name = h("text", { x: 27, y: 70.5, "font-size": 9.5, class: "d-tx" }, form);
    h("text", { x: 20, y: 94, "font-size": 8.5, class: "d-tx3", text: t.msg }, form);
    h("rect", { x: 20, y: 99, width: 112, height: 78, rx: 5, class: "d-card2", style: "stroke: var(--border)" }, form);
    const body = h("text", { x: 27, y: 113, "font-size": 9, class: "d-tx" }, form);
    wrapText(body, t.text, 21, 12);
    const bodySpans = [...body.querySelectorAll("tspan")];
    const bodyFull = bodySpans.map((s) => s.textContent);
    bodySpans.forEach((s) => { s.textContent = ""; });
    const caret = h("rect", { x: 27, y: 105, width: 1, height: 10, class: "d-acc" }, form);
    const btn = h("g", {}, form);
    const btnBg = h("rect", { x: 20, y: 186, width: 112, height: 22, rx: 6, class: "d-acc" }, btn);
    const btnText = h("text", { x: 76, y: 200.5, "font-size": 9.5, fill: "#fff", "text-anchor": "middle", class: "db", text: t.send }, btn);

    // Inbox view that replaces the form at the end
    const inbox = h("g", { opacity: 0 }, svg);
    h("text", { x: 20, y: 52, "font-size": 9, class: "d-tx3 dm", text: t.inbox.toUpperCase() }, inbox);
    h("rect", { x: 18, y: 60, width: 116, height: 70, rx: 7, class: "d-card2" }, inbox);
    h("circle", { cx: 32, cy: 76, r: 8, class: "d-acc" }, inbox);
    h("text", { x: 32, y: 79, "font-size": 7.5, fill: "#fff", "text-anchor": "middle", class: "db", text: "NX" }, inbox);
    h("text", { x: 45, y: 74, "font-size": 9, class: "d-tx db", text: "Nizomiddin" }, inbox);
    h("text", { x: 45, y: 85, "font-size": 8, class: "d-tx3", text: "+2 h" }, inbox);
    const reTxt = h("text", { x: 26, y: 102, "font-size": 8.5, class: "d-tx2" }, inbox);
    wrapText(reTxt, t.re, 24, 11);
    const replyTxt = h("text", { x: 26, y: 145, "font-size": 9, class: "d-tx" }, inbox);
    wrapText(replyTxt, t.reply, 22, 12);

    // ── Server log ──
    h("rect", { x: 152, y: 34, width: 114, height: 172, rx: 9, fill: TERM.bg }, svg);
    h("rect", { x: 152, y: 34, width: 114, height: 18, rx: 9, fill: TERM.bar }, svg);
    h("rect", { x: 152, y: 44, width: 114, height: 8, fill: TERM.bar }, svg);
    [0, 1, 2].forEach((i) => h("circle", { cx: 162 + i * 8, cy: 43, r: 2.4, fill: ["#ff5f57", "#febc2e", "#28c840"][i], opacity: 0.8 }, svg));
    h("text", { x: 190, y: 46, "font-size": 7.5, fill: TERM.dim, class: "dm", text: "server.log" }, svg);
    const logs = [
      [["POST ", TERM.key], ["/contact 302", TERM.text]],
      [["honeypot ", TERM.dim], ["✓", TERM.ok]],
      [["rate limit ", TERM.dim], ["✓", TERM.ok]],
      [["saved ", TERM.dim], ["#482", TERM.text]],
      [["telegram ", TERM.dim], ["200", TERM.ok]],
      [["email ", TERM.dim], ["250 OK", TERM.ok]],
    ].map((parts, i) => {
      const line = h("text", { x: 160, y: 70 + i * 17, "font-size": 9, class: "dm", opacity: 0 }, svg);
      parts.forEach(([txt, color]) => h("tspan", { fill: color, text: txt }, line));
      return line;
    });

    // ── My phone ──
    h("rect", { x: 276, y: 12, width: 114, height: 226, rx: 16, fill: TG.bg }, svg);
    h("path", { d: "M276 42V28q0-16 16-16h82q16 0 16 16v14z", fill: TG.head }, svg);
    h("circle", { cx: 292, cy: 30, r: 7, fill: TG.avatar }, svg);
    h("text", { x: 303, y: 28, "font-size": 9, fill: TG.text, class: "db", text: "Portfolio bot" }, svg);
    h("text", { x: 303, y: 38, "font-size": 7.5, fill: TG.faint, text: "bot" }, svg);
    const note = h("g", { opacity: 0 }, svg);
    h("rect", { x: 284, y: 52, width: 98, height: 96, rx: 9, fill: TG.bubble }, note);
    h("text", { x: 292, y: 68, "font-size": 9, fill: TG.text, class: "db", text: t.fresh }, note);
    h("text", { x: 292, y: 82, "font-size": 8.5, fill: TG.link, text: "Aziz Karimov" }, note);
    const prev = h("text", { x: 292, y: 97, "font-size": 8.5, fill: TG.soft }, note);
    wrapText(prev, t.text, 18, 11);
    [...prev.querySelectorAll("tspan")].slice(3).forEach((s) => s.remove());
    h("text", { x: 374, y: 143, "font-size": 7, fill: TG.faint, "text-anchor": "end", class: "dm", text: "10:42" }, note);
    const mine = h("g", { opacity: 0 }, svg);
    h("rect", { x: 300, y: 158, width: 82, height: 50, rx: 9, fill: TG.me }, mine);
    const mineTxt = h("text", { x: 307, y: 172, "font-size": 8.5, fill: TG.meText }, mine);
    wrapText(mineTxt, t.reply, 15, 11);
    [...mineTxt.querySelectorAll("tspan")].slice(3).forEach((s) => s.remove());
    h("text", { x: 376, y: 204, "font-size": 7, fill: TG.meMeta, "text-anchor": "end", class: "dm", text: "12:15 ✓✓" }, mine);
    const replied = h("text", { x: 333, y: 226, "font-size": 8.5, fill: "#3fcf8e", "text-anchor": "middle", opacity: 0, text: `✓ ${t.replied}` }, svg);

    return { wires, packet, form, name, bodySpans, bodyFull, caret, btn, btnBg, btnText, inbox, logs, note, mine, replied };
  },

  async play(api, s, t) {
    const travel = async (wire, dur = 650) => {
      const len = wire.getTotalLength();
      s.packet.style.opacity = "1";
      await api.tick(dur, (p) => {
        const pt = wire.getPointAtLength(p * len);
        s.packet.setAttribute("cx", pt.x.toFixed(1));
        s.packet.setAttribute("cy", pt.y.toFixed(1));
      }, "inOut");
      s.packet.style.opacity = "0";
    };
    const caretAt = (el) => {
      try {
        const b = el.getBBox();
        s.caret.setAttribute("x", (b.x + b.width + 1).toFixed(1));
        s.caret.setAttribute("y", (b.y + 1).toFixed(1));
      } catch { /* not rendered yet */ }
    };
    const blink = api.loop(s.caret, [{ opacity: 1 }, { opacity: 0 }], { duration: 900, easing: "steps(1)" });

    api.step(0);
    await api.wait(300);
    await api.tick(500, (p) => { s.name.textContent = "Aziz Karimov".slice(0, Math.round(p * 12)); caretAt(s.name); });
    for (let i = 0; i < s.bodySpans.length; i++) {
      const full = s.bodyFull[i];
      await api.tick((full.length / 34) * 1000, (p) => {
        s.bodySpans[i].textContent = full.slice(0, Math.round(p * full.length));
        caretAt(s.bodySpans[i]);
      });
    }
    await api.wait(250);
    api.unloop(blink);
    s.caret.style.opacity = "0";
    await api.tween(s.btn, [{ transform: "scale(1)" }, { transform: "scale(0.97)" }, { transform: "scale(1)" }], { dur: 220 });
    s.btnBg.setAttribute("class", "d-ok");
    s.btnText.textContent = `✓ ${t.sent}`;

    api.step(1);
    await travel(s.wires[0]);
    for (const l of s.logs.slice(0, 4)) { await api.show(l, 200, "translateX(-4px)"); await api.wait(120); }

    api.step(2);
    await travel(s.wires[1], 500);
    api.show(s.logs[4], 200, "translateX(-4px)");
    await api.show(s.note, 380, "translateY(6px)");
    api.show(s.logs[5], 200, "translateX(-4px)");
    await api.wait(900);
    api.poster();

    api.step(3);
    await api.show(s.mine, 380, "translateY(6px)");
    s.wires[2].style.opacity = "0.6";
    await travel(s.wires[2], 800);
    await api.hide(s.form, 260);
    await api.show(s.inbox, 420, "translateY(6px)");
    await api.show(s.replied, 300);
    await api.wait(1500);
  },
};
