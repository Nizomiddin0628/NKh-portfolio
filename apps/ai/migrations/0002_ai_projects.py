"""Content: the two AI projects (assistant on this site, AI Kotib for the ERP).

Runs once per database as part of `migrate`. The texts live in
apps/ai/content/projects.py; `python manage.py ai_projects` re-applies them.
"""
from django.db import migrations


def forwards(apps, schema_editor):
    from apps.ai.content.projects import apply
    apply()


class Migration(migrations.Migration):
    dependencies = [
        ("ai", "0001_initial"),
        ("projects", "0001_initial"),
    ]

    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
