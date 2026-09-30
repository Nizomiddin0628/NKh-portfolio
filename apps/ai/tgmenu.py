"""Telegram menu and sections for the owner.

Bottom keyboard (always two columns):
    📊 Report      📥 Leads
    ✉️ Messages    📈 Stats
    ⏰ Reminders   🧠 Knowledge
    🌐 Global      ⚙️ Settings
    🆕 New chat    ⬇️ Hide

Each section is one message with inline buttons that edit the same message
(no chat clutter). Buttons pressed by the owner act directly: pressing a
button is itself the confirmation. Free text still goes to the AI.
Callback data: "m:<section>:<args>" (Telegram limit: 64 bytes).
"""
import html

from django.db.models import Sum
from django.utils import timezone

from apps.core.models import ContactMessage, DailyVisitor, PageView

from .models import AiChat, AiKnowledge, Lead, Reminder

e = html.escape

L = {
    "uz": {
        "b_report": "📊 Hisobot", "b_leads": "📥 So'rovlar", "b_msgs": "✉️ Xabarlar", "b_stats": "📈 Statistika",
        "b_rem": "⏰ Eslatmalar", "b_know": "🧠 Bilim", "b_web": "🌐 Global", "b_site": "🏠 Sayt",
        "b_settings": "⚙️ Sozlamalar", "b_new": "🆕 Yangi suhbat", "b_hide": "⬇️ Yig'ish",
        "today": "Bugun", "yesterday": "Kecha", "week": "Hafta", "d7": "7 kun", "d30": "30 kun",
        "back": "⬅️ Orqaga", "refresh": "🔄 Yangilash", "new_only": "Yangilari", "all": "Hammasi",
        "leads_title": "📥 <b>So'rovlar</b>", "no_leads": "So'rovlar yo'q.",
        "contacted": "✅ Bog'landim", "close": "🗂 Yopish", "reopen": "↩️ Qayta ochish", "draft": "✍️ Javob tayyorla",
        "transcript": "📄 Suhbat", "status": {"new": "🆕 yangi", "contacted": "✅ bog'lanildi", "closed": "🗂 yopilgan"},
        "msgs_title": "✉️ <b>O'qilmagan xabarlar</b>", "no_msgs": "O'qilmagan xabar yo'q.",
        "read": "✔ O'qildi", "read_all": "✔ Hammasini o'qildi", "all_read": "Hammasi o'qilgan deb belgilandi.",
        "stats_title": "📈 <b>Statistika</b> · {days} kun", "visitors": "Tashriflar", "views": "Ko'rishlar",
        "top": "Eng ko'p ko'rilgan", "devices": "Qurilmalar", "refs": "Qayerdan", "direct": "to'g'ridan-to'g'ri",
        "rem_title": "⏰ <b>Eslatmalar</b>", "no_rem": "Eslatma yo'q.",
        "rem_hint": "Qo'shish uchun oddiy yozing yoki gapiring: <i>ertaga 10:00 da mijozga qo'ng'iroq qilishni eslat</i>",
        "know_title": "🧠 <b>Assistent biladigan faktlar</b>", "no_know": "Hali fakt yo'q.",
        "know_hint": "Qo'shish: <i>eslab qol: 2025-yildan freelance loyihalar ham olaman</i>",
        "deleted": "O'chirildi.",
        "settings_title": "⚙️ <b>Sozlamalar</b>", "lang": "Til", "mode": "Rejim",
        "mode_local": "🏠 Sayt ma'lumotlari", "mode_web": "🌐 Global (internet)",
        "digest": "Kunlik hisobot 08:30 va 18:00", "on": "🔔 yoqilgan", "off": "🔕 o'chirilgan",
        "toggle_digest": "🔔 Hisobotni yoqish/o'chirish", "toggle_mode": "🌐/🏠 Rejimni almashtirish",
        "draft_q": "#{id} so'rovga {lang_name} tilida qisqa, samimiy javob xatini tayyorla. Mijoz ehtiyojini va mos loyihalarimni hisobga ol. "
                   "Email bo'lsa reply_lead bilan tayyorla, bo'lmasa faqat matnni ber.",
        "draft_msg_q": "#{id} kontakt xabariga javob matnini tayyorla (faqat matn, yuborma).",
        "transcript_title": "📄 <b>#{id} suhbati</b>",
    },
    "ru": {
        "b_report": "📊 Отчёт", "b_leads": "📥 Заявки", "b_msgs": "✉️ Сообщения", "b_stats": "📈 Статистика",
        "b_rem": "⏰ Напоминания", "b_know": "🧠 Знания", "b_web": "🌐 Глобальный", "b_site": "🏠 Сайт",
        "b_settings": "⚙️ Настройки", "b_new": "🆕 Новый диалог", "b_hide": "⬇️ Скрыть",
        "today": "Сегодня", "yesterday": "Вчера", "week": "Неделя", "d7": "7 дней", "d30": "30 дней",
        "back": "⬅️ Назад", "refresh": "🔄 Обновить", "new_only": "Новые", "all": "Все",
        "leads_title": "📥 <b>Заявки</b>", "no_leads": "Заявок нет.",
        "contacted": "✅ Связался", "close": "🗂 Закрыть", "reopen": "↩️ Открыть снова", "draft": "✍️ Черновик ответа",
        "transcript": "📄 Диалог", "status": {"new": "🆕 новая", "contacted": "✅ на связи", "closed": "🗂 закрыта"},
        "msgs_title": "✉️ <b>Непрочитанные сообщения</b>", "no_msgs": "Непрочитанных нет.",
        "read": "✔ Прочитано", "read_all": "✔ Прочитать все", "all_read": "Все отмечены прочитанными.",
        "stats_title": "📈 <b>Статистика</b> · {days} дн.", "visitors": "Посетители", "views": "Просмотры",
        "top": "Популярные страницы", "devices": "Устройства", "refs": "Источники", "direct": "прямые",
        "rem_title": "⏰ <b>Напоминания</b>", "no_rem": "Напоминаний нет.",
        "rem_hint": "Чтобы добавить, напишите или скажите: <i>напомни завтра в 10:00 позвонить клиенту</i>",
        "know_title": "🧠 <b>Факты, которые знает ассистент</b>", "no_know": "Пока нет фактов.",
        "know_hint": "Добавить: <i>запомни: с 2025 года беру и фриланс-проекты</i>",
        "deleted": "Удалено.",
        "settings_title": "⚙️ <b>Настройки</b>", "lang": "Язык", "mode": "Режим",
        "mode_local": "🏠 Данные сайта", "mode_web": "🌐 Глобальный (интернет)",
        "digest": "Ежедневный отчёт 08:30 и 18:00", "on": "🔔 включён", "off": "🔕 выключен",
        "toggle_digest": "🔔 Вкл/выкл отчёт", "toggle_mode": "🌐/🏠 Сменить режим",
        "draft_q": "Подготовь короткий дружелюбный ответ на заявку #{id} на языке: {lang_name}. Учти потребность клиента и мои подходящие проекты. "
                   "Если есть email — подготовь через reply_lead, иначе дай только текст.",
        "draft_msg_q": "Подготовь текст ответа на сообщение #{id} из формы контакта (только текст, не отправляй).",
        "transcript_title": "📄 <b>Диалог заявки #{id}</b>",
    },
    "en": {
        "b_report": "📊 Report", "b_leads": "📥 Leads", "b_msgs": "✉️ Messages", "b_stats": "📈 Stats",
        "b_rem": "⏰ Reminders", "b_know": "🧠 Knowledge", "b_web": "🌐 Global", "b_site": "🏠 Site",
        "b_settings": "⚙️ Settings", "b_new": "🆕 New chat", "b_hide": "⬇️ Hide",
        "today": "Today", "yesterday": "Yesterday", "week": "Week", "d7": "7 days", "d30": "30 days",
        "back": "⬅️ Back", "refresh": "🔄 Refresh", "new_only": "New", "all": "All",
        "leads_title": "📥 <b>Leads</b>", "no_leads": "No leads.",
        "contacted": "✅ Contacted", "close": "🗂 Close", "reopen": "↩️ Reopen", "draft": "✍️ Draft reply",
        "transcript": "📄 Conversation", "status": {"new": "🆕 new", "contacted": "✅ contacted", "closed": "🗂 closed"},
        "msgs_title": "✉️ <b>Unread messages</b>", "no_msgs": "No unread messages.",
        "read": "✔ Read", "read_all": "✔ Mark all read", "all_read": "All marked as read.",
        "stats_title": "📈 <b>Statistics</b> · {days} days", "visitors": "Visitors", "views": "Page views",
        "top": "Top pages", "devices": "Devices", "refs": "Sources", "direct": "direct",
        "rem_title": "⏰ <b>Reminders</b>", "no_rem": "No reminders.",
        "rem_hint": "To add one, just type or say: <i>remind me tomorrow at 10:00 to call the client</i>",
        "know_title": "🧠 <b>Facts the assistant knows</b>", "no_know": "No facts yet.",
        "know_hint": "Add: <i>remember: since 2025 I also take freelance projects</i>",
        "deleted": "Deleted.",
        "settings_title": "⚙️ <b>Settings</b>", "lang": "Language", "mode": "Mode",
        "mode_local": "🏠 Site data", "mode_web": "🌐 Global (web)",
        "digest": "Daily report 08:30 and 18:00", "on": "🔔 on", "off": "🔕 off",
        "toggle_digest": "🔔 Report on/off", "toggle_mode": "🌐/🏠 Switch mode",
        "draft_q": "Draft a short, friendly reply to lead #{id} in {lang_name}. Consider their need and my matching projects. "
                   "If they left an email, prepare it with reply_lead; otherwise give only the text.",
        "draft_msg_q": "Draft a reply to contact message #{id} (text only, do not send).",
        "transcript_title": "📄 <b>Lead #{id} conversation</b>",
    },
}
LANG_NAMES = {"uz": "O'zbekcha", "ru": "Русский", "en": "English"}
LEAD_LANG = {"uz": "Uzbek", "ru": "Russian", "en": "English"}


