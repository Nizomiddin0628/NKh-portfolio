"""Changes the assistant prepares and the owner confirms.

    propose()  -> validates, stores an AiAction(PROPOSED), changes nothing
    confirm()  -> locks the row, validates again, applies, marks DONE/FAILED
    cancel()   -> marks CANCELLED

Kinds and what they may touch are fixed here in code. Nothing about users,
passwords, keys, the domain or deployment can be changed through the assistant.
"""
import logging
from datetime import datetime

from django.conf import settings
from django.core.mail import EmailMessage
from django.db import transaction
from django.utils import timezone

from apps.core.models import ContactMessage, SiteSettings
from apps.projects.models import Project

from .models import AiAction, AiKnowledge, AiLog, Lead, Reminder

logger = logging.getLogger(__name__)
EXPIRES_MINUTES = 30
LANGS = ("en", "uz", "ru")

SETTINGS_TRANSLATED = ("headline", "intro", "about", "availability_note", "work_philosophy", "meta_description")
SETTINGS_PLAIN = ("job_title", "location", "availability")
PROJECT_TRANSLATED = ("tagline", "role", "summary", "context")
PROJECT_PLAIN = ("title", "status", "organisation", "order", "is_featured", "live_url")


class ActionError(Exception):
    pass


def _max_len(model, field):
    f = model._meta.get_field(field)
    return getattr(f, "max_length", None)


def _shorten(text, n=70):
    text = " ".join(str(text).split())
    return text if len(text) <= n else text[: n - 1] + "…"


# ── Validation + summaries ──────────────────────────────────────────────────

def _check_settings(p):
    field, value, lang = p.get("field", ""), p.get("value", ""), p.get("lang", "")
    conf = SiteSettings.load()
    if field in SETTINGS_TRANSLATED:
        if lang not in LANGS:
            raise ActionError("lang must be en, uz or ru for this field")
        attr = f"{field}_{lang}"
    elif field in SETTINGS_PLAIN:
        attr = field
        if field == "availability" and value not in ("open", "selective", "busy"):
            raise ActionError("availability must be open, selective or busy")
    else:
        raise ActionError(f"field {field} cannot be changed here")
    limit = _max_len(SiteSettings, attr)
    if limit and len(value) > limit:
        raise ActionError(f"too long: max {limit} characters")
    old = getattr(conf, attr, "")
    p["attr"] = attr
    return f"Site {attr}: «{_shorten(old)}» → «{_shorten(value)}»"


def _do_settings(p):
    conf = SiteSettings.load()
    setattr(conf, p["attr"], p["value"])
    conf.save(update_fields=[p["attr"], "updated_at"])
    return f"{p['attr']} updated"


def _check_project(p):
    project = Project.objects.filter(slug=p.get("slug", "")).first()
    if project is None:
        raise ActionError("no such project")
    field, value, lang = p.get("field", ""), p.get("value", ""), p.get("lang", "")
    if field in PROJECT_TRANSLATED:
        if lang not in LANGS:
            raise ActionError("lang must be en, uz or ru for this field")
        attr = f"{field}_{lang}"
    elif field in PROJECT_PLAIN:
        attr = field
        if field == "status" and value not in ("production", "research", "wip", "archived"):
            raise ActionError("status must be production, research, wip or archived")
        if field == "order":
            try:
                p["value"] = value = int(value)
            except ValueError as exc:
                raise ActionError("order must be a number") from exc
        if field == "is_featured":
            p["value"] = value = str(value).lower() in ("1", "true", "yes", "ha", "da")
    else:
        raise ActionError(f"field {field} cannot be changed here")
    limit = _max_len(Project, attr)
    if limit and isinstance(value, str) and len(value) > limit:
        raise ActionError(f"too long: max {limit} characters")
    p["attr"] = attr
    old = getattr(project, attr, "")
    return f"Project {project.title} — {attr}: «{_shorten(old)}» → «{_shorten(value)}»"


def _do_project(p):
    project = Project.objects.get(slug=p["slug"])
    setattr(project, p["attr"], p["value"])
    project.save(update_fields=[p["attr"], "updated_at"])
    return f"{project.title}: {p['attr']} updated"


def _check_visibility(p):
    project = Project.objects.filter(slug=p.get("slug", "")).first()
    if project is None:
        raise ActionError("no such project")
    state = "published" if p.get("published") else "hidden"
    return f"Project {project.title}: {state}"


