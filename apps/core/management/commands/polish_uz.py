"""Replace the Uzbek texts in the database with the rewritten versions.

Reads content/portfolio/uz_texts.json. Before changing anything, the current
Uzbek values are saved to backups/uz_before_<timestamp>.json, so the run can
be undone with:

    python manage.py polish_uz --restore backups/uz_before_<timestamp>.json

Objects are found by stable keys (project slug + order, company name, ...),
not by database id, so the command works on any copy of the site.
"""
import json
from datetime import datetime

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

DATA = settings.BASE_DIR / "content" / "portfolio" / "uz_texts.json"

MODELS = {
    "SiteSettings": "core.SiteSettings",
    "Principle": "core.Principle",
    "Project": "projects.Project",
    "CaseSection": "projects.CaseSection",
    "Metric": "projects.Metric",
    "ProjectImage": "projects.ProjectImage",
    "Experience": "resume.Experience",
    "ExperienceBullet": "resume.ExperienceBullet",
    "Education": "resume.Education",
    "SkillGroup": "resume.SkillGroup",
    "LanguageSkill": "resume.LanguageSkill",
    "Award": "resume.Award",
}


def find(row):
    model = apps.get_model(MODELS[row["model"]])
    qs = model.objects.filter(**row["key"]) if row["key"] else model.objects.all()
    return qs.first()


class Command(BaseCommand):
    help = "Rewrite Uzbek texts (with automatic backup)."

    def add_arguments(self, parser):
        parser.add_argument("--restore", help="Backup file to restore from.")

    @transaction.atomic
    def handle(self, *args, restore=None, **options):
        source = restore or DATA
        try:
            rows = json.loads(open(source, encoding="utf-8").read())
        except FileNotFoundError:
            raise CommandError(f"File not found: {source}")

        backup, updated, missing = [], 0, []
        for row in rows:
            obj = find(row)
            if obj is None:
                missing.append(f"{row['model']} {row['key']}")
                continue
            field = f"{row['field']}_uz"
            backup.append({**row, "uz": getattr(obj, field)})
            if getattr(obj, field) != row["uz"]:
                setattr(obj, field, row["uz"])
                obj.save(update_fields=[field])
                updated += 1

        if not restore:
            folder = settings.BASE_DIR / "backups"
            folder.mkdir(exist_ok=True)
            path = folder / f"uz_before_{datetime.now():%Y%m%d_%H%M%S}.json"
            path.write_text(json.dumps(backup, ensure_ascii=False, indent=1), encoding="utf-8")
            self.stdout.write(f"Backup: {path}")

        for m in missing:
            self.stdout.write(self.style.WARNING(f"· not found, skipped: {m}"))
        self.stdout.write(self.style.SUCCESS(f"Updated {updated} Uzbek text(s)."))
