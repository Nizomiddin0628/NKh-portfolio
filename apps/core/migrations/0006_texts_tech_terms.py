"""Text fixes: technical terms stay in English, availability note updated."""
from django.db import migrations

MODELS = [
    "core.SiteSettings", "core.Principle", "projects.Project", "projects.CaseSection",
    "projects.Metric", "projects.ProjectImage", "resume.Experience", "resume.ExperienceBullet",
    "resume.Education", "resume.SkillGroup", "resume.LanguageSkill", "resume.Award",
]

# Applied to every Uzbek field, in this order (longer phrases first)
UZ_REPLACE = [
    ("Kompyuter ko'rish (computer vision) sohasiga", "Computer Vision sohasiga"),
    ("backend va kompyuter ko'rish (computer vision) bo'yicha dasturchi", "Backend va Computer Vision dasturchisi"),
    ("Kompyuter ko'rish va sun'iy intellekt", "Computer Vision va AI"),
    ("klassik kompyuter ko'rish usullari", "klassik Computer Vision usullari"),
    ("Kompyuter ko'rish, to'liq mustaqil", "Computer Vision, to'liq o'zim"),
    ("kompyuter ko'rish sohasida", "Computer Vision sohasida"),
    ("Kompyuter ko'rish", "Computer Vision"),
    ("kompyuter ko'rish", "Computer Vision"),
    ("computer vision", "Computer Vision"),
    ("Boshqaruv paneli, README hujjati va tushunarli jurnal yozuvlari ham ishning ajralmas qismi.", "Admin panel, README va tushunarli loglar ham ishning ajralmas qismi."),
    ("xavfsizlik boshqaruv panelini", "xavfsizlik dashboardini"),
    ("boshqaruv panellari", "dashboardlar"),
    ("boshqaruv paneli", "dashboard"),
    ("Boshqaruv paneli", "Dashboard"),
    ("Tkinter asosidagi kompyuter dasturi", "Tkinter'da yozilgan desktop dastur"),
    ("kompyuter dasturi", "desktop dastur"),
    ("Ma'lumotlar to'plami ham", "Dataset ham"),
    ("ma'lumotlar to'plamidan", "datasetdan"),
    ("ma'lumotlar to'plami", "dataset"),
    ("Avtopark (fleet) va aktivlar (asset) bo'limlari", "Fleet va asset bo'limlari"),
    ("Avtopark, aktivlar va buxgalteriya bo'limlari", "Fleet, asset va buxgalteriya bo'limlari"),
    ("Avtopark va aktivlar bo'limlarini", "Fleet va asset bo'limlarini"),
    ("Avtopark bo'limi", "Fleet bo'limi"),
    ("real vaqt rejimidagi oqim", "real-time streaming"),
    ("real vaqt rejimida", "real vaqtda"),
    ("serverga joylashtirish, monitoring", "deploy, monitoring"),
    ("mashina bo'yicha yozuv", "mashina kartasi"),
    ("**Yig'ma yozuv**", "**Case summary**"),
    ("Yig'ma yozuv:", "Case summary:"),
    ("yig'ma yozuv", "karta"),
    ("yagona yozuvga", "bitta kartaga"),
    ("Tajriba uchun emas, amaldagi tizimlar uchun", "Notebook uchun emas, production uchun"),
]

# Whole-field values: (model, lookup, field, value)
OVERRIDES = [
    ("core.SiteSettings", {}, "intro_uz",
     "Python va Django asosida backend tizimlar, YOLO va OpenCV yordamida esa Computer Vision yechimlarini ishlab chiqaman. Hozirda AQSH bozorida faoliyat yurituvchi logistika kompaniyasining ichki tizimlari ustida ishlayman: 500 ta yuk mashinasi va 600 ta tirkama."),
    ("core.SiteSettings", {}, "availability_note_uz",
     "Full Stack, Computer Vision va Deep Learning yo'nalishlarida ishga tayyorman"),
    ("core.SiteSettings", {}, "availability_note_en",
     "Available for Full Stack, Computer Vision and Deep Learning roles"),
    ("core.SiteSettings", {}, "availability_note_ru",
     "\u0413\u043e\u0442\u043e\u0432 \u043a \u0440\u0430\u0431\u043e\u0442\u0435: Full Stack, Computer Vision, Deep Learning"),
]


def forwards(apps, schema_editor):
    for label in MODELS:
        model = apps.get_model(*label.split("."))
        fields = [f.name for f in model._meta.fields if f.name.endswith("_uz")]
        for obj in model.objects.all():
            changed = []
            for name in fields:
                old = getattr(obj, name) or ""
                new = old
                for a, b in UZ_REPLACE:
                    new = new.replace(a, b)
                if new != old:
                    setattr(obj, name, new)
                    changed.append(name)
            if changed:
                obj.save(update_fields=changed)
    for label, lookup, field, value in OVERRIDES:
        apps.get_model(*label.split(".")).objects.filter(**lookup).update(**{field: value})


class Migration(migrations.Migration):
    dependencies = [("core", "0005_content_update_uz_diagrams")]
    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
