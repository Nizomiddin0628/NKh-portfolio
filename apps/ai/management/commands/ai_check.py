"""Check the assistant setup: key, models, Telegram, limits.

    python manage.py ai_check            # prints the state, sends one tiny request
    python manage.py ai_check --models   # also lists the models the key can use
"""
from django.conf import settings
from django.core.management.base import BaseCommand

from apps.ai import gemini, telegram
from apps.ai.gemini import AiError


class Command(BaseCommand):
    help = "Check the AI assistant configuration."

    def add_arguments(self, parser):
        parser.add_argument("--models", action="store_true", help="List available Gemini models.")

    def handle(self, *args, **options):
        out = self.stdout.write
        ok, warn = self.style.SUCCESS, self.style.WARNING
        out(f"GEMINI_API_KEY:           {ok('set') if gemini.enabled() else warn('missing (.env)')}")
        out(f"GEMINI_MODELS:            {', '.join(gemini.models())}")
        out(f"TELEGRAM_BOT_TOKEN:       {ok('set') if telegram.token() else warn('missing')}")
        out(f"AI owner Telegram id:     {ok(str(telegram.owner_id())) if telegram.owner_id() else warn('missing (AI_OWNER_TELEGRAM_ID or TELEGRAM_CHAT_ID)')}")
        out(f"TELEGRAM_WEBHOOK_SECRET:  {ok('set') if getattr(settings, 'TELEGRAM_WEBHOOK_SECRET', '') else warn('missing (webhook off)')}")
        out(f"Guest limits:             {settings.AI_GUEST_HOURLY}/hour, {settings.AI_GUEST_DAILY}/day, "
            f"{settings.AI_DAILY_LIMIT}/day for all guests")
        if not gemini.enabled():
            return
        if options["models"]:
            try:
                names = gemini.list_models()
                out("Models available to this key:")
                for n in names:
                    out(f"  - {n}")
            except AiError as exc:
                out(warn(f"Could not list models: {exc.code}"))
        try:
            model, ms = gemini.ping()
            out(ok(f"Gemini answers: {model} in {ms} ms"))
        except AiError as exc:
            out(self.style.ERROR(f"Gemini request failed: {exc.code} {exc.detail}"))
