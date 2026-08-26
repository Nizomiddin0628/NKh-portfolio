from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.core.mixins import TranslatedModel, with_translations

from .imaging import process_upload


class Technology(models.Model):
    class Category(models.TextChoices):
        LANGUAGE = "language", _("Language")
        BACKEND = "backend", _("Backend")
        AI = "ai", _("AI / Computer Vision")
        DATA = "data", _("Data")
        FRONTEND = "frontend", _("Frontend")
        INFRA = "infra", _("Infrastructure")
        TOOL = "tool", _("Tooling")

    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=60, unique=True)
    category = models.CharField(max_length=12, choices=Category.choices, default=Category.TOOL)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name_plural = _("Technologies")

    def __str__(self):
        return self.name


@with_translations("tagline", "role", "summary", "context")
class Project(TranslatedModel):
    class Status(models.TextChoices):
        PRODUCTION = "production", _("In production")
        RESEARCH = "research", _("Research")
        WIP = "wip", _("In progress")
        ARCHIVED = "archived", _("Archived")

    title = models.CharField(max_length=140, help_text=_("Product name — usually not translated."))
    slug = models.SlugField(max_length=160, unique=True)

    tagline_en = models.CharField(max_length=220, help_text=_("One line. What it does, for whom."))
    tagline_uz = models.CharField(max_length=220, blank=True)
    tagline_de = models.CharField(max_length=220, blank=True)
    tagline_ru = models.CharField(max_length=220, blank=True)

    role_en = models.CharField(max_length=140, blank=True, help_text=_("e.g. Backend + Computer Vision"))
    role_uz = models.CharField(max_length=140, blank=True)
    role_de = models.CharField(max_length=140, blank=True)
    role_ru = models.CharField(max_length=140, blank=True)

    summary_en = models.TextField(blank=True, help_text=_("2–4 sentences shown in the list. Markdown."))
    summary_uz = models.TextField(blank=True)
    summary_de = models.TextField(blank=True)
    summary_ru = models.TextField(blank=True)

    context_en = models.TextField(blank=True, help_text=_("Who it was for, team size, timeframe. Markdown."))
    context_uz = models.TextField(blank=True)
    context_de = models.TextField(blank=True)
    context_ru = models.TextField(blank=True)

    organisation = models.CharField(max_length=140, blank=True, help_text=_("Company or university."))
    year_started = models.PositiveSmallIntegerField(null=True, blank=True)
    year_finished = models.PositiveSmallIntegerField(null=True, blank=True)
    team_size = models.PositiveSmallIntegerField(null=True, blank=True)

    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PRODUCTION)
    technologies = models.ManyToManyField(Technology, blank=True, related_name="projects")

    live_url = models.URLField(blank=True)
    repo_url = models.URLField(blank=True)
    is_confidential = models.BooleanField(
        default=False,
        help_text=_("Show a 'source code is private' note instead of repo links."),
    )

    is_featured = models.BooleanField(default=False, help_text=_("Show on the home page."))
    is_published = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0, help_text=_("Lower number = higher on the page."))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "-year_started", "-id"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("projects:detail", kwargs={"slug": self.slug})

    # ── Rasmlar ───────────────────────────────────────────────────────────────
    @property
    def cover(self):
        """Asosiy rasm: `is_primary` belgilangani, bo'lmasa birinchisi."""
        images = list(self.images.all())
        if not images:
            return None
        for img in images:
            if img.is_primary:
                return img
        return images[0]

    @property
    def secondary_images(self):
        cover = self.cover
        return [i for i in self.images.all() if cover is None or i.pk != cover.pk]

    @property
    def image_count(self):
        return len(self.images.all())

    @property
    def period(self):
        if self.year_started and self.year_finished and self.year_started != self.year_finished:
            return f"{self.year_started}–{self.year_finished}"
        return str(self.year_finished or self.year_started or "")


def project_image_path(instance, filename):
    return f"projects/{instance.project.slug}/{filename}"


