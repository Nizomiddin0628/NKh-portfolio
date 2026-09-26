"""New contact message -> email and Telegram.

Both channels are optional and configured in .env:
    EMAIL_HOST + EMAIL_HOST_PASSWORD        -> email via SMTP
    TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID   -> Telegram bot message

Delivery runs in a background thread with short timeouts, so a slow SMTP
server or a Telegram outage never delays the visitor. The message is saved
to the database before this runs, so nothing is lost if a channel fails.
"""
import html
import json
import logging
import threading
import urllib.request

from django.conf import settings
from django.core.mail import EmailMessage

logger = logging.getLogger(__name__)


def telegram_send(text, chat_id=None):
    token = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
    chat = chat_id or getattr(settings, "TELEGRAM_CHAT_ID", "")
    if not token or not chat:
        return False
    payload = json.dumps({
        "chat_id": chat, "text": text, "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }).encode()
    request = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            return response.status == 200
    except Exception as exc:
        logger.warning("Telegram notification failed: %s", exc)
        return False


def email_send(subject, body, reply_to=None):
    to = getattr(settings, "CONTACT_NOTIFY_EMAIL", "")
    if not to or "smtp" not in settings.EMAIL_BACKEND:
        return False
    try:
        EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, [to],
                     reply_to=[reply_to] if reply_to else None).send()
        return True
    except Exception as exc:
        logger.warning("Email notification failed: %s", exc)
        return False


def _deliver(msg, admin_url):
    e = html.escape
    subject = msg.subject or "No subject"

    lines = ["<b>New message from the portfolio</b>", "",
             f"<b>{e(msg.name)}</b>", e(msg.email)]
    if msg.phone:
        lines.append(e(msg.phone))           # Telegram makes numbers tappable
    lines += [f"Subject: {e(subject)}", "", e(msg.message[:3000]), ""]
    if admin_url:
        lines.append(f'<a href="{e(admin_url)}">Open in admin</a>')
    telegram_send("\n".join(lines))

    body = [f"From: {msg.name} <{msg.email}>"]
    if msg.phone:
        body.append(f"Phone: {msg.phone}")
    body += [f"Language: {msg.language}", "", msg.message, "", "---",
             f"Admin: {admin_url}", "Reply to this email to answer the sender directly."]
    email_send(f"[Portfolio] {subject} - {msg.name}", "\n".join(body), reply_to=msg.email)


def notify_new_message(msg, admin_url=""):
    threading.Thread(target=_deliver, args=(msg, admin_url), daemon=True).start()
