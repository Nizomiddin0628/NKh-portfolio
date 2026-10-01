"""Changes the assistant prepares, the owner confirms (or auto-applies) and can undo.

    propose()  -> validates, stores an AiAction(PROPOSED), changes nothing;
                  with ctx.auto it applies at once (except ALWAYS_CONFIRM kinds)
    confirm()  -> locks the row, validates again, applies, marks DONE/FAILED
    cancel()   -> marks CANCELLED
    undo()     -> puts the previous value back (DONE actions only), marks UNDONE

Kinds and what they may touch are fixed here in code. Nothing about users,
passwords, keys, the domain or deployment can be changed through the assistant.
"""
import logging
from datetime import date, datetime

from django.conf import settings
from django.core.exceptions import FieldDoesNotExist
from django.core.mail import EmailMessage
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from apps.core.models import ContactMessage, Principle, SiteSettings
from apps.projects.models import CaseSection, Metric, Project, Technology
from apps.resume.models import (
    Award,
    Certificate,
    Education,
    Experience,
    ExperienceBullet,
    LanguageSkill,
    Skill,
    SkillGroup,
)

from .models import AiAction, AiKnowledge, AiLog, Lead, Reminder

logger = logging.getLogger(__name__)
EXPIRES_MINUTES = 30
UNDO_HOURS = 48
LANGS = ("en", "uz", "ru")

SETTINGS_TRANSLATED = ("headline", "intro", "about", "availability_note", "work_philosophy", "meta_description")
SETTINGS_PLAIN = ("job_title", "location", "availability", "full_name", "email", "phone", "github_username")
PROJECT_TRANSLATED = ("tagline", "role", "summary", "context")
PROJECT_PLAIN = ("title", "status", "organisation", "order", "is_featured", "live_url", "repo_url",
                 "is_confidential", "year_started", "year_finished", "team_size")

# Rows the generic item editor may touch: key -> (model, translated fields, plain fields, parent)
ITEMS = {
    "section": (CaseSection, ("heading", "body"), ("kind", "order"), "project"),
    "metric": (Metric, ("label", "note"), ("value_before", "value_after", "order"), "project"),
    "experience": (Experience, ("role", "employment_type", "summary"),
                   ("company", "company_url", "location", "start_date", "end_date", "order", "is_published"), None),
    "bullet": (ExperienceBullet, ("text",), ("order",), "experience"),
    "education": (Education, ("degree", "field_of_study", "note"),
                  ("institution", "institution_url", "location", "start_year", "end_year", "grade", "order"), None),
    "skill_group": (SkillGroup, ("name", "note"), ("order",), None),
    "skill": (Skill, (), ("name", "depth", "order"), "group"),
    "language": (LanguageSkill, ("name", "level"), ("order",), None),
    "award": (Award, ("title", "description"), ("issuer", "year", "url", "order"), None),
    "certificate": (Certificate, ("title",), ("order", "is_published"), None),
    "principle": (Principle, ("title", "body"), ("order", "is_published"), None),
}
# Which items may be created and removed by the assistant (and what a new one needs)
ADDABLE = {"section": "project", "metric": "project", "bullet": "experience", "skill": "group",
           "language": None, "award": None, "principle": None}
# Changes that always wait for a tap, even in auto mode: they leave the site or are hard to reverse
ALWAYS_CONFIRM = ("reply_lead",)


class ActionError(Exception):
    pass


def _max_len(model, field):
    f = model._meta.get_field(field)
    return getattr(f, "max_length", None)


def _shorten(text, n=70):
    text = " ".join(str(text).split())
    return text if len(text) <= n else text[: n - 1] + "…"


def _coerce(model, attr, value):
    """Turn the model's string into what the field stores; raise ActionError on nonsense."""
    try:
        f = model._meta.get_field(attr)
    except FieldDoesNotExist as exc:
        raise ActionError(f"field {attr} does not exist") from exc
    kind = f.get_internal_type()
    raw = "" if value is None else str(value).strip()
    if kind in ("BooleanField",):
        return raw.lower() in ("1", "true", "yes", "ha", "da", "on")
    if kind in ("PositiveSmallIntegerField", "IntegerField", "PositiveIntegerField", "SmallIntegerField"):
        if raw == "" and f.null:
            return None
        try:
            return int(raw)
        except ValueError as exc:
            raise ActionError(f"{attr} must be a whole number") from exc
    if kind == "DateField":
        if raw == "" and f.null:
            return None
        try:
            return date.fromisoformat(raw[:10])
        except ValueError as exc:
            raise ActionError(f"{attr} must be a date like 2026-01-31") from exc
    if f.choices:
        allowed = [c[0] for c in f.choices]
        if raw not in allowed:
            raise ActionError(f"{attr} must be one of: {', '.join(allowed)}")
        return raw
    if kind == "URLField" and raw and not raw.startswith(("http://", "https://")):
        raise ActionError(f"{attr} must start with https://")
    limit = getattr(f, "max_length", None)
    if limit and len(raw) > limit:
        raise ActionError(f"too long: max {limit} characters")
    return raw


