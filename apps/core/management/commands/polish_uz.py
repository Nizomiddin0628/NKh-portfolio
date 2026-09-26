"""Apply the rewritten Uzbek texts, or restore a backup.

    python manage.py polish_uz
    python manage.py polish_uz --restore backups/uz_before_<timestamp>.json

Normally not needed by hand: deploys apply the texts through a data migration.
"""
from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.core.content.uz_texts import apply_texts

DATA = settings.BASE_DIR / "content" / "portfolio" / "uz_texts.json"


class Command(BaseCommand):
    help = "Rewrite Uzbek texts (with automatic backup)."

    def add_arguments(self, parser):
        parser.add_argument("--restore", help="Backup file to restore from.")

    @transaction.atomic
    def handle(self, *args, restore=None, **options):
        changed = apply_texts(apps.get_model, restore or DATA, backup=not restore,
                              log=self.stdout.write)
        self.stdout.write(self.style.SUCCESS(f"Updated {changed} Uzbek text(s)."))
