"""Data kept by the AI assistant.

Nothing here holds secrets: the Gemini key and the Telegram token live in
.env only. Guest conversations are stored with a salted IP hash, never the
raw address, and are pruned after AI_LOG_RETENTION_DAYS.
"""
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class AiLog(models.Model):
    """One row per request: who asked what, which model answered, how long."""

    class Channel(models.TextChoices):
        SITE = "site", "Site"
        TELEGRAM = "telegram", "Telegram"
        SYSTEM = "system", "System"

    class Kind(models.TextChoices):
        ASK = "ask", "Question"
        VOICE = "voice", "Voice"
        FILE = "file", "Image / PDF"
        DIGEST = "digest", "Digest"
        ACTION = "action", "Action"

    channel = models.CharField(max_length=10, choices=Channel.choices, default=Channel.SITE)
    role = models.CharField(max_length=6, default="guest")  # guest | owner
    kind = models.CharField(max_length=8, choices=Kind.choices, default=Kind.ASK)
    lang = models.CharField(max_length=5, blank=True)
    mode = models.CharField(max_length=6, blank=True)  # local | web
    question = models.TextField(blank=True)
    answer = models.TextField(blank=True)
    model = models.CharField(max_length=60, blank=True)
    steps = models.PositiveSmallIntegerField(default=0)
    tools_used = models.CharField(max_length=200, blank=True)
    tokens_in = models.PositiveIntegerField(default=0)
    tokens_out = models.PositiveIntegerField(default=0)
    ms = models.PositiveIntegerField(default=0)
    ok = models.BooleanField(default=True)
    error = models.CharField(max_length=200, blank=True)
    unanswered = models.BooleanField(default=False, help_text=_("The assistant had no facts for this question."))
    ip_hash = models.CharField(max_length=32, blank=True, db_index=True)
    session = models.CharField(max_length=40, blank=True, db_index=True)
    chat_id = models.BigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("AI request")
        verbose_name_plural = _("AI requests")

    def __str__(self):
        return f"{self.get_channel_display()} · {self.role} · {self.question[:40]}"


class AiKnowledge(models.Model):
    """Facts the owner teaches the assistant ("remember that ...")."""

    text = models.TextField(help_text=_("One fact per row, in any language."))
    is_active = models.BooleanField(default=True)
    source = models.CharField(max_length=20, blank=True)  # telegram | site | admin
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("AI fact")
        verbose_name_plural = _("AI facts")

    def __str__(self):
        return self.text[:60]


class Lead(models.Model):
    """A visitor who told the assistant about a project and left a contact."""

    class Status(models.TextChoices):
        NEW = "new", _("New")
        CONTACTED = "contacted", _("Contacted")
        CLOSED = "closed", _("Closed")

    name = models.CharField(max_length=120, blank=True)
    contact = models.CharField(max_length=200, help_text=_("Email, Telegram username or phone."))
    need = models.TextField(help_text=_("What they want to build, in their words."))
    timeline = models.CharField(max_length=120, blank=True)
    budget = models.CharField(max_length=120, blank=True)
    lang = models.CharField(max_length=5, blank=True)
    page = models.CharField(max_length=300, blank=True)
    ip_hash = models.CharField(max_length=32, blank=True)
    session = models.CharField(max_length=40, blank=True)
    transcript = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.NEW)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Lead")
        verbose_name_plural = _("Leads")

    def __str__(self):
        return f"{self.name or self.contact} — {self.created_at:%Y-%m-%d}"

    @property
    def contact_is_email(self):
        return "@" in self.contact and "." in self.contact.split("@")[-1] and not self.contact.startswith("@")


class AiAction(models.Model):
    """A change the assistant prepared. Nothing runs until the owner confirms."""

    class Status(models.TextChoices):
        PROPOSED = "proposed", _("Waiting for confirmation")
        DONE = "done", _("Done")
        CANCELLED = "cancelled", _("Cancelled")
        EXPIRED = "expired", _("Expired")
        FAILED = "failed", _("Failed")

    kind = models.CharField(max_length=30)
    params = models.JSONField(default=dict)
    summary = models.TextField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PROPOSED)
    channel = models.CharField(max_length=10, default="site")  # where it was requested
    tg_msgs = models.JSONField(default=list, blank=True)  # [[chat_id, message_id], ...]
    result = models.CharField(max_length=300, blank=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    decided_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("AI action")
        verbose_name_plural = _("AI actions")

    def __str__(self):
        return f"{self.kind}: {self.summary[:50]} [{self.status}]"

    @property
    def is_open(self):
        return self.status == self.Status.PROPOSED and self.expires_at > timezone.now()


class AiChat(models.Model):
    """Telegram conversation state, one row per chat."""

    chat_id = models.BigIntegerField(unique=True)
    lang = models.CharField(max_length=5, default="uz")
    mode = models.CharField(max_length=6, default="local")  # local | web
    state = models.CharField(max_length=6, default="idle")  # idle | busy
    run = models.CharField(max_length=36, blank=True)  # key of the running request
    history = models.JSONField(default=list, blank=True)  # [{"role": "user"|"model", "text": ...}]
    busy_since = models.DateTimeField(null=True, blank=True)
    digest_on = models.BooleanField(default=True, help_text=_("Send the 08:30 / 18:00 report here."))
    last_activity = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Telegram chat")
        verbose_name_plural = _("Telegram chats")

    def __str__(self):
        return f"chat {self.chat_id} ({self.state})"


class Reminder(models.Model):
    text = models.CharField(max_length=300)
    due_at = models.DateTimeField(db_index=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["due_at"]
        verbose_name = _("Reminder")
        verbose_name_plural = _("Reminders")

    def __str__(self):
        return f"{self.due_at:%Y-%m-%d %H:%M} — {self.text[:40]}"