def _display(value):
    if isinstance(value, bool):
        return "yes" if value else "no"
    return "" if value is None else str(value)


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
    else:
        raise ActionError(f"field {field} cannot be changed here")
    p["value"] = value = _coerce(SiteSettings, attr, value)
    old = getattr(conf, attr, "")
    p["attr"], p["old"] = attr, _display(old)
    return f"Site {attr}: «{_shorten(old)}» → «{_shorten(value)}»"


def _do_settings(p):
    conf = SiteSettings.load()
    setattr(conf, p["attr"], p["value"])
    conf.save(update_fields=[p["attr"], "updated_at"])
    return f"{p['attr']} updated"


def _undo_settings(p):
    conf = SiteSettings.load()
    setattr(conf, p["attr"], _coerce(SiteSettings, p["attr"], p.get("old", "")))
    conf.save(update_fields=[p["attr"], "updated_at"])


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
    else:
        raise ActionError(f"field {field} cannot be changed here")
    p["value"] = value = _coerce(Project, attr, value)
    old = getattr(project, attr, "")
    p["attr"], p["old"] = attr, _display(old)
    return f"Project {project.title} — {attr}: «{_shorten(old)}» → «{_shorten(value)}»"


def _do_project(p):
    project = Project.objects.get(slug=p["slug"])
    setattr(project, p["attr"], p["value"])
    project.save(update_fields=[p["attr"], "updated_at"])
    return f"{project.title}: {p['attr']} updated"


def _undo_project(p):
    project = Project.objects.get(slug=p["slug"])
    setattr(project, p["attr"], _coerce(Project, p["attr"], p.get("old", "")))
    project.save(update_fields=[p["attr"], "updated_at"])


def _check_visibility(p):
    project = Project.objects.filter(slug=p.get("slug", "")).first()
    if project is None:
        raise ActionError("no such project")
    p["old"] = project.is_published
    state = "published" if p.get("published") else "hidden"
    return f"Project {project.title}: {state}"


def _do_visibility(p):
    project = Project.objects.get(slug=p["slug"])
    project.is_published = bool(p.get("published"))
    project.save(update_fields=["is_published", "updated_at"])
    return "visibility updated"


def _undo_visibility(p):
    Project.objects.filter(slug=p["slug"]).update(is_published=bool(p.get("old", True)))


# ── Generic rows: sections, metrics, experience, skills, ... ────────────────

def _item(p):
    key = p.get("item", "")
    if key not in ITEMS:
        raise ActionError(f"item must be one of: {', '.join(ITEMS)}")
    model, translated, plain, parent = ITEMS[key]
    row = model.objects.filter(pk=p.get("id")).first()
    if row is None:
        raise ActionError(f"no {key} with id {p.get('id')}")
    return key, model, translated, plain, row


def _label(key, row):
    if key == "section":
        return f"{row.project.title} / {row.title}"
    if key == "metric":
        return f"{row.project.title} / {row.label_en}"
    if key == "bullet":
        return f"{row.experience.company} / {_shorten(row.text_en, 40)}"
    if key == "skill":
        return f"{row.group.name_en} / {row.name}"
    if key == "experience":
        return f"{row.company} — {row.role_en}"
    return _shorten(str(row), 60)


def _check_item(p):
    key, model, translated, plain, row = _item(p)
    field, lang = p.get("field", ""), p.get("lang", "")
    if field in translated:
        if lang not in LANGS:
            raise ActionError("lang must be en, uz or ru for this field")
        attr = f"{field}_{lang}"
    elif field in plain:
        attr = field
    else:
        raise ActionError(f"{key} has no editable field {field}; use: {', '.join(translated + plain)}")
    p["value"] = value = _coerce(model, attr, p.get("value", ""))
    old = getattr(row, attr, "")
    p["attr"], p["old"] = attr, _display(old)
    return f"{key} #{row.pk} ({_label(key, row)}) — {attr}: «{_shorten(old)}» → «{_shorten(value)}»"


