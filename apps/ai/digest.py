"""Reports and the scheduled tick.

`build_report(period)` returns numbers + a ready HTML text (owner's language).
`tick()` runs every 15 minutes from a systemd timer (manage.py ai_tick):
sends due reminders, and the digest at 08:30 and 18:00 local time once each.
"""
import html
import logging

from django.conf import settings
from django.db.models import Sum
from django.utils import timezone

from apps.core.models import ContactMessage, DailyVisitor, PageView

from .actions import pending
from .models import AiLog, Lead, Reminder
from .notify import owner_message

logger = logging.getLogger(__name__)
DIGEST_TIMES = ((8, 30), (18, 0))
WINDOW_MINUTES = 20

T = {
    "uz": {
        "title": {"today": "Bugungi hisobot", "yesterday": "Kechagi hisobot", "week": "Haftalik hisobot"},
        "visitors": "Tashriflar", "views": "Sahifa ko'rishlari", "top": "Eng ko'p ko'rilgan",
        "leads": "Yangi so'rovlar", "messages": "Xabarlar", "unread": "o'qilmagan", "ai": "AI savollari",
        "unanswered": "javobsiz", "pending": "Tasdiq kutayotgan amallar", "reminders": "Bugungi eslatmalar",
        "none": "yo'q", "morning": "Xayrli tong! Bugun uchun:", "evening": "Kun yakuni:",
        "unanswered_list": "Assistent javob bera olmagan savollar",
    },
    "ru": {
        "title": {"today": "Отчёт за сегодня", "yesterday": "Отчёт за вчера", "week": "Отчёт за неделю"},
        "visitors": "Посетители", "views": "Просмотры страниц", "top": "Самые просматриваемые",
        "leads": "Новые заявки", "messages": "Сообщения", "unread": "непрочитанных", "ai": "Вопросы к AI",
        "unanswered": "без ответа", "pending": "Действия, ждущие подтверждения", "reminders": "Напоминания на сегодня",
        "none": "нет", "morning": "Доброе утро! На сегодня:", "evening": "Итоги дня:",
        "unanswered_list": "Вопросы, на которые ассистент не смог ответить",
    },
    "en": {
        "title": {"today": "Today's report", "yesterday": "Yesterday's report", "week": "Weekly report"},
        "visitors": "Visitors", "views": "Page views", "top": "Most viewed",
        "leads": "New leads", "messages": "Messages", "unread": "unread", "ai": "AI questions",
        "unanswered": "unanswered", "pending": "Actions waiting for confirmation", "reminders": "Reminders today",
        "none": "none", "morning": "Good morning! For today:", "evening": "End of day:",
        "unanswered_list": "Questions the assistant could not answer",
    },
}


def owner_lang():
    return getattr(settings, "AI_OWNER_LANG", "uz")


