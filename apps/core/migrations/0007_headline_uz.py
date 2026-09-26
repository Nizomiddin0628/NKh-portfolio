from django.db import migrations

HEADLINE = "Kuzatib, tahlil qilib, inson ishtirokisiz o'zi qaror qabul qiladigan tizimlar yarataman."


def forwards(apps, schema_editor):
    apps.get_model("core", "SiteSettings").objects.update(headline_uz=HEADLINE)


class Migration(migrations.Migration):
    dependencies = [("core", "0006_texts_tech_terms")]
    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