def tx(lang):
    return L.get(lang) or L["uz"]


# ── Bottom keyboard ─────────────────────────────────────────────────────────

def keyboard(lang, mode="local"):
    x = tx(lang)
    return {"keyboard": [
        [{"text": x["b_report"]}, {"text": x["b_leads"]}],
        [{"text": x["b_msgs"]}, {"text": x["b_stats"]}],
        [{"text": x["b_rem"]}, {"text": x["b_know"]}],
        [{"text": x["b_site"] if mode == "web" else x["b_web"]}, {"text": x["b_settings"]}],
        [{"text": x["b_new"]}, {"text": x["b_hide"]}],
    ], "resize_keyboard": True, "is_persistent": False}


# Label -> action, for every language (so an old keyboard still works after a language switch)
BUTTONS = {}
for _code, _x in L.items():
    for _key in ("b_report", "b_leads", "b_msgs", "b_stats", "b_rem", "b_know", "b_web", "b_site",
                 "b_settings", "b_new", "b_hide"):
        BUTTONS[_x[_key]] = _key[2:]

COMMANDS = {"/report": "report", "/leads": "leads", "/messages": "msgs", "/stats": "stats",
            "/reminders": "rem", "/knowledge": "know", "/web": "web", "/site": "site",
            "/settings": "settings", "/new": "new"}


