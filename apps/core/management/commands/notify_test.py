"""Check notification channels.

    python manage.py notify_test

If TELEGRAM_BOT_TOKEN is set but TELEGRAM_CHAT_ID is empty, this prints
the chat id of everyone who has written to your bot, so you can copy yours.
"""
import json
import urllib.request

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.core.notify import email_send, telegram_send


class Command(BaseCommand):
    help = "Send a test notification and help find your Telegram chat id."

    def handle(self, *args, **options):
        token = settings.TELEGRAM_BOT_TOKEN

        if token and not settings.TELEGRAM_CHAT_ID:
            url = f"https://api.telegram.org/bot{token}/getUpdates"
            with urllib.request.urlopen(url, timeout=10) as response:
                updates = json.load(response).get("result", [])
            chats = {}
            for update in updates:
                chat = (update.get("message") or {}).get("chat") or {}
                if chat.get("id"):
                    chats[chat["id"]] = chat.get("username") or chat.get("first_name", "")
            if not chats:
                self.stdout.write(self.style.WARNING(
                    "No messages found. Open your bot in Telegram, press Start, "
                    "send any text, then run this command again."))
                return
            self.stdout.write("Put this into .env as TELEGRAM_CHAT_ID:")
            for chat_id, name in chats.items():
                self.stdout.write(f"  {chat_id}   ({name})")
            return

        tg = telegram_send("<b>Test</b>\nPortfolio notifications work.")
        mail = email_send("[Portfolio] Test notification",
                          "If you can read this, email notifications work.")
        self.stdout.write(("OK    " if tg else "SKIP  ") + "Telegram")
        self.stdout.write(("OK    " if mail else "SKIP  ") + "Email")
        if not tg:
            self.stdout.write("  -> set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env")
        if not mail:
            self.stdout.write("  -> set EMAIL_HOST_PASSWORD (Gmail app password) in .env")