def _do_visibility(p):
    project = Project.objects.get(slug=p["slug"])
    project.is_published = bool(p.get("published"))
    project.save(update_fields=["is_published", "updated_at"])
    return "visibility updated"


def _check_lead(p):
    lead = Lead.objects.filter(pk=p.get("id")).first()
    if lead is None:
        raise ActionError("no such lead")
    status = p.get("status") or ""
    if status and status not in ("new", "contacted", "closed"):
        raise ActionError("status must be new, contacted or closed")
    if not status and not p.get("note"):
        raise ActionError("nothing to change")
    bits = []
    if status:
        bits.append(f"status {lead.status} → {status}")
    if p.get("note"):
        bits.append(f"note: {_shorten(p['note'])}")
    return f"Lead #{lead.pk} ({lead.name or lead.contact}): " + ", ".join(bits)


def _do_lead(p):
    lead = Lead.objects.get(pk=p["id"])
    if p.get("status"):
        lead.status = p["status"]
    if p.get("note"):
        lead.note = (lead.note + "\n" if lead.note else "") + p["note"]
    lead.save()
    return "lead updated"


def _check_reply(p):
    lead = Lead.objects.filter(pk=p.get("id")).first()
    if lead is None:
        raise ActionError("no such lead")
    if not lead.contact_is_email:
        raise ActionError("this lead left no email address; write to them directly")
    if "smtp" not in settings.EMAIL_BACKEND:
        raise ActionError("email is not configured on the server (EMAIL_HOST_PASSWORD)")
    if len(p.get("body", "")) < 20:
        raise ActionError("the reply is too short")
    return f"Email to {lead.contact}: «{p.get('subject', '')}» — {_shorten(p.get('body', ''), 120)}"


def _do_reply(p):
    lead = Lead.objects.get(pk=p["id"])
    conf = SiteSettings.load()
    EmailMessage(p["subject"], p["body"], settings.DEFAULT_FROM_EMAIL, [lead.contact],
                 reply_to=[conf.email] if conf.email else None).send()
    lead.status = "contacted"
    lead.note = (lead.note + "\n" if lead.note else "") + f"Replied by email {timezone.localtime():%Y-%m-%d %H:%M}"
    lead.save()
    return "email sent"


def _check_messages_read(p):
    ids = p.get("ids") or []
    qs = ContactMessage.objects.filter(is_read=False)
    if ids:
        qs = qs.filter(pk__in=ids)
    n = qs.count()
    if not n:
        raise ActionError("no unread messages match")
    return f"Mark {n} message(s) as read"


def _do_messages_read(p):
    qs = ContactMessage.objects.filter(is_read=False)
    if p.get("ids"):
        qs = qs.filter(pk__in=p["ids"])
    return f"{qs.update(is_read=True)} marked read"


def _check_remember(p):
    text = p.get("text", "").strip()
    if len(text) < 5:
        raise ActionError("the fact is too short")
    return f"Remember: «{_shorten(text, 120)}»"


def _do_remember(p):
    AiKnowledge.objects.create(text=p["text"].strip(), source="assistant")
    from .state import invalidate
    invalidate()
    return "fact saved"


def _check_forget(p):
    row = AiKnowledge.objects.filter(pk=p.get("id"), is_active=True).first()
    if row is None:
        raise ActionError("no such fact")
    return f"Forget: «{_shorten(row.text, 120)}»"


def _do_forget(p):
    AiKnowledge.objects.filter(pk=p["id"]).update(is_active=False)
    from .state import invalidate
    invalidate()
    return "fact removed"


def _parse_due(value):
    try:
        naive = datetime.fromisoformat(str(value).replace(" ", "T")[:16])
    except ValueError as exc:
        raise ActionError("due must look like 2026-10-01T10:00") from exc
    due = timezone.make_aware(naive, timezone.get_current_timezone())
    if due <= timezone.now():
        raise ActionError("that time is already in the past")
    return due


def _check_reminder(p):
    due = _parse_due(p.get("due"))
    if len(p.get("text", "").strip()) < 2:
        raise ActionError("reminder text is empty")
    return f"Reminder {timezone.localtime(due):%d.%m %H:%M}: «{_shorten(p['text'], 100)}»"


def _do_reminder(p):
    Reminder.objects.create(text=p["text"].strip(), due_at=_parse_due(p["due"]))
    return "reminder saved"