def btn(text, data):
    return {"text": text, "callback_data": data[:64]}


# ── Sections: each returns (text, inline_keyboard rows) ─────────────────────

def report(lang, period="today"):
    from .digest import build_report
    x = tx(lang)
    text = build_report(period, lang)["text"]
    row = [btn(("• " if p == period else "") + x[p], f"m:rep:{p}") for p in ("today", "yesterday", "week")]
    return text, [row]


def leads(lang, which="open"):
    x = tx(lang)
    qs = Lead.objects.all() if which == "all" else Lead.objects.exclude(status="closed")
    rows = list(qs[:8])
    lines = [x["leads_title"], ""]
    kb = []
    if not rows:
        lines.append(x["no_leads"])
    for ld in rows:
        lines.append(f"<b>#{ld.pk}</b> {e(ld.name or '—')} · {e(ld.contact)} · {x['status'][ld.status]}\n"
                     f"{e(ld.need[:140])}\n<i>{timezone.localtime(ld.created_at):%d.%m %H:%M}</i>\n")
        kb.append([btn(f"#{ld.pk} {(ld.name or ld.contact)[:24]}", f"m:lead:{ld.pk}")])
    kb.append([btn(("• " if which != "all" else "") + x["new_only"], "m:leads:open"),
               btn(("• " if which == "all" else "") + x["all"], "m:leads:all")])
    return "\n".join(lines), kb


def lead_card(lang, pk):
    x = tx(lang)
    ld = Lead.objects.filter(pk=pk).first()
    if ld is None:
        return x["no_leads"], [[btn(x["back"], "m:leads:open")]]
    lines = [f"📥 <b>#{ld.pk} · {e(ld.name or '—')}</b>", e(ld.contact), "", e(ld.need[:1500])]
    extra = [v for v in (ld.timeline, ld.budget) if v]
    if extra:
        lines += ["", " · ".join(e(v) for v in extra)]
    lines += ["", f"{x['status'][ld.status]} · {ld.lang or '-'} · {e(ld.page or '/')} · "
                  f"{timezone.localtime(ld.created_at):%d.%m %H:%M}"]
    if ld.note:
        lines += ["", f"<i>{e(ld.note[-400:])}</i>"]
    status_row = [btn(x["contacted"], f"m:ls:{pk}:contacted"), btn(x["close"], f"m:ls:{pk}:closed")] \
        if ld.status != "closed" else [btn(x["reopen"], f"m:ls:{pk}:new")]
    kb = [status_row, [btn(x["draft"], f"m:ldraft:{pk}"), btn(x["transcript"], f"m:ltr:{pk}")],
          [btn(x["back"], "m:leads:open")]]
    return "\n".join(lines), kb


