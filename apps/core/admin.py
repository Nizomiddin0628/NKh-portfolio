from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .admin_utils import lang_fieldsets
from .models import ContactMessage, PageView, Principle, SiteSettings, SocialLink

admin.site.site_header = "Nizomiddin Xalilov"
admin.site.site_title = "Portfolio admin"
admin.site.index_title = _("Dashboard")
admin.site.index_template = "admin/portfolio_index.html"


class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = "__all__"
        widgets = {"avatar_crop": forms.HiddenInput}


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    form = SiteSettingsForm

    class Media:
        css = {"all": ["https://cdn.jsdelivr.net/npm/cropperjs@1.6.2/dist/cropper.min.css"]}
        js = [
            "https://cdn.jsdelivr.net/npm/cropperjs@1.6.2/dist/cropper.min.js",
            "js/admin-avatar-crop.js",
        ]

    fieldsets = [
        (_("Identity"), {"fields": ["full_name", "job_title", "location", "avatar", "avatar_crop", "og_image"]}),
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
    list_display = ["name", "email", "phone", "subject", "created_at", "is_read"]
    list_filter = ["is_read", "created_at", "language"]
    search_fields = ["name", "email", "subject", "message"]
    readonly_fields = ["name", "email", "phone", "reply", "subject", "message", "ip_address",
                       "user_agent", "language", "created_at"]
    actions = ["mark_read"]
    fields = ["name", "email", "phone", "reply", "subject", "message",
              "created_at", "language", "ip_address", "user_agent", "is_read"]

    @admin.display(description=_("Reply"))
    def reply(self, obj):
        mail = format_html('<a class="button" href="mailto:{}">Reply by email</a>', obj.email)
        if not obj.phone:
            return mail
        tel = "".join(ch for ch in obj.phone if ch.isdigit() or ch == "+")
        return format_html('{} &nbsp;<a class="button" href="tel:{}">Call {}</a>', mail, tel, obj.phone)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        # Opening a message marks it as read
        ContactMessage.objects.filter(pk=object_id, is_read=False).update(is_read=True)
        return super().change_view(request, object_id, form_url, extra_context)

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
