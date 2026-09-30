from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import AiAction, AiChat, AiKnowledge, AiLog, Lead, Reminder


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ["created_at", "name", "contact", "short_need", "lang", "status"]
    list_filter = ["status", "lang", "created_at"]
    list_editable = ["status"]
    search_fields = ["name", "contact", "need", "transcript"]
    readonly_fields = ["name", "contact", "need", "timeline", "budget", "lang", "page", "session",
                       "transcript", "created_at", "updated_at"]
    fieldsets = [
        (None, {"fields": ["status", "note"]}),
        (_("Request"), {"fields": ["name", "contact", "need", "timeline", "budget"]}),
        (_("Context"), {"fields": ["lang", "page", "created_at", "transcript"]}),
    ]
    date_hierarchy = "created_at"

    @admin.display(description=_("Need"))
    def short_need(self, obj):
        return obj.need[:80]


@admin.register(AiKnowledge)
class AiKnowledgeAdmin(admin.ModelAdmin):
    list_display = ["short", "is_active", "source", "created_at"]
    list_filter = ["is_active"]
    list_editable = ["is_active"]
    search_fields = ["text"]

    @admin.display(description=_("Fact"))
    def short(self, obj):
        return obj.text[:100]

    def save_model(self, request, obj, form, change):
        if not obj.source:
            obj.source = "admin"
        super().save_model(request, obj, form, change)
        from .state import invalidate
        invalidate()


@admin.register(AiLog)
class AiLogAdmin(admin.ModelAdmin):
    list_display = ["created_at", "channel", "role", "kind", "lang", "short_q", "model", "steps",
                    "tokens_in", "tokens_out", "ms", "ok", "unanswered"]
    list_filter = ["channel", "role", "kind", "ok", "unanswered", "lang"]
    search_fields = ["question", "answer"]
    readonly_fields = [f.name for f in AiLog._meta.fields]
    date_hierarchy = "created_at"

    @admin.display(description=_("Question"))
    def short_q(self, obj):
        return obj.question[:70]

    def has_add_permission(self, request):
        return False


@admin.register(AiAction)
class AiActionAdmin(admin.ModelAdmin):
    list_display = ["created_at", "kind", "summary", "status", "channel", "result"]
    list_filter = ["status", "kind", "channel"]
    readonly_fields = [f.name for f in AiAction._meta.fields]

    def has_add_permission(self, request):
        return False


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ["due_at", "text", "sent_at"]
    list_filter = ["sent_at"]


@admin.register(AiChat)
class AiChatAdmin(admin.ModelAdmin):
    list_display = ["chat_id", "lang", "mode", "state", "last_activity"]
    readonly_fields = ["chat_id", "history", "run", "busy_since", "last_activity"]