def _check_reminder_remove(p):
    row = Reminder.objects.filter(pk=p.get("id"), sent_at__isnull=True).first()
    if row is None:
        raise ActionError("no such reminder")
    return f"Delete reminder {timezone.localtime(row.due_at):%d.%m %H:%M}: «{_shorten(row.text)}»"


def _do_reminder_remove(p):
    Reminder.objects.filter(pk=p["id"]).delete()
    return "reminder deleted"


KINDS = {
    "settings": (_check_settings, _do_settings),
    "project": (_check_project, _do_project),
    "project_visibility": (_check_visibility, _do_visibility),
    "lead": (_check_lead, _do_lead),
    "reply_lead": (_check_reply, _do_reply),
    "messages_read": (_check_messages_read, _do_messages_read),
    "remember": (_check_remember, _do_remember),
    "forget": (_check_forget, _do_forget),
    "reminder": (_check_reminder, _do_reminder),
    "reminder_remove": (_check_reminder_remove, _do_reminder_remove),
}


# ── Public API ──────────────────────────────────────────────────────────────

def propose(ctx, kind, params):
    """Validate and store. Returns what the model should be told."""
    if not ctx.is_owner:
        raise ActionError("not allowed")
    if kind not in KINDS:
        raise ActionError("unknown change")
    check, _do = KINDS[kind]
    summary = check(params)
    action = AiAction.objects.create(
        kind=kind, params=params, summary=summary, channel=ctx.channel,
        expires_at=timezone.now() + timezone.timedelta(minutes=EXPIRES_MINUTES),
    )
    ctx.actions.append(action)
    return {"ok": True, "status": "PENDING_CONFIRMATION - nothing changed yet",
            "action_id": action.pk, "summary": summary,
            "note": "Tell the owner it is ready and ask to confirm. Do not say it is done."}


def as_dict(action):
    return {"id": action.pk, "kind": action.kind, "summary": action.summary, "status": action.status,
            "expires_at": action.expires_at.isoformat(), "result": action.result}


def pending():
    return list(AiAction.objects.filter(status=AiAction.Status.PROPOSED, expires_at__gt=timezone.now())
                .order_by("created_at"))


def confirm(action_id, channel="site"):
    expired = False
    with transaction.atomic():
        action = AiAction.objects.select_for_update().filter(pk=action_id).first()
        if action is None:
            raise ActionError("no such action")
        if action.status != AiAction.Status.PROPOSED:
            raise ActionError(f"already {action.get_status_display().lower()}")
        if action.expires_at <= timezone.now():
            action.status = AiAction.Status.EXPIRED
            action.decided_at = timezone.now()
            action.save(update_fields=["status", "decided_at"])
            expired = True
        else:
            check, do = KINDS[action.kind]
            try:
                check(action.params)          # re-validate: things may have changed meanwhile
                action.result = do(action.params)[:300]
                action.status = AiAction.Status.DONE
            except ActionError as exc:
                action.result, action.status = str(exc)[:300], AiAction.Status.FAILED
            except Exception as exc:
                logger.exception("action %s failed", action.pk)
                action.result = f"{type(exc).__name__}: {exc}"[:300]
                action.status = AiAction.Status.FAILED
            action.decided_at = timezone.now()
            action.save()
    if expired:
        _sync_telegram(action)
        raise ActionError("expired; ask again")
    AiLog.objects.create(channel=channel, role="owner", kind="action", question=action.summary[:500],
                         answer=action.result, ok=action.status == AiAction.Status.DONE, model="-")
    _sync_telegram(action)
    return action


def cancel(action_id, channel="site"):
    with transaction.atomic():
        action = AiAction.objects.select_for_update().filter(pk=action_id).first()
        if action is None:
            raise ActionError("no such action")
        if action.status != AiAction.Status.PROPOSED:
            raise ActionError(f"already {action.get_status_display().lower()}")
        action.status = AiAction.Status.CANCELLED
        action.decided_at = timezone.now()
        action.save(update_fields=["status", "decided_at"])
    _sync_telegram(action)
    return action


def _sync_telegram(action):
    """Update the Telegram confirmation message(s), whichever channel decided."""
    if not action.tg_msgs:
        return
    try:
        from . import telegram
        telegram.update_action_messages(action)
    except Exception as exc:
        logger.warning("could not update telegram action message: %s", exc)
