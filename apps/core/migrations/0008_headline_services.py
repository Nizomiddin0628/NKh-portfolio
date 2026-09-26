from django.db import migrations

HEAD = {'headline_uz': 'AI integratsiyalari, web saytlar, Telegram botlar va Machine Learning modellarini ishlab chiqaman.', 'headline_en': 'I build AI integrations, websites, Telegram bots and Machine Learning models.', 'headline_ru': 'Разрабатываю AI-интеграции, веб-сайты, Telegram-ботов и модели Machine Learning.'}


def forwards(apps, schema_editor):
    apps.get_model("core", "SiteSettings").objects.update(**HEAD)


class Migration(migrations.Migration):
    dependencies = [("core", "0007_headline_uz")]
    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
