"""Tools the model may call. Each one is a plain function plus a declaration.

Guests get read-only tools and `save_lead`. Owner tools are declared only
for the owner, and `run()` checks the role again before running anything.
Changing tools never change data directly: they create an AiAction that
waits for the owner's confirmation (see actions.py).
"""
import re
from dataclasses import dataclass, field

from django.db.models import Q, Sum
from django.utils import timezone, translation

from apps.core.models import ContactMessage, DailyVisitor, PageView, SiteSettings
from apps.projects.models import Project, Technology
from apps.resume.models import Award, Certificate, Education, Experience, LanguageSkill, SkillGroup

from . import actions
from .models import AiKnowledge, AiLog, Lead, Reminder
from .state import project_url

TOOLS = {}


@dataclass
class Ctx:
    role: str = "guest"          # guest | owner
    channel: str = "site"        # site | telegram
    lang: str = "en"
    session: str = ""
    page: str = ""
    ip_hash: str = ""
    history: list = field(default_factory=list)   # [{"role","text"}] for lead transcripts
    question: str = ""
    actions: list = field(default_factory=list)   # AiAction objects created in this turn
    leads: list = field(default_factory=list)
    used: list = field(default_factory=list)

    @property
    def is_owner(self):
        return self.role == "owner"


def tool(name, description, properties=None, required=(), owner=False):
    def deco(fn):
        TOOLS[name] = {
            "fn": fn, "owner": owner,
            "decl": {"name": name, "description": description,
                     "parameters": {"type": "object", "properties": properties or {},
                                    "required": list(required)}},
        }
        return fn
    return deco


def available(ctx):
    """Declarations for this role. Guests never even see the owner tools."""
    return [t["decl"] for t in TOOLS.values() if ctx.is_owner or not t["owner"]]


def run(ctx, name, args):
    t = TOOLS.get(name)
    if t is None:
        return {"ok": False, "error": f"unknown tool {name}"}
    if t["owner"] and not ctx.is_owner:
        return {"ok": False, "error": "not allowed"}
    ctx.used.append(name)
    try:
        return t["fn"](ctx, **(args or {}))
    except TypeError as exc:
        return {"ok": False, "error": f"bad arguments: {exc}"}
    except actions.ActionError as exc:
        return {"ok": False, "error": str(exc)}
    except Exception as exc:  # the model gets a readable error, the log gets the trace
        import logging
        logging.getLogger(__name__).exception("tool %s failed", name)
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"[:200]}


def _s(v, n=300):
    return (str(v) if v is not None else "").strip()[:n]


# ── Read-only tools (everyone) ──────────────────────────────────────────────

def _project_row(p, lang, full=False):
    with translation.override(lang):
        row = {
            "title": p.title, "slug": p.slug, "tagline": p.tr("tagline"), "role": p.tr("role"),
            "status": p.get_status_display(), "period": p.period, "organisation": p.organisation,
            "technologies": [t.name for t in p.technologies.all()],
            "url": project_url(p.slug, lang),
            "source_code": "private" if p.is_confidential else (p.repo_url or "not listed"),
        }
        if p.live_url:
            row["live_url"] = p.live_url
        if full:
            row["summary"] = p.tr("summary")
            row["context"] = p.tr("context")
            row["team_size"] = p.team_size
            row["sections"] = [{"heading": s.title, "text": s.tr("body")} for s in p.sections.all()]
            row["metrics"] = [{"label": m.tr("label"), "before": m.value_before, "after": m.value_after,
                               "note": m.tr("note")} for m in p.metrics.all()]
            row["images"] = [i.tr("alt_text") for i in p.images.all()[:6]]
        return row


@tool("projects", "List Nizomiddin's published projects, optionally filtered by a keyword "
      "(title, tagline, summary) or a technology name. Use this before recommending a project.",
      {"query": {"type": "string", "description": "keyword to search, optional"},
       "technology": {"type": "string", "description": "technology name, e.g. YOLO, Django"},
       "limit": {"type": "integer", "description": "max rows, default 12"}})
