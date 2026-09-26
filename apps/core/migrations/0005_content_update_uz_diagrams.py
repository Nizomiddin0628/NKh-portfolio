"""Content update: literary Uzbek texts and diagrams for two projects.

Runs once per database as part of `migrate`, so deploys need no extra commands.
"""
from django.conf import settings
from django.core.management import call_command
from django.db import migrations


def forwards(apps, schema_editor):
    from apps.core.content.uz_texts import apply_texts

    # Diagrams first (only for projects without images), so the texts below
    # also cover their captions
    call_command("load_project_diagrams", verbosity=0)
    apply_texts(apps.get_model, settings.BASE_DIR / "content" / "portfolio" / "uz_texts.json")


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0004_contact_phone"),
        ("projects", "0001_initial"),
        ("resume", "0002_certificate"),
    ]

    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