def _do_item(p):
    key, model, _t, _p, row = _item(p)
    setattr(row, p["attr"], p["value"])
    row.save()
    return f"{key} #{row.pk}: {p['attr']} updated"


def _undo_item(p):
    key, model, _t, _p, row = _item(p)
    setattr(row, p["attr"], _coerce(model, p["attr"], p.get("old", "")))
    row.save()


def _check_item_add(p):
    key = p.get("item", "")
    if key not in ADDABLE:
        raise ActionError(f"item must be one of: {', '.join(ADDABLE)}")
    model, translated, plain, parent = ITEMS[key]
    fields = p.get("fields") or {}
    if not isinstance(fields, dict) or not fields:
        raise ActionError("fields is empty")
    clean = {}
    for name, value in fields.items():
        base = name.rsplit("_", 1)[0] if name.rsplit("_", 1)[-1] in LANGS else name
        if base in translated and name != base:
            attr = name
        elif base in translated:
            attr = f"{base}_en"
        elif name in plain:
            attr = name
        else:
            raise ActionError(f"{key} has no field {name}; use: {', '.join(translated + plain)}")
        clean[attr] = _coerce(model, attr, value)
    if parent:
        if key in ("section", "metric"):
            proj = Project.objects.filter(slug=p.get("parent", "")).first()
            if proj is None:
                raise ActionError("parent must be a project slug")
            p["parent_pk"] = proj.pk
            where = proj.title
        else:
            pm = ITEMS[parent][0] if parent in ITEMS else {"experience": Experience, "group": SkillGroup}[parent]
            par = pm.objects.filter(pk=p.get("parent")).first()
            if par is None:
                raise ActionError(f"parent must be an existing {parent} id")
            p["parent_pk"] = par.pk
            where = _shorten(str(par), 40)
    else:
        where = "resume"
    required = [f for f in model._meta.fields if not f.blank and not f.null and f.name not in ("id",)
                and f.name != parent and not f.has_default() and f.get_internal_type() != "AutoField"]
    missing = [f.name for f in required if f.name not in clean]
    if missing:
        raise ActionError(f"required for a new {key}: {', '.join(missing)}")
    p["clean"] = {k: (v.isoformat() if isinstance(v, date) else v) for k, v in clean.items()}
    shown = "; ".join(f"{k}={_shorten(v, 40)}" for k, v in clean.items())
    return f"Add {key} to {where}: {shown}"


def _do_item_add(p):
    key = p["item"]
    model, _t, _p, parent = ITEMS[key]
    data = {k: _coerce(model, k, v) for k, v in p["clean"].items()}
    if parent:
        data[f"{parent}_id"] = p["parent_pk"]
    row = model.objects.create(**data)
    p["created_pk"] = row.pk
    return f"{key} #{row.pk} added"


def _undo_item_add(p):
    ITEMS[p["item"]][0].objects.filter(pk=p.get("created_pk")).delete()


def _check_item_remove(p):
    key = p.get("item", "")
    if key not in ADDABLE:
        raise ActionError(f"item must be one of: {', '.join(ADDABLE)}")
    key, model, translated, plain, row = _item(p)
    snapshot = {}
    for f in model._meta.fields:
        if f.name == "id" or f.get_internal_type() in ("FileField", "ImageField"):
            continue
        v = getattr(row, f.attname)
        snapshot[f.attname] = v.isoformat() if isinstance(v, (date, datetime)) else v
    p["snapshot"] = snapshot
    return f"Remove {key} #{row.pk} ({_label(key, row)})"


def _do_item_remove(p):
    key, model, _t, _p, row = _item(p)
    row.delete()
    return f"{key} #{p['id']} removed"


def _undo_item_remove(p):
    model = ITEMS[p["item"]][0]
    data = {}
    for attname, v in p["snapshot"].items():
        f = model._meta.get_field(attname[:-3] if attname.endswith("_id") and attname != "id" else attname)
        if f.get_internal_type() == "DateField" and v:
            v = date.fromisoformat(v)
        data[attname] = v
    model.objects.create(pk=p["id"], **data)


