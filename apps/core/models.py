from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from .mixins import TranslatedModel, with_translations


class SingletonModel(models.Model):
    """Bazada faqat bitta yozuv bo'ladigan model."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):  # noqa: D102
        raise ValidationError(_("This record cannot be deleted."))

    @classmethod
    def load(cls):
        obj, _created = cls.objects.get_or_create(pk=1)
        return obj


@with_translations("headline", "intro", "about", "availability_note", "work_philosophy")
class SiteSettings(SingletonModel, TranslatedModel):
    class Availability(models.TextChoices):
        OPEN = "open", _("Open to opportunities")
        SELECTIVE = "selective", _("Open to selected projects")
        BUSY = "busy", _("Not available right now")

    full_name = models.CharField(max_length=120, default="Nizomiddin Xalilov")
    job_title = models.CharField(
        max_length=140,
        default="Backend & Computer Vision Engineer",
        help_text=_("Shown under the name. Keep it short."),
    )
    location = models.CharField(max_length=120, blank=True, default="Tashkent, Uzbekistan")

    headline_en = models.CharField(max_length=220, blank=True)
    headline_uz = models.CharField(max_length=220, blank=True)
    headline_de = models.CharField(max_length=220, blank=True)
    headline_ru = models.CharField(max_length=220, blank=True)

    intro_en = models.TextField(blank=True, help_text=_("1–2 sentences under the headline."))
    intro_uz = models.TextField(blank=True)
    intro_de = models.TextField(blank=True)
    intro_ru = models.TextField(blank=True)

    about_en = models.TextField(blank=True, help_text=_("About page. Markdown supported."))
    about_uz = models.TextField(blank=True)
    about_de = models.TextField(blank=True)
    about_ru = models.TextField(blank=True)

    work_philosophy_en = models.TextField(blank=True, help_text=_("'How I work' intro. Markdown."))
    work_philosophy_uz = models.TextField(blank=True)
    work_philosophy_de = models.TextField(blank=True)
    work_philosophy_ru = models.TextField(blank=True)

    availability = models.CharField(max_length=12, choices=Availability.choices, default=Availability.OPEN)
    availability_note_en = models.CharField(max_length=180, blank=True)
    availability_note_uz = models.CharField(max_length=180, blank=True)
    availability_note_de = models.CharField(max_length=180, blank=True)
    availability_note_ru = models.CharField(max_length=180, blank=True)

    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)

    avatar = models.ImageField(upload_to="site/", blank=True, help_text=_("Square photo, at least 600×600."))
    og_image = models.ImageField(upload_to="site/", blank=True, help_text=_("1200×630 social preview."))
    cv_file = models.FileField(
        upload_to="site/", blank=True,
        help_text=_("Optional. If empty, the /cv/ page is used for printing to PDF."),
    )

    github_username = models.CharField(max_length=60, blank=True, help_text=_("For live GitHub stats."))
    meta_description_en = models.CharField(max_length=200, blank=True)
    meta_description_uz = models.CharField(max_length=200, blank=True)
    meta_description_de = models.CharField(max_length=200, blank=True)
    meta_description_ru = models.CharField(max_length=200, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Site settings")
        verbose_name_plural = _("Site settings")

    def __str__(self):
        return self.full_name

    @property
    def availability_is_open(self):
        return self.availability in (self.Availability.OPEN, self.Availability.SELECTIVE)


class SocialLink(models.Model):
    ICONS = [
        ("github", "GitHub"), ("linkedin", "LinkedIn"), ("telegram", "Telegram"),
        ("mail", "Email"), ("x", "X / Twitter"), ("globe", "Website"),
        ("phone", "Phone"), ("kaggle", "Kaggle"),
    ]
    label = models.CharField(max_length=60)
    url = models.CharField(max_length=300, help_text=_("Full URL, or mailto:/tel: link."))
    icon = models.CharField(max_length=20, choices=ICONS, default="globe")
    show_in_header = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = _("Social link")

    def __str__(self):
        return self.label


@with_translations("title", "body")
class Principle(TranslatedModel):
    """'How I work' bo'limi uchun."""
    title_en = models.CharField(max_length=120)
    title_uz = models.CharField(max_length=120, blank=True)
    title_de = models.CharField(max_length=120, blank=True)
    title_ru = models.CharField(max_length=120, blank=True)
    body_en = models.TextField()
    body_uz = models.TextField(blank=True)
    body_de = models.TextField(blank=True)
    body_ru = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = _("Principle")

    def __str__(self):
        return self.title_en


class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=300, blank=True)
    language = models.CharField(max_length=8, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Message")

    def __str__(self):
        return f"{self.name} — {self.created_at:%Y-%m-%d}"


class PageView(models.Model):
    """Juda oddiy ichki statistika (tashqi analitikasiz)."""
    path = models.CharField(max_length=300, db_index=True)
    date = models.DateField(auto_now_add=True, db_index=True)
    count = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("path", "date")
        ordering = ["-date", "-count"]
        verbose_name = _("Page view")

    def __str__(self):
        return f"{self.path} · {self.date} · {self.count}"
