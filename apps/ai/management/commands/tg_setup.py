"""Point the Telegram bot's webhook at this site and register the commands.

    python manage.py tg_setup                       # uses https://khalilovn.uz
    python manage.py tg_setup --url https://x.y.z   # another base URL

Safe to run again (setWebhook is idempotent). deploy.sh runs it on every deploy.
"""
from django.core.management.base import BaseCommand

from apps.ai import telegram


class Command(BaseCommand):
    help = "Register the Telegram webhook and bot commands."

    def add_arguments(self, parser):
        parser.add_argument("--url", default="https://khalilovn.uz")

    def handle(self, *args, **options):
        self.stdout.write(telegram.setup(options["url"]))