@with_translations("caption", "alt_text")
class ProjectImage(TranslatedModel):
    project = models.ForeignKey(Project, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to=project_image_path)

    alt_text_en = models.CharField(
        max_length=200, help_text=_("Required. Describe the image for screen readers.")
    )
    alt_text_uz = models.CharField(max_length=200, blank=True)
    alt_text_de = models.CharField(max_length=200, blank=True)
    alt_text_ru = models.CharField(max_length=200, blank=True)

    caption_en = models.CharField(max_length=220, blank=True)
    caption_uz = models.CharField(max_length=220, blank=True)
    caption_de = models.CharField(max_length=220, blank=True)
    caption_ru = models.CharField(max_length=220, blank=True)

    is_primary = models.BooleanField(default=False, help_text=_("The large image. Only one per project."))
    order = models.PositiveSmallIntegerField(default=0)

    width = models.PositiveIntegerField(null=True, blank=True, editable=False)
    height = models.PositiveIntegerField(null=True, blank=True, editable=False)

    class Meta:
        ordering = ["-is_primary", "order", "id"]
        verbose_name = _("Image")

    def __str__(self):
        return f"{self.project.title} — {self.pk}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        size = process_upload(self.image, max_width=1800)
        if size and (self.width, self.height) != size:
            self.width, self.height = size
            super().save(update_fields=["width", "height"])
        if self.is_primary:
            ProjectImage.objects.filter(project=self.project).exclude(pk=self.pk).update(is_primary=False)

    @property
    def aspect(self):
        if self.width and self.height:
            return f"{self.width} / {self.height}"
        return "16 / 10"


@with_translations("heading", "body")
class CaseSection(TranslatedModel):
    """Case study bloklari. Tartibni admin panelda o'zgartirasiz."""

    class Kind(models.TextChoices):
        PROBLEM = "problem", _("Problem")
        CONSTRAINTS = "constraints", _("Constraints")
        DECISION = "decision", _("Decisions & trade-offs")
        ARCHITECTURE = "architecture", _("Architecture")
        RESULT = "result", _("Outcome")
        RETRO = "retro", _("What I'd do differently")
        CUSTOM = "custom", _("Custom section")

    project = models.ForeignKey(Project, related_name="sections", on_delete=models.CASCADE)
    kind = models.CharField(max_length=14, choices=Kind.choices, default=Kind.PROBLEM)

    heading_en = models.CharField(max_length=160, blank=True, help_text=_("Leave empty to use the section type name."))
    heading_uz = models.CharField(max_length=160, blank=True)
    heading_de = models.CharField(max_length=160, blank=True)
    heading_ru = models.CharField(max_length=160, blank=True)

    body_en = models.TextField(help_text=_("Markdown: **bold**, lists, `code`."))
    body_uz = models.TextField(blank=True)
    body_de = models.TextField(blank=True)
    body_ru = models.TextField(blank=True)

    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = _("Case study section")

    def __str__(self):
        return f"{self.project.title} — {self.get_kind_display()}"

    @property
    def title(self):
        return self.tr("heading") or self.get_kind_display()


@with_translations("label", "note")
class Metric(TranslatedModel):
    """Natijani raqamda ko'rsatadigan blok."""
    project = models.ForeignKey(Project, related_name="metrics", on_delete=models.CASCADE)

    label_en = models.CharField(max_length=90, help_text=_("e.g. Manual data entry"))
    label_uz = models.CharField(max_length=90, blank=True)
    label_de = models.CharField(max_length=90, blank=True)
    label_ru = models.CharField(max_length=90, blank=True)

    value_before = models.CharField(max_length=40, blank=True, help_text=_("e.g. 40 min/day"))
    value_after = models.CharField(max_length=40, help_text=_("e.g. 4 min/day"))

    note_en = models.CharField(max_length=140, blank=True)
    note_uz = models.CharField(max_length=140, blank=True)
    note_de = models.CharField(max_length=140, blank=True)
    note_ru = models.CharField(max_length=140, blank=True)

    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.label_en}: {self.value_after}"