def lead_transcript(lang, pk):
    x = tx(lang)
    ld = Lead.objects.filter(pk=pk).first()
    body = e((ld.transcript if ld else "")[-3500:]) or "—"
    return f"{x['transcript_title'].format(id=pk)}\n\n{body}", [[btn(x["back"], f"m:lead:{pk}")]]


def messages(lang):
    x = tx(lang)
    rows = list(ContactMessage.objects.filter(is_read=False)[:6])
    lines = [x["msgs_title"], ""]
    kb = []
    if not rows:
        lines.append(x["no_msgs"])
    for m in rows:
        lines.append(f"<b>#{m.pk}</b> {e(m.name)} · {e(m.email)}" + (f" · {e(m.phone)}" if m.phone else "")
                     + f"\n{e((m.subject + ': ') if m.subject else '')}{e(m.message[:220])}\n"
                     f"<i>{timezone.localtime(m.created_at):%d.%m %H:%M}</i>\n")
        kb.append([btn(f"{x['read']} #{m.pk}", f"m:mr:{m.pk}"), btn(f"{x['draft']} #{m.pk}", f"m:mdraft:{m.pk}")])
    if rows:
        kb.append([btn(x["read_all"], "m:mr:all")])
    kb.append([btn(x["refresh"], "m:msgs")])
    return "\n".join(lines), kb


def _bar(n, top, width=12):
    return "▇" * max(1, round(width * n / top)) if top and n else "·"


def stats(lang, days=7):
    x = tx(lang)
    since = timezone.localdate() - timezone.timedelta(days=days - 1)
    vis = DailyVisitor.objects.filter(date__gte=since)
    views = PageView.objects.filter(date__gte=since)
    by_day = {}
    for d in vis.values_list("date", flat=True):
        by_day[d] = by_day.get(d, 0) + 1
    lines = [x["stats_title"].format(days=days), "",
             f"👥 {x['visitors']}: <b>{vis.count()}</b> · {x['views']}: <b>{views.aggregate(n=Sum('count'))['n'] or 0}</b>", ""]
    if days <= 14:
        top = max(by_day.values(), default=0)
        for i in range(days):
            d = since + timezone.timedelta(days=i)
            n = by_day.get(d, 0)
            lines.append(f"<code>{d:%d.%m} {_bar(n, top):<12} {n}</code>")
        lines.append("")
    pages = list(views.values("path").annotate(n=Sum("count")).order_by("-n")[:5])
    if pages:
        lines.append(f"<b>{x['top']}</b>")
        lines += [f"• {e(p['path'])} — {p['n']}" for p in pages]
        lines.append("")
    dev = {}
    for d in vis.values_list("device", flat=True):
        dev[d or "?"] = dev.get(d or "?", 0) + 1
    if dev:
        lines.append(f"<b>{x['devices']}</b>: " + ", ".join(f"{k} {v}" for k, v in sorted(dev.items(), key=lambda i: -i[1])))
    refs = {}
    for r in vis.values_list("referrer", flat=True):
        refs[r or x["direct"]] = refs.get(r or x["direct"], 0) + 1
    if refs:
        lines.append(f"<b>{x['refs']}</b>: " + ", ".join(f"{e(k)} {v}" for k, v in sorted(refs.items(), key=lambda i: -i[1])[:6]))
    kb = [[btn(("• " if days == 7 else "") + x["d7"], "m:st:7"), btn(("• " if days == 30 else "") + x["d30"], "m:st:30")]]
    return "\n".join(lines), kb


def reminders(lang):
    x = tx(lang)
    rows = list(Reminder.objects.filter(sent_at__isnull=True)[:10])
    lines = [x["rem_title"], ""]
    if not rows:
        lines.append(x["no_rem"])
    lines += [f"• {timezone.localtime(r.due_at):%d.%m %H:%M} — {e(r.text)}" for r in rows]
    lines += ["", x["rem_hint"]]
    kb = [[btn(f"🗑 {timezone.localtime(r.due_at):%d.%m %H:%M} {r.text[:20]}", f"m:rdel:{r.pk}")] for r in rows]
    return "\n".join(lines), kb


