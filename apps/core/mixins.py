"""Ko'p tilli maydonlar uchun yengil yechim (tashqi kutubxonasiz).

Har bir tarjima qilinadigan maydon `<name>_en`, `<name>_uz`, `<name>_de`,
`<name>_ru` ko'rinishida saqlanadi. `@with_translations("tagline")` dekoratori
modelga `.tagline` xossasini qo'shadi — u faol tilga mos qiymatni qaytaradi,
qiymat bo'sh bo'lsa inglizchaga qaytadi.

Natijada admin panelda faqat inglizchani to'ldirish ham yetarli:
sayt hech qachon bo'sh matn ko'rsatmaydi.
"""
from django.db import models
from django.utils.translation import get_language

TRANSLATION_LANGS = ("en", "uz", "de", "ru")
FALLBACK_LANG = "en"


class TranslatedModel(models.Model):
    class Meta:
        abstract = True

    def tr(self, field: str) -> str:
        lang = (get_language() or FALLBACK_LANG).split("-")[0]
        if lang not in TRANSLATION_LANGS:
            lang = FALLBACK_LANG
        value = getattr(self, f"{field}_{lang}", "") or ""
        if not value and lang != FALLBACK_LANG:
            value = getattr(self, f"{field}_{FALLBACK_LANG}", "") or ""
        return value


def with_translations(*fields):
    """Modelga tarjima xossalarini qo'shadi: `obj.tagline` -> `obj.tr("tagline")`."""

    def decorator(cls):
        for name in fields:
            setattr(cls, name, property(lambda self, _n=name: self.tr(_n)))
        cls.TRANSLATED_FIELDS = tuple(fields)
        return cls

    return decorator


def translated_field_names(*fields):
    """Admin `fieldsets` uchun: ("tagline",) -> ["tagline_en", "tagline_uz", ...]"""
    return [f"{name}_{lang}" for name in fields for lang in TRANSLATION_LANGS]
