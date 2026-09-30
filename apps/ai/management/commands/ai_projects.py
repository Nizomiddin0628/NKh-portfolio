"""Re-apply the texts of the two AI project pages from apps/ai/content/projects.py.

    python manage.py ai_projects

Sections and metrics are rewritten; images uploaded in the admin are kept.
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.ai.content.projects import apply


class Command(BaseCommand):
    help = "Create or update the AI project pages."

    @transaction.atomic
    def handle(self, *args, **options):
        apply(self.stdout.write)
        self.stdout.write(self.style.SUCCESS("Done."))
