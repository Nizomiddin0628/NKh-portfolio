"""Run the Telegram bot from this computer, without a webhook (for local testing).

    python manage.py tg_poll

Telegram delivers updates either to a webhook or to getUpdates, not both.
If the live site already has its webhook set, this command refuses to start,
because taking the updates here would silence the bot on the server.
Stop with Ctrl+C.
"""
import time

from django.core.management.base import BaseCommand, CommandError

from apps.ai import telegram


class Command(BaseCommand):
    help = "Poll Telegram for updates and answer them locally (testing without a webhook)."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true",
                            help="Remove the live webhook first (the server bot stops until the next deploy).")

    def handle(self, *args, **options):
        if not telegram.token():
            raise CommandError("TELEGRAM_BOT_TOKEN is empty in .env")
        info = telegram.call("getWebhookInfo") or {}
        if info.get("url"):
            if not options["force"]:
                raise CommandError(
                    f"The bot already has a webhook: {info['url']}\n"
                    "The live site answers it. Test in Telegram directly, or run with --force "
                    "(then run `manage.py tg_setup` on the server to give the bot back).")
            telegram.call("deleteWebhook")
        telegram.call("setMyCommands", commands=telegram.COMMAND_LIST)
        telegram.call("setChatMenuButton", menu_button={"type": "commands"})
        me = telegram.call("getMe") or {}
        self.stdout.write(self.style.SUCCESS(f"Polling as @{me.get('username', '?')} - write to the bot. Ctrl+C to stop."))

        offset = None
        while True:
            try:
                payload = {"timeout": 25, "allowed_updates": ["message", "edited_message", "callback_query"]}
                if offset is not None:
                    payload["offset"] = offset
                updates = telegram.call("getUpdates", _timeout=35, **payload)
                if updates is None:
                    time.sleep(2)
                    continue
                for upd in updates:
                    offset = upd["update_id"] + 1
                    kind = "button" if "callback_query" in upd else "message"
                    self.stdout.write(f"  <- {kind}")
                    try:
                        telegram.process_update(upd)
                    except Exception as exc:  # keep polling whatever happens
                        self.stderr.write(f"  ! {type(exc).__name__}: {exc}")
            except KeyboardInterrupt:
                self.stdout.write("Stopped.")
                return
