from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.core.admin_utils import lang_fieldsets

from .models import Award, Education, Experience, ExperienceBullet, LanguageSkill, Skill, SkillGroup


class ExperienceBulletInline(admin.TabularInline):
    model = ExperienceBullet
    extra = 2
    fields = ["text_en", "text_uz", "text_de", "text_ru", "order"]


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ["role_en", "company", "start_date", "end_date", "is_published", "order"]
    list_editable = ["is_published", "order"]
    list_display_links = ["role_en"]
    inlines = [ExperienceBulletInline]
    save_on_top = True
    fieldsets = [
        (_("Company"), {"fields": ["company", "company_url", "location"]}),
        (_("Period"), {"fields": ["start_date", "end_date", "is_published", "order"],
                       "description": _("Leave 'end date' empty for your current job.")}),
        *lang_fieldsets(["role", "employment_type", "summary"]),
    ]


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ["degree_en", "institution", "end_year", "grade", "order"]
    list_editable = ["order"]
    list_display_links = ["degree_en"]
    fieldsets = [
        (_("Institution"), {"fields": ["institution", "institution_url", "location"]}),
        (_("Period"), {"fields": ["start_year", "end_year", "grade", "order"]}),
        *lang_fieldsets(["degree", "field_of_study", "note"]),
    ]


class SkillInline(admin.TabularInline):
    model = Skill
    extra = 3


@admin.register(SkillGroup)
class SkillGroupAdmin(admin.ModelAdmin):
    list_display = ["name_en", "skill_count", "order"]
    list_editable = ["order"]
    list_display_links = ["name_en"]
    inlines = [SkillInline]
    fieldsets = [(None, {"fields": ["order"]}), *lang_fieldsets(["name", "note"])]

    @admin.display(description=_("Skills"))
    def skill_count(self, obj):
        return obj.skills.count()


@admin.register(LanguageSkill)
class LanguageSkillAdmin(admin.ModelAdmin):
    list_display = ["name_en", "level_en", "order"]
    list_editable = ["order"]
    list_display_links = ["name_en"]
    fieldsets = [(None, {"fields": ["order"]}), *lang_fieldsets(["name", "level"])]


@admin.register(Award)
class AwardAdmin(admin.ModelAdmin):
    list_display = ["title_en", "issuer", "year", "order"]
    list_editable = ["order"]
    list_display_links = ["title_en"]
    fieldsets = [
        (_("Details"), {"fields": ["issuer", "year", "url", "order"]}),
        *lang_fieldsets(["title", "description"]),
    ]