def _check_project_tech(p):
    project = Project.objects.filter(slug=p.get("slug", "")).first()
    if project is None:
        raise ActionError("no such project")
    add = [str(n).strip() for n in (p.get("add") or []) if str(n).strip()][:20]
    remove = [str(n).strip() for n in (p.get("remove") or []) if str(n).strip()][:20]
    if not add and not remove:
        raise ActionError("nothing to add or remove")
    have = {t.name.lower(): t.name for t in project.technologies.all()}
    remove = [have[n.lower()] for n in remove if n.lower() in have]
    add = [n for n in add if n.lower() not in have]
    p["add"], p["remove"] = add, remove
    bits = (["+ " + ", ".join(add)] if add else []) + (["− " + ", ".join(remove)] if remove else [])
    return f"Project {project.title} technologies: " + "; ".join(bits)


def _do_project_tech(p):
    project = Project.objects.get(slug=p["slug"])
    created = []
    for name in p["add"]:
        tech = Technology.objects.filter(name__iexact=name).first()
        if tech is None:
            base = slugify(name)[:56] or f"t-{project.pk}"
            slug, n = base, 2
            while Technology.objects.filter(slug=slug).exists():
                slug, n = f"{base}-{n}", n + 1
            tech = Technology.objects.create(name=name[:60], slug=slug)
            created.append(tech.pk)
        project.technologies.add(tech)
    for name in p["remove"]:
        tech = Technology.objects.filter(name__iexact=name).first()
        if tech:
            project.technologies.remove(tech)
    p["created"] = created
    return "technologies updated"


def _undo_project_tech(p):
    project = Project.objects.get(slug=p["slug"])
    for name in p["add"]:
        tech = Technology.objects.filter(name__iexact=name).first()
        if tech:
            project.technologies.remove(tech)
    for name in p["remove"]:
        tech = Technology.objects.filter(name__iexact=name).first()
        if tech:
            project.technologies.add(tech)
    Technology.objects.filter(pk__in=p.get("created", []), projects__isnull=True).delete()


# ── Leads, messages, knowledge, reminders ────────────────────────────────────

def _check_lead(p):
    lead = Lead.objects.filter(pk=p.get("id")).first()
    if lead is None:
        raise ActionError("no such lead")
    status = p.get("status") or ""
    if status and status not in ("new", "contacted", "closed"):
        raise ActionError("status must be new, contacted or closed")
    if not status and not p.get("note"):
        raise ActionError("nothing to change")
    p["old"] = {"status": lead.status, "note": lead.note}
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


def _undo_lead(p):
    Lead.objects.filter(pk=p["id"]).update(**p.get("old", {}))


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
    p["marked"] = list(qs.values_list("pk", flat=True))
    return f"{qs.update(is_read=True)} marked read"


def _undo_messages_read(p):
    ContactMessage.objects.filter(pk__in=p.get("marked", [])).update(is_read=False)


def _check_remember(p):
    text = p.get("text", "").strip()
    if len(text) < 5:
        raise ActionError("the fact is too short")
    return f"Remember: «{_shorten(text, 120)}»"


def _do_remember(p):
    row = AiKnowledge.objects.create(text=p["text"].strip(), source="assistant")
    p["created_pk"] = row.pk
    from .state import invalidate
    invalidate()
    return "fact saved"


def _undo_remember(p):
    AiKnowledge.objects.filter(pk=p.get("created_pk")).delete()
    from .state import invalidate
    invalidate()


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


def _undo_forget(p):
    AiKnowledge.objects.filter(pk=p["id"]).update(is_active=True)
    from .state import invalidate
    invalidate()


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
    row = Reminder.objects.create(text=p["text"].strip(), due_at=_parse_due(p["due"]))
    p["created_pk"] = row.pk
    return "reminder saved"


def _undo_reminder(p):
    Reminder.objects.filter(pk=p.get("created_pk"), sent_at__isnull=True).delete()


def _check_reminder_remove(p):
    row = Reminder.objects.filter(pk=p.get("id"), sent_at__isnull=True).first()
    if row is None:
        raise ActionError("no such reminder")
    p["old"] = {"text": row.text, "due_at": row.due_at.isoformat()}
    return f"Delete reminder {timezone.localtime(row.due_at):%d.%m %H:%M}: «{_shorten(row.text)}»"


def _do_reminder_remove(p):
    Reminder.objects.filter(pk=p["id"]).delete()
    return "reminder deleted"


def _undo_reminder_remove(p):
    old = p.get("old") or {}
    if old:
        Reminder.objects.create(pk=p["id"], text=old["text"], due_at=datetime.fromisoformat(old["due_at"]))


