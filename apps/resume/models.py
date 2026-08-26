from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.mixins import TranslatedModel, with_translations


@with_translations("role", "summary", "employment_type")
class Experience(TranslatedModel):
    company = models.CharField(max_length=140)
    company_url = models.URLField(blank=True)
    location = models.CharField(max_length=140, blank=True)

    role_en = models.CharField(max_length=160)
    role_uz = models.CharField(max_length=160, blank=True)
    role_de = models.CharField(max_length=160, blank=True)
    role_ru = models.CharField(max_length=160, blank=True)

    employment_type_en = models.CharField(max_length=60, blank=True, help_text=_("Full-time, Contract…"))
    employment_type_uz = models.CharField(max_length=60, blank=True)
    employment_type_de = models.CharField(max_length=60, blank=True)
    employment_type_ru = models.CharField(max_length=60, blank=True)

    summary_en = models.TextField(blank=True, help_text=_("Markdown. 1–3 sentences."))
    summary_uz = models.TextField(blank=True)
    summary_de = models.TextField(blank=True)
    summary_ru = models.TextField(blank=True)

    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True, help_text=_("Leave empty if this is your current job."))
    is_published = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "-start_date"]
        verbose_name = _("Experience")
        verbose_name_plural = _("Experience")

    def __str__(self):
        return f"{self.role_en} — {self.company}"

    @property
    def is_current(self):
        return self.end_date is None


@with_translations("text")
class ExperienceBullet(TranslatedModel):
    experience = models.ForeignKey(Experience, related_name="bullets", on_delete=models.CASCADE)
    text_en = models.CharField(max_length=300)
    text_uz = models.CharField(max_length=300, blank=True)
    text_de = models.CharField(max_length=300, blank=True)
    text_ru = models.CharField(max_length=300, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = _("Bullet point")

    def __str__(self):
        return self.text_en[:60]


@with_translations("degree", "field_of_study", "note")
class Education(TranslatedModel):
    institution = models.CharField(max_length=180)
    institution_url = models.URLField(blank=True)
    location = models.CharField(max_length=140, blank=True)

    degree_en = models.CharField(max_length=140)
    degree_uz = models.CharField(max_length=140, blank=True)
    degree_de = models.CharField(max_length=140, blank=True)
    degree_ru = models.CharField(max_length=140, blank=True)

    field_of_study_en = models.CharField(max_length=160, blank=True)
    field_of_study_uz = models.CharField(max_length=160, blank=True)
    field_of_study_de = models.CharField(max_length=160, blank=True)
    field_of_study_ru = models.CharField(max_length=160, blank=True)

    note_en = models.TextField(blank=True)
    note_uz = models.TextField(blank=True)
    note_de = models.TextField(blank=True)
    note_ru = models.TextField(blank=True)

    start_year = models.PositiveSmallIntegerField(null=True, blank=True)
    end_year = models.PositiveSmallIntegerField(null=True, blank=True)
    grade = models.CharField(max_length=40, blank=True, help_text=_("e.g. GPA 4.5 / 5.0"))
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "-end_year"]
        verbose_name = _("Education")
        verbose_name_plural = _("Education")

    def __str__(self):
        return f"{self.degree_en} — {self.institution}"


@with_translations("name", "note")
class SkillGroup(TranslatedModel):
    name_en = models.CharField(max_length=100)
    name_uz = models.CharField(max_length=100, blank=True)
    name_de = models.CharField(max_length=100, blank=True)
    name_ru = models.CharField(max_length=100, blank=True)
    note_en = models.CharField(max_length=200, blank=True)
    note_uz = models.CharField(max_length=200, blank=True)
    note_de = models.CharField(max_length=200, blank=True)
    note_ru = models.CharField(max_length=200, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = _("Skill group")

    def __str__(self):
        return self.name_en


class Skill(models.Model):
    """Ataylab foiz ko'rsatkichisiz — faqat 'qanchalik markaziy' ekani."""

    class Depth(models.TextChoices):
        CORE = "core", _("Core — daily driver")
        STRONG = "strong", _("Strong — used in production")
        WORKING = "working", _("Working knowledge")

    group = models.ForeignKey(SkillGroup, related_name="skills", on_delete=models.CASCADE)
    name = models.CharField(max_length=80)
    depth = models.CharField(max_length=8, choices=Depth.choices, default=Depth.STRONG)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.name


@with_translations("name", "level")
class LanguageSkill(TranslatedModel):
    name_en = models.CharField(max_length=60)
    name_uz = models.CharField(max_length=60, blank=True)
    name_de = models.CharField(max_length=60, blank=True)
    name_ru = models.CharField(max_length=60, blank=True)
    level_en = models.CharField(max_length=80, help_text=_("e.g. Native, IELTS 6.0 (B2)"))
    level_uz = models.CharField(max_length=80, blank=True)
    level_de = models.CharField(max_length=80, blank=True)
    level_ru = models.CharField(max_length=80, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = _("Language")

    def __str__(self):
        return self.name_en


@with_translations("title", "description")
class Award(TranslatedModel):
    title_en = models.CharField(max_length=180)
    title_uz = models.CharField(max_length=180, blank=True)
    title_de = models.CharField(max_length=180, blank=True)
    title_ru = models.CharField(max_length=180, blank=True)
    description_en = models.TextField(blank=True)
    description_uz = models.TextField(blank=True)
    description_de = models.TextField(blank=True)
    description_ru = models.TextField(blank=True)
    issuer = models.CharField(max_length=180, blank=True)
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    url = models.URLField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "-year"]
        verbose_name = _("Award / recognition")

    def __str__(self):
        return self.title_en