def build_report(period="today", lang=None):
    lang = lang or owner_lang()
    t = T.get(lang, T["en"])
    today = timezone.localdate()
    if period == "yesterday":
        start, end = today - timezone.timedelta(days=1), today - timezone.timedelta(days=1)
    elif period == "week":
        start, end = today - timezone.timedelta(days=6), today
    else:
        period, start, end = "today", today, today
    tz = timezone.get_current_timezone()
    start_dt = timezone.make_aware(timezone.datetime.combine(start, timezone.datetime.min.time()), tz)
    end_dt = timezone.make_aware(timezone.datetime.combine(end + timezone.timedelta(days=1),
                                                          timezone.datetime.min.time()), tz)

    visitors = DailyVisitor.objects.filter(date__gte=start, date__lte=end).count()
    views_qs = PageView.objects.filter(date__gte=start, date__lte=end)
    views = views_qs.aggregate(n=Sum("count"))["n"] or 0
    top = list(views_qs.values("path").annotate(n=Sum("count")).order_by("-n")[:5])
    leads = list(Lead.objects.filter(created_at__gte=start_dt, created_at__lt=end_dt))
    msgs = ContactMessage.objects.filter(created_at__gte=start_dt, created_at__lt=end_dt).count()
    unread = ContactMessage.objects.filter(is_read=False).count()
    ai_qs = AiLog.objects.filter(created_at__gte=start_dt, created_at__lt=end_dt, role="guest",
                                 kind__in=("ask", "voice", "file"))
    ai_n = ai_qs.count()
    unanswered = list(ai_qs.filter(unanswered=True).values_list("question", flat=True)[:5])
    acts = pending()
    today_end = timezone.make_aware(timezone.datetime.combine(today + timezone.timedelta(days=1),
                                                             timezone.datetime.min.time()), tz)
    rems = list(Reminder.objects.filter(sent_at__isnull=True, due_at__lt=today_end)[:10])

    e = html.escape
    lines = [f"<b>{t['title'][period]}</b> · {start:%d.%m}" + (f"–{end:%d.%m}" if start != end else ""), ""]
    lines.append(f"\U0001f465 {t['visitors']}: <b>{visitors}</b> · {t['views']}: <b>{views}</b>")
    if top:
        lines.append(f"\U0001f4c8 {t['top']}: " + ", ".join(f"{e(x['path'])} ({x['n']})" for x in top))
    lines.append(f"\U0001f195 {t['leads']}: <b>{len(leads)}</b>")
    for ld in leads[:5]:
        lines.append(f"   • {e(ld.name or '-')} — {e(ld.contact)} — {e(ld.need[:80])}")
    lines.append(f"✉️ {t['messages']}: <b>{msgs}</b> ({unread} {t['unread']})")
    lines.append(f"\U0001f916 {t['ai']}: <b>{ai_n}</b> ({len(unanswered)} {t['unanswered']})")
    if unanswered:
        lines.append(f"   {t['unanswered_list']}:")
        for q in unanswered:
            lines.append(f"   • {e(q[:100])}")
    if acts:
        lines.append(f"⏳ {t['pending']}: {len(acts)}")
        for a in acts[:5]:
            lines.append(f"   • #{a.pk} {e(a.summary[:90])}")
    if rems:
        lines.append(f"⏰ {t['reminders']}:")
        for r in rems:
            lines.append(f"   • {timezone.localtime(r.due_at):%H:%M} {e(r.text)}")
    text = "\n".join(lines)
    return {"period": period, "from": str(start), "to": str(end), "visitors": visitors, "page_views": views,
            "top_pages": top, "leads": [{"id": ld.pk, "name": ld.name, "contact": ld.contact, "need": ld.need[:200]}
                                        for ld in leads],
            "messages": msgs, "unread_messages": unread, "ai_questions": ai_n, "unanswered": unanswered,
            "pending_actions": [{"id": a.pk, "summary": a.summary} for a in acts],
            "reminders": [{"id": r.pk, "due": str(timezone.localtime(r.due_at))[:16], "text": r.text} for r in rems],
            "text": text}


def send_digest(slot="morning"):
    from .models import AiChat
    from .notify import owner_chat_id
    chat_id = owner_chat_id()
    chat = AiChat.objects.filter(chat_id=int(chat_id)).first() if chat_id.lstrip("-").isdigit() else None
    if chat is not None and not chat.digest_on:
        return True  # switched off in Telegram settings; counts as handled
    lang = chat.lang if chat else owner_lang()
    t = T.get(lang, T["en"])
    period = "yesterday" if slot == "morning" else "today"
    rep = build_report(period, lang)
    head = t["morning"] if slot == "morning" else t["evening"]
    ok = owner_message(f"{head}\n\n{rep['text']}")
    AiLog.objects.create(channel="system", role="owner", kind="digest", question=slot,
                         answer=rep["text"][:4000], ok=bool(ok), model="-")
    return ok


def _digest_sent_today(slot):
    start = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
    return AiLog.objects.filter(kind="digest", question=slot, created_at__gte=start, ok=True).exists()


def send_due_reminders():
    now = timezone.now()
    sent = 0
    for r in Reminder.objects.filter(sent_at__isnull=True, due_at__lte=now)[:20]:
        if owner_message(f"⏰ <b>{html.escape(r.text)}</b>"):
            r.sent_at = now
            r.save(update_fields=["sent_at"])
            sent += 1
    return sent


def tick(force=None):
    """Called every 15 minutes. Returns what it did."""
    done = {"reminders": send_due_reminders(), "digest": None}
    now = timezone.localtime()
    minutes = now.hour * 60 + now.minute
    for i, (h, m) in enumerate(DIGEST_TIMES):
        slot = "morning" if i == 0 else "evening"
        target = h * 60 + m
        if force == slot or (target <= minutes < target + WINDOW_MINUTES and not _digest_sent_today(slot)):
            done["digest"] = slot if send_digest(slot) else f"{slot}:failed"
    if getattr(settings, "AI_LOG_RETENTION_DAYS", 90):
        cutoff = timezone.now() - timezone.timedelta(days=int(settings.AI_LOG_RETENTION_DAYS))
        AiLog.objects.filter(created_at__lt=cutoff).delete()
    return done