def projects(ctx, query="", technology="", limit=12):
    qs = Project.objects.filter(is_published=True).prefetch_related("technologies")
    if query:
        q = _s(query, 80)
        qs = qs.filter(Q(title__icontains=q) | Q(slug__icontains=q) | Q(tagline_en__icontains=q)
                       | Q(tagline_uz__icontains=q) | Q(tagline_ru__icontains=q)
                       | Q(summary_en__icontains=q) | Q(summary_uz__icontains=q)
                       | Q(summary_ru__icontains=q) | Q(technologies__name__icontains=q)).distinct()
    if technology:
        qs = qs.filter(technologies__name__icontains=_s(technology, 40)).distinct()
    rows = [_project_row(p, ctx.lang) for p in qs[: max(1, min(int(limit or 12), 30))]]
    return {"ok": True, "count": len(rows), "projects": rows}


@tool("project_detail", "Full case study of one project: summary, context, sections (problem, "
      "decisions, architecture, outcome), metrics and technologies.",
      {"slug": {"type": "string", "description": "project slug from the projects list"}}, ("slug",))
def project_detail(ctx, slug=""):
    p = (Project.objects.filter(is_published=True, slug=_s(slug, 160))
         .prefetch_related("technologies", "sections", "metrics", "images").first())
    if p is None:
        return {"ok": False, "error": "no such project"}
    return {"ok": True, "project": _project_row(p, ctx.lang, full=True)}


@tool("resume", "Nizomiddin's resume: experience with bullet points, education, skills, languages, "
      "certificates and awards.",
      {"section": {"type": "string",
                   "description": "all | experience | education | skills | languages | certificates | awards"}})
def resume(ctx, section="all"):
    section = _s(section, 20) or "all"
    out = {"ok": True}
    with translation.override(ctx.lang):
        if section in ("all", "experience"):
            out["experience"] = [{
                "role": e.tr("role"), "company": e.company, "location": e.location,
                "type": e.tr("employment_type"), "from": f"{e.start_date:%Y-%m}",
                "to": f"{e.end_date:%Y-%m}" if e.end_date else "present",
                "summary": e.tr("summary"), "bullets": [b.tr("text") for b in e.bullets.all()],
            } for e in Experience.objects.filter(is_published=True).prefetch_related("bullets")]
        if section in ("all", "education"):
            out["education"] = [{
                "degree": e.tr("degree"), "field": e.tr("field_of_study"), "institution": e.institution,
                "years": f"{e.start_year or ''}–{e.end_year or ''}", "grade": e.grade, "note": e.tr("note"),
            } for e in Education.objects.all()]
        if section in ("all", "skills"):
            out["skills"] = [{"group": g.tr("name"), "note": g.tr("note"),
                              "items": [f"{s.name} ({s.get_depth_display()})" for s in g.skills.all()]}
                             for g in SkillGroup.objects.prefetch_related("skills")]
        if section in ("all", "languages"):
            out["languages"] = [f"{x.tr('name')}: {x.tr('level')}" for x in LanguageSkill.objects.all()]
        if section in ("all", "certificates"):
            out["certificates"] = [c.tr("title") for c in Certificate.objects.filter(is_published=True)]
        if section in ("all", "awards"):
            out["awards"] = [{"title": a.tr("title"), "issuer": a.issuer, "year": a.year,
                              "description": a.tr("description")} for a in Award.objects.all()]
    return out


@tool("site_info", "Site owner's profile: name, title, location, headline, intro, about text, "
      "availability and contacts.")
def site_info(ctx):
    with translation.override(ctx.lang):
        c = SiteSettings.load()
        return {"ok": True, "name": c.full_name, "title": c.job_title, "location": c.location,
                "headline": c.tr("headline"), "intro": c.tr("intro"), "about": c.tr("about")[:3000],
                "how_i_work": c.tr("work_philosophy")[:2000],
                "availability": c.get_availability_display(), "availability_note": c.tr("availability_note"),
                "email": c.email, "phone": c.phone}


@tool("search_knowledge", "Search the facts the owner taught the assistant (things not on the site).",
      {"query": {"type": "string"}}, ("query",))
def search_knowledge(ctx, query=""):
    words = [w for w in re.split(r"\W+", _s(query, 80)) if len(w) > 2][:6]
    qs = AiKnowledge.objects.filter(is_active=True)
    if words:
        cond = Q()
        for w in words:
            cond |= Q(text__icontains=w)
        qs = qs.filter(cond)
    return {"ok": True, "facts": [r.text for r in qs[:10]]}


CONTACT_OK = re.compile(r"(@[A-Za-z0-9_]{4,32}|[\w.+-]+@[\w-]+\.[\w.]+|\+?[\d\s()\-]{7,20})")


