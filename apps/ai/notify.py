"""Owner notifications from the assistant (Telegram, via the existing bot)."""
import html
import logging
import threading

from django.conf import settings
from django.urls import reverse

from apps.core.notify import telegram_send

logger = logging.getLogger(__name__)


def owner_chat_id():
    return (getattr(settings, "AI_OWNER_TELEGRAM_ID", "") or getattr(settings, "TELEGRAM_CHAT_ID", "") or "").strip()


def admin_url(route, *args):
    try:
        return "https://khalilovn.uz" + reverse(route, args=args)
    except Exception:
        return ""


def lead_text(lead):
    e = html.escape
    lines = ["<b>\U0001f195 Yangi so'rov — AI assistent</b>", ""]
    if lead.name:
        lines.append(f"<b>{e(lead.name)}</b>")
    lines.append(e(lead.contact))
    lines += ["", e(lead.need[:1500])]
    extra = []
    if lead.timeline:
        extra.append(f"Muddat: {e(lead.timeline)}")
    if lead.budget:
        extra.append(f"Byudjet: {e(lead.budget)}")
    if extra:
        lines += ["", " · ".join(extra)]
    lines += ["", f"Til: {lead.lang or '-'} · Sahifa: {e(lead.page or '/')}"]
    url = admin_url("admin:ai_lead_change", lead.pk)
    if url:
        lines.append(f'<a href="{e(url)}">Admin</a>')
    return "\n".join(lines)


def lead_buttons(lead):
    """Inline buttons under the new-lead message; handled by apps/ai/tgmenu.py."""
    return {"inline_keyboard": [
        [{"text": "\u2705 Bog'landim", "callback_data": f"m:ls:{lead.pk}:contacted"},
         {"text": "\u270d\ufe0f Javob tayyorla", "callback_data": f"m:ldraft:{lead.pk}"}],
        [{"text": "\U0001f4c4 Suhbat", "callback_data": f"m:ltr:{lead.pk}"},
         {"text": "\U0001f4e5 Barcha so'rovlar", "callback_data": "m:leads:open"}],
    ]}


def _send_lead(text, chat, markup):
    from . import telegram
    if telegram.call("sendMessage", chat_id=chat, text=text, parse_mode="HTML",
                     disable_web_page_preview=True, reply_markup=markup) is None:
        telegram_send(text, chat)  # fallback without buttons


def lead_created(lead):
    chat = owner_chat_id()
    if not chat:
        return
    args = (lead_text(lead), chat, lead_buttons(lead))
    if getattr(settings, "AI_RUN_ASYNC", True):
        threading.Thread(target=_send_lead, args=args, daemon=True).start()
    else:
        _send_lead(*args)


def owner_message(text):
    chat = owner_chat_id()
    return telegram_send(text, chat) if chat else False