KINDS = {
    "settings": (_check_settings, _do_settings, _undo_settings),
    "project": (_check_project, _do_project, _undo_project),
    "project_visibility": (_check_visibility, _do_visibility, _undo_visibility),
    "project_tech": (_check_project_tech, _do_project_tech, _undo_project_tech),
    "item": (_check_item, _do_item, _undo_item),
    "item_add": (_check_item_add, _do_item_add, _undo_item_add),
    "item_remove": (_check_item_remove, _do_item_remove, _undo_item_remove),
    "lead": (_check_lead, _do_lead, _undo_lead),
    "reply_lead": (_check_reply, _do_reply, None),
    "messages_read": (_check_messages_read, _do_messages_read, _undo_messages_read),
    "remember": (_check_remember, _do_remember, _undo_remember),
    "forget": (_check_forget, _do_forget, _undo_forget),
    "reminder": (_check_reminder, _do_reminder, _undo_reminder),
    "reminder_remove": (_check_reminder_remove, _do_reminder_remove, _undo_reminder_remove),
}


# ── Public API ──────────────────────────────────────────────────────────────

def propose(ctx, kind, params):
    """Validate and store. Returns what the model should be told.

    In auto mode (Telegram, owner's choice) the change is applied right away and
    the model is told it is DONE; the chat then shows an undo button.
    """
    if not ctx.is_owner:
        raise ActionError("not allowed")
    if kind not in KINDS:
        raise ActionError("unknown change")
    check, _do, _undo = KINDS[kind]
    summary = check(params)
    action = AiAction.objects.create(
        kind=kind, params=params, summary=summary, channel=ctx.channel,
        expires_at=timezone.now() + timezone.timedelta(minutes=EXPIRES_MINUTES),
    )
    ctx.actions.append(action)
    if getattr(ctx, "auto", False) and kind not in ALWAYS_CONFIRM:
        try:
            confirm(action.pk, channel=ctx.channel, sync=False)
        except ActionError:
            pass
        action.refresh_from_db()
        if action.status == AiAction.Status.DONE:
            return {"ok": True, "status": "DONE", "action_id": action.pk, "summary": summary,
                    "result": action.result, "note": "Applied. Tell the owner what changed (he can undo it with the button)."}
        return {"ok": False, "status": "FAILED", "action_id": action.pk, "error": action.result}
    return {"ok": True, "status": "PENDING_CONFIRMATION - nothing changed yet",
            "action_id": action.pk, "summary": summary,
            "note": "Tell the owner it is ready and ask to confirm. Do not say it is done."}


def as_dict(action):
    return {"id": action.pk, "kind": action.kind, "summary": action.summary, "status": action.status,
            "expires_at": action.expires_at.isoformat(), "result": action.result,
            "undoable": can_undo(action)}


def can_undo(action):
    return (action.status == AiAction.Status.DONE and KINDS.get(action.kind, (None, None, None))[2] is not None
            and action.decided_at is not None
            and timezone.now() - action.decided_at < timezone.timedelta(hours=UNDO_HOURS))


def pending():
    return list(AiAction.objects.filter(status=AiAction.Status.PROPOSED, expires_at__gt=timezone.now())
                .order_by("created_at"))


def confirm(action_id, channel="site", sync=True):
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
            check, do, _undo = KINDS[action.kind]
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
        if sync:
            _sync_telegram(action)
        raise ActionError("expired; ask again")
    if action.status == AiAction.Status.DONE:
        from .state import invalidate
        invalidate()                    # the assistant's CURRENT STATE must show the change at once
    AiLog.objects.create(channel=channel, role="owner", kind="action", question=action.summary[:500],
                         answer=action.result, ok=action.status == AiAction.Status.DONE, model="-")
    if sync:
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


def undo(action_id, channel="site"):
    """Put back what a DONE action changed (within UNDO_HOURS)."""
    with transaction.atomic():
        action = AiAction.objects.select_for_update().filter(pk=action_id).first()
        if action is None:
            raise ActionError("no such action")
        if not can_undo(action):
            raise ActionError("this change cannot be undone any more")
        _check, _do, undo_fn = KINDS[action.kind]
        try:
            undo_fn(action.params)
        except ActionError:
            raise
        except Exception as exc:
            logger.exception("undo %s failed", action.pk)
            raise ActionError(f"undo failed: {type(exc).__name__}") from exc
        action.status = AiAction.Status.UNDONE
        action.result = "undone"
        action.save(update_fields=["status", "result"])
    from .state import invalidate
    invalidate()
    AiLog.objects.create(channel=channel, role="owner", kind="action", question=f"[undo] {action.summary[:490]}",
                         answer="undone", ok=True, model="-")
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