@tool("save_lead", "Save a visitor's request so Nizomiddin can reply. Call it ONCE, only after the visitor "
      "gave (1) what they need and (2) a contact: email, Telegram username or phone.",
      {"name": {"type": "string"}, "contact": {"type": "string", "description": "email, @telegram or phone"},
       "need": {"type": "string", "description": "what they want to build, in their words, 1-3 sentences"},
       "timeline": {"type": "string"}, "budget": {"type": "string"}},
      ("contact", "need"))
def save_lead(ctx, name="", contact="", need="", timeline="", budget=""):
    contact, need = _s(contact, 200), _s(need, 2000)
    if not CONTACT_OK.search(contact):
        return {"ok": False, "error": "contact does not look like an email, @username or phone; ask again"}
    if len(need) < 10:
        return {"ok": False, "error": "need is too short; ask what they want to build"}
    transcript = "\n".join(f"{m.get('role', '?')}: {m.get('text', '')}" for m in ctx.history[-16:])
    if ctx.question:
        transcript += f"\nuser: {ctx.question}"
    lead = None
    if ctx.session:
        recent = timezone.now() - timezone.timedelta(hours=2)
        lead = Lead.objects.filter(session=ctx.session, created_at__gte=recent).first()
    if lead is None:
        lead = Lead(session=ctx.session, ip_hash=ctx.ip_hash, lang=ctx.lang, page=ctx.page[:300])
    lead.name, lead.contact, lead.need = _s(name, 120), contact, need
    lead.timeline, lead.budget, lead.transcript = _s(timeline, 120), _s(budget, 120), transcript[:8000]
    lead.save()
    ctx.leads.append(lead)
    AiLog.objects.create(channel=ctx.channel, role=ctx.role, kind="ask", lang=ctx.lang,
                         question=f"[lead] {contact}", answer=need[:500], ip_hash=ctx.ip_hash,
                         session=ctx.session, model="-", tools_used="save_lead")
    from .notify import lead_created
    lead_created(lead)
    return {"ok": True, "saved": True, "lead_id": lead.pk,
            "note": "Tell the visitor Nizomiddin received it and will reply personally. Do not ask more."}


# ── Owner: reading ───────────────────────────────────────────────────────────

def _lead_row(ld, full=False):
    row = {"id": ld.pk, "name": ld.name, "contact": ld.contact, "need": ld.need[:400],
           "timeline": ld.timeline, "budget": ld.budget, "lang": ld.lang, "status": ld.status,
           "created": f"{timezone.localtime(ld.created_at):%Y-%m-%d %H:%M}", "note": ld.note[:200]}
    if full:
        row["transcript"] = ld.transcript[:4000]
        row["page"] = ld.page
    return row


@tool("leads", "Leads (visitor requests) collected by the assistant, newest first.",
      {"status": {"type": "string", "description": "new | contacted | closed | all (default new+contacted)"},
       "query": {"type": "string"}, "limit": {"type": "integer"}}, owner=True)
def leads(ctx, status="", query="", limit=10):
    qs = Lead.objects.all()
    status = _s(status, 10)
    if status in ("new", "contacted", "closed"):
        qs = qs.filter(status=status)
    elif status != "all":
        qs = qs.exclude(status="closed")
    if query:
        q = _s(query, 80)
        qs = qs.filter(Q(name__icontains=q) | Q(contact__icontains=q) | Q(need__icontains=q))
    rows = [_lead_row(ld) for ld in qs[: max(1, min(int(limit or 10), 30))]]
    return {"ok": True, "count": len(rows), "new_total": Lead.objects.filter(status="new").count(),
            "leads": rows}


@tool("lead_detail", "One lead with the full conversation transcript.",
      {"id": {"type": "integer"}}, ("id",), owner=True)
def lead_detail(ctx, id=0):
    ld = Lead.objects.filter(pk=int(id)).first()
    return {"ok": True, "lead": _lead_row(ld, full=True)} if ld else {"ok": False, "error": "no such lead"}


@tool("messages", "Messages sent through the site's contact form.",
      {"unread_only": {"type": "boolean"}, "limit": {"type": "integer"}}, owner=True)