def knowledge(lang):
    x = tx(lang)
    rows = list(AiKnowledge.objects.filter(is_active=True)[:12])
    lines = [x["know_title"], ""]
    if not rows:
        lines.append(x["no_know"])
    lines += [f"<b>{i}.</b> {e(r.text[:200])}" for i, r in enumerate(rows, 1)]
    lines += ["", x["know_hint"]]
    kb = [[btn(f"🗑 {i}. {r.text[:28]}", f"m:kdel:{r.pk}")] for i, r in enumerate(rows, 1)]
    return "\n".join(lines), kb


def settings_view(chat):
    x = tx(chat.lang)
    lines = [x["settings_title"], "",
             f"{x['lang']}: <b>{LANG_NAMES.get(chat.lang, chat.lang)}</b>",
             f"{x['mode']}: <b>{x['mode_web'] if chat.mode == 'web' else x['mode_local']}</b>",
             f"{x['digest']}: <b>{x['on'] if chat.digest_on else x['off']}</b>"]
    kb = [[btn(("• " if c == chat.lang else "") + name, f"m:lang:{c}") for c, name in LANG_NAMES.items()],
          [btn(x["toggle_mode"], "m:mode")], [btn(x["toggle_digest"], "m:dig")]]
    return "\n".join(lines), kb


SECTIONS = {"report": lambda chat: report(chat.lang), "leads": lambda chat: leads(chat.lang),
            "msgs": lambda chat: messages(chat.lang), "stats": lambda chat: stats(chat.lang),
            "rem": lambda chat: reminders(chat.lang), "know": lambda chat: knowledge(chat.lang),
            "settings": settings_view}


# ── Callbacks ───────────────────────────────────────────────────────────────

def on_callback(chat, data):
    """Returns ("edit", text, kb) | ("send", text, kb) | ("ai", question) | ("keyboard", text) | None."""
    parts = data.split(":")
    what = parts[1] if len(parts) > 1 else ""
    arg = parts[2] if len(parts) > 2 else ""
    x = tx(chat.lang)

    if what == "rep":
        return ("edit", *report(chat.lang, arg or "today"))
    if what == "leads":
        return ("edit", *leads(chat.lang, arg or "open"))
    if what == "lead":
        return ("edit", *lead_card(chat.lang, int(arg)))
    if what == "ltr":
        return ("edit", *lead_transcript(chat.lang, int(arg)))
    if what == "ls":
        status = parts[3] if len(parts) > 3 else ""
        if status in ("new", "contacted", "closed"):
            ld = Lead.objects.filter(pk=int(arg)).first()
            if ld:
                ld.status = status
                ld.note = (ld.note + "\n" if ld.note else "") + f"{timezone.localtime():%d.%m %H:%M} → {status}"
                ld.save(update_fields=["status", "note", "updated_at"])
        return ("edit", *lead_card(chat.lang, int(arg)))
    if what == "ldraft":
        ld = Lead.objects.filter(pk=int(arg)).first()
        lang_name = LEAD_LANG.get(ld.lang if ld else "", "the lead's language")
        return ("ai", x["draft_q"].format(id=arg, lang_name=lang_name))
    if what == "msgs":
        return ("edit", *messages(chat.lang))
    if what == "mr":
        qs = ContactMessage.objects.filter(is_read=False)
        if arg != "all":
            qs = qs.filter(pk=int(arg))
        qs.update(is_read=True)
        return ("edit", *messages(chat.lang))
    if what == "mdraft":
        return ("ai", x["draft_msg_q"].format(id=arg))
    if what == "st":
        return ("edit", *stats(chat.lang, 30 if arg == "30" else 7))
    if what == "rdel":
        Reminder.objects.filter(pk=int(arg), sent_at__isnull=True).delete()
        return ("edit", *reminders(chat.lang))
    if what == "kdel":
        AiKnowledge.objects.filter(pk=int(arg)).update(is_active=False)
        from .state import invalidate
        invalidate()
        return ("edit", *knowledge(chat.lang))
    if what == "lang" and arg in LANG_NAMES:
        chat.lang = arg
        chat.save(update_fields=["lang"])
        return ("keyboard", *settings_view(chat))
    if what == "mode":
        chat.mode = "local" if chat.mode == "web" else "web"
        chat.save(update_fields=["mode"])
        return ("keyboard", *settings_view(chat))
    if what == "dig":
        chat.digest_on = not chat.digest_on
        chat.save(update_fields=["digest_on"])
        return ("edit", *settings_view(chat))
    return None


def owner_digest_on(chat_id):
    chat = AiChat.objects.filter(chat_id=chat_id).first()
    return chat is None or chat.digest_on
