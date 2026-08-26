from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .admin_utils import lang_fieldsets
from .models import ContactMessage, PageView, Principle, SiteSettings, SocialLink

admin.site.site_header = "Portfolio"
admin.site.site_title = "Portfolio admin"
admin.site.index_title = _("Manage your site content")


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = [
        (_("Identity"), {"fields": ["full_name", "job_title", "location", "avatar", "og_image"]}),
        (_("Availability"), {"fields": ["availability"]}),
        (_("Contact"), {"fields": ["email", "phone", "github_username", "cv_file"]}),
        *lang_fieldsets(["headline", "intro", "about", "work_philosophy",
                         "availability_note", "meta_description"]),
    ]

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        """Ro'yxat o'rniga to'g'ridan-to'g'ri tahrirlash sahifasini ochadi."""
        from django.shortcuts import redirect
        from django.urls import reverse
        obj = SiteSettings.load()
        return redirect(reverse("admin:core_sitesettings_change", args=[obj.pk]))


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ["label", "icon", "url", "show_in_header", "order"]
    list_editable = ["show_in_header", "order"]
    list_display_links = ["label"]


@admin.register(Principle)
class PrincipleAdmin(admin.ModelAdmin):
    list_display = ["title_en", "is_published", "order"]
    list_editable = ["is_published", "order"]
    list_display_links = ["title_en"]
    fieldsets = [
        (None, {"fields": ["order", "is_published"]}),
        *lang_fieldsets(["title", "body"]),
    ]


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "subject", "created_at", "is_read"]
    list_filter = ["is_read", "created_at", "language"]
    search_fields = ["name", "email", "subject", "message"]
    readonly_fields = ["name", "email", "subject", "message", "ip_address",
                       "user_agent", "language", "created_at"]
    actions = ["mark_read"]

    @admin.action(description=_("Mark selected messages as read"))
    def mark_read(self, request, queryset):
        queryset.update(is_read=True)

    def has_add_permission(self, request):
        return False


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ["path", "date", "count"]
    list_filter = ["date"]
    search_fields = ["path"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