def messages(ctx, unread_only=True, limit=10):
    qs = ContactMessage.objects.all()
    if unread_only:
        qs = qs.filter(is_read=False)
    rows = [{"id": m.pk, "name": m.name, "email": m.email, "phone": m.phone, "subject": m.subject,
             "message": m.message[:600], "lang": m.language, "read": m.is_read,
             "created": f"{timezone.localtime(m.created_at):%Y-%m-%d %H:%M}"}
            for m in qs[: max(1, min(int(limit or 10), 30))]]
    return {"ok": True, "count": len(rows), "unread_total": ContactMessage.objects.filter(is_read=False).count(),
            "messages": rows}


@tool("stats", "Site statistics for the last N days: visitors, page views, top pages, devices, referrers.",
      {"days": {"type": "integer", "description": "1-90, default 7"}}, owner=True)
def stats(ctx, days=7):
    days = max(1, min(int(days or 7), 90))
    since = timezone.localdate() - timezone.timedelta(days=days - 1)
    visitors = DailyVisitor.objects.filter(date__gte=since)
    views = PageView.objects.filter(date__gte=since)
    top = list(views.values("path").annotate(n=Sum("count")).order_by("-n")[:8])
    devices = {}
    for d in visitors.values_list("device", flat=True):
        devices[d or "unknown"] = devices.get(d or "unknown", 0) + 1
    refs = {}
    for r in visitors.exclude(referrer="").values_list("referrer", flat=True):
        refs[r] = refs.get(r, 0) + 1
    by_day = {}
    for d in visitors.values_list("date", flat=True):
        by_day[str(d)] = by_day.get(str(d), 0) + 1
    return {"ok": True, "days": days, "since": str(since),
            "visitors": visitors.count(), "page_views": views.aggregate(n=Sum("count"))["n"] or 0,
            "visitors_by_day": by_day, "top_pages": [{"path": t["path"], "views": t["n"]} for t in top],
            "devices": devices, "referrers": sorted(refs.items(), key=lambda x: -x[1])[:8],
            "ai_questions": AiLog.objects.filter(created_at__date__gte=since, role="guest").count(),
            "leads": Lead.objects.filter(created_at__date__gte=since).count(),
            "messages": ContactMessage.objects.filter(created_at__date__gte=since).count()}


@tool("guest_questions", "What visitors asked the assistant recently; unanswered ones are questions "
      "the assistant had no facts for (good candidates for remember_fact).",
      {"days": {"type": "integer"}, "unanswered_only": {"type": "boolean"}, "limit": {"type": "integer"}},
      owner=True)
def guest_questions(ctx, days=1, unanswered_only=False, limit=20):
    since = timezone.now() - timezone.timedelta(days=max(1, min(int(days or 1), 30)))
    qs = AiLog.objects.filter(role="guest", kind__in=("ask", "voice", "file"), created_at__gte=since,
                              ok=True).exclude(question="")
    if unanswered_only:
        qs = qs.filter(unanswered=True)
    rows = [{"when": f"{timezone.localtime(r.created_at):%m-%d %H:%M}", "lang": r.lang,
             "question": r.question[:200], "answer": r.answer[:200], "unanswered": r.unanswered}
            for r in qs[: max(1, min(int(limit or 20), 50))]]
    return {"ok": True, "count": len(rows), "questions": rows}


@tool("report", "The daily/weekly report: visitors, leads, messages, assistant usage, pending actions, "
      "reminders. Use it when asked for a report or summary.",
      {"period": {"type": "string", "description": "today | yesterday | week"}}, owner=True)
def report(ctx, period="today"):
    from .digest import build_report
    return {"ok": True, **build_report(_s(period, 10) or "today")}


@tool("reminders", "List reminders that have not been sent yet.", owner=True)
def reminders(ctx):
    rows = [{"id": r.pk, "due": f"{timezone.localtime(r.due_at):%Y-%m-%d %H:%M}", "text": r.text}
            for r in Reminder.objects.filter(sent_at__isnull=True)[:30]]
    return {"ok": True, "reminders": rows}


@tool("knowledge_list", "Facts the owner taught the assistant, with ids.", owner=True)
def knowledge_list(ctx):
    return {"ok": True, "facts": [{"id": r.pk, "text": r.text} for r in AiKnowledge.objects.filter(is_active=True)[:60]]}


@tool("technologies", "Technology names known to the site (for filtering projects).", owner=False)
def technologies(ctx):
    return {"ok": True, "technologies": list(Technology.objects.values_list("name", flat=True))}


