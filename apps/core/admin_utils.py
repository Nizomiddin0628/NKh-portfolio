"""Admin panelni ko'p tilli maydonlar bilan o'qishli qilish uchun yordamchilar."""
from django.utils.html import format_html

LANGS = (("en", "English"), ("uz", "O'zbekcha"), ("de", "Deutsch"), ("ru", "Русский"))


def lang_fieldsets(fields, extra_classes=("collapse",)):
    """Har bir til uchun alohida yig'ma bo'lim yasaydi.

    Inglizcha bo'lim ochiq turadi (majburiy), qolganlari yopiq —
    faqat kerak bo'lganda ochasiz.
    """
    sets = []
    for code, label in LANGS:
        classes = () if code == "en" else extra_classes
        title = f"Content · {label}" + ("" if code == "en" else " (optional)")
        sets.append((title, {
            "fields": [f"{name}_{code}" for name in fields],
            "classes": classes,
            "description": None if code == "en"
            else "Leave empty to fall back to the English text.",
        }))
    return sets


def thumb(image_field, size=64):
    if not image_field:
        return "—"
    return format_html(
        '<img src="{}" style="height:{}px;width:{}px;object-fit:cover;'
        'border-radius:6px;border:1px solid #ddd" />',
        image_field.url, size, size,
    )
