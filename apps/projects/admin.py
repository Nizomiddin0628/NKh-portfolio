from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from apps.core.admin_utils import lang_fieldsets, thumb

from .models import CaseSection, Metric, Project, ProjectImage, Technology


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ["preview", "image", "alt_text_en", "caption_en", "is_primary", "order"]
    readonly_fields = ["preview"]
    ordering = ["-is_primary", "order"]

    @admin.display(description=_("Preview"))
    def preview(self, obj):
        return thumb(obj.image, 72)


class CaseSectionInline(admin.StackedInline):
    model = CaseSection
    extra = 0
    fields = ["kind", "order", "heading_en", "body_en",
              "heading_uz", "body_uz", "heading_de", "body_de", "heading_ru", "body_ru"]
    classes = ["collapse"]


class MetricInline(admin.TabularInline):
    model = Metric
    extra = 0
    fields = ["label_en", "value_before", "value_after", "note_en", "order"]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["cover_thumb", "title", "status", "is_featured", "is_published",
                    "image_count_display", "section_count", "order"]
    list_display_links = ["title"]
    list_editable = ["is_featured", "is_published", "order"]
    list_filter = ["status", "is_featured", "is_published", "technologies"]
    search_fields = ["title", "tagline_en", "summary_en", "organisation"]
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ["technologies"]
    inlines = [ProjectImageInline, MetricInline, CaseSectionInline]
    save_on_top = True

    fieldsets = [
        (_("Basics"), {"fields": ["title", "slug", "status", "technologies"]}),
        (_("Placement"), {"fields": ["is_featured", "is_published", "order"]}),
        (_("Facts"), {"fields": ["organisation", "year_started", "year_finished", "team_size"]}),
        (_("Links"), {"fields": ["live_url", "repo_url", "is_confidential"]}),
        *lang_fieldsets(["tagline", "role", "summary", "context"]),
    ]

    @admin.display(description="")
    def cover_thumb(self, obj):
        cover = obj.cover
        return thumb(cover.image, 48) if cover else "—"

    @admin.display(description=_("Images"))
    def image_count_display(self, obj):
        n = obj.images.count()
        if n == 0:
            return format_html('<span style="color:#b45309">no images</span>')
        return n

    @admin.display(description=_("Case study"))
    def section_count(self, obj):
        n = obj.sections.count()
        if n == 0:
            return format_html('<span style="color:#b45309">empty</span>')
        return n

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("images", "sections")


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "project_count", "order"]
    list_editable = ["category", "order"]
    list_display_links = ["name"]
    prepopulated_fields = {"slug": ("name",)}
    list_filter = ["category"]

    @admin.display(description=_("Projects"))
    def project_count(self, obj):
        return obj.projects.count()