# ── Owner: changes (all go through confirmation) ────────────────────────────

def _propose(ctx, kind, params):
    return actions.propose(ctx, kind, params)


@tool("update_settings", "PREPARE a change of a site text or setting (needs confirmation). "
      "Translated fields need lang: headline, intro, about, availability_note, work_philosophy, "
      "meta_description. Plain fields: job_title, location, availability (open|selective|busy).",
      {"field": {"type": "string"}, "value": {"type": "string"},
       "lang": {"type": "string", "description": "en | uz | ru for translated fields"}},
      ("field", "value"), owner=True)
def update_settings(ctx, field="", value="", lang=""):
    return _propose(ctx, "settings", {"field": _s(field, 40), "value": _s(value, 5000), "lang": _s(lang, 2)})


@tool("update_project", "PREPARE a change of one project field (needs confirmation). Translated fields "
      "need lang: tagline, role, summary, context. Plain: title, status (production|research|wip|archived), "
      "organisation, order, is_featured (true|false), live_url.",
      {"slug": {"type": "string"}, "field": {"type": "string"}, "value": {"type": "string"},
       "lang": {"type": "string"}}, ("slug", "field", "value"), owner=True)
def update_project(ctx, slug="", field="", value="", lang=""):
    return _propose(ctx, "project", {"slug": _s(slug, 160), "field": _s(field, 40),
                                     "value": _s(value, 5000), "lang": _s(lang, 2)})


@tool("set_project_visibility", "PREPARE publishing or hiding a project (needs confirmation).",
      {"slug": {"type": "string"}, "published": {"type": "boolean"}}, ("slug", "published"), owner=True)
def set_project_visibility(ctx, slug="", published=True):
    return _propose(ctx, "project_visibility", {"slug": _s(slug, 160), "published": bool(published)})


@tool("update_lead", "PREPARE a lead status/note change (needs confirmation). status: new|contacted|closed.",
      {"id": {"type": "integer"}, "status": {"type": "string"}, "note": {"type": "string"}}, ("id",), owner=True)
def update_lead(ctx, id=0, status="", note=""):
    return _propose(ctx, "lead", {"id": int(id), "status": _s(status, 10), "note": _s(note, 1000)})


@tool("reply_lead", "PREPARE an email reply to a lead whose contact is an email address (needs confirmation). "
      "Write the reply in the lead's language.",
      {"id": {"type": "integer"}, "subject": {"type": "string"}, "body": {"type": "string"}},
      ("id", "subject", "body"), owner=True)
def reply_lead(ctx, id=0, subject="", body=""):
    return _propose(ctx, "reply_lead", {"id": int(id), "subject": _s(subject, 150), "body": _s(body, 6000)})


@tool("mark_messages_read", "PREPARE marking contact messages as read (needs confirmation).",
      {"ids": {"type": "array", "items": {"type": "integer"}, "description": "empty = all unread"}}, owner=True)
def mark_messages_read(ctx, ids=None):
    return _propose(ctx, "messages_read", {"ids": [int(i) for i in (ids or [])][:100]})


@tool("remember_fact", "PREPARE saving a fact the assistant should know from now on (needs confirmation).",
      {"text": {"type": "string"}}, ("text",), owner=True)
def remember_fact(ctx, text=""):
    return _propose(ctx, "remember", {"text": _s(text, 1000)})


@tool("forget_fact", "PREPARE removing a remembered fact by id (needs confirmation).",
      {"id": {"type": "integer"}}, ("id",), owner=True)
def forget_fact(ctx, id=0):
    return _propose(ctx, "forget", {"id": int(id)})


@tool("add_reminder", "PREPARE a reminder sent to the owner on Telegram at a given local time (needs "
      "confirmation). due must be ISO like 2026-10-01T10:00 in Asia/Tashkent time.",
      {"due": {"type": "string"}, "text": {"type": "string"}}, ("due", "text"), owner=True)
def add_reminder(ctx, due="", text=""):
    return _propose(ctx, "reminder", {"due": _s(due, 25), "text": _s(text, 300)})


@tool("remove_reminder", "PREPARE deleting a reminder by id (needs confirmation).",
      {"id": {"type": "integer"}}, ("id",), owner=True)
def remove_reminder(ctx, id=0):
    return _propose(ctx, "reminder_remove", {"id": int(id)})
