"""Scheduled work: due reminders and the 08:30 / 18:00 digest.

Run every 15 minutes from a systemd timer (deploy/portfolio-ai-tick.timer):
    python manage.py ai_tick
    python manage.py ai_tick --digest morning|evening   # send now, for testing
"""
from django.core.management.base import BaseCommand

from apps.ai.digest import tick


class Command(BaseCommand):
    help = "Send due reminders and the scheduled digest."

    def add_arguments(self, parser):
        parser.add_argument("--digest", choices=["morning", "evening"], help="Force a digest now.")

    def handle(self, *args, **options):
        done = tick(force=options.get("digest"))
        self.stdout.write(f"reminders sent: {done['reminders']}, digest: {done['digest'] or '-'}")
