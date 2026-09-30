"""CURRENT STATE: a compact, language-specific summary of the database.

It goes into every system prompt, so most questions are answered without a
single tool call. Cached for five minutes; changes in the admin show up in
the assistant's answers within that time.
"""
from django.core.cache import cache
from django.urls import reverse
from django.utils import translation

from apps.core.models import SiteSettings, SocialLink
from apps.projects.models import Project
from apps.resume.models import Award, Certificate, Education, Experience, LanguageSkill, SkillGroup

from .models import AiKnowledge

STATE_TTL = 5 * 60
KNOWLEDGE_TTL = 60
SITE = "https://khalilovn.uz"


def site_url(path):
    return SITE.rstrip("/") + path


def project_url(slug, lang):
    with translation.override(lang):
        return site_url(reverse("projects:detail", kwargs={"slug": slug}))


def build_state(lang):
    lines = []
    with translation.override(lang):
        conf = SiteSettings.load()
        lines.append(f"Name: {conf.full_name} — {conf.job_title}. Location: {conf.location}.")
        if conf.tr("headline"):
            lines.append(f"Headline: {conf.tr('headline')}")
        if conf.tr("intro"):
            lines.append(f"Intro: {conf.tr('intro')}")
        avail = conf.get_availability_display()
        note = conf.tr("availability_note")
        lines.append(f"Availability: {avail}" + (f" — {note}" if note else ""))
        contacts = [c for c in (conf.email, conf.phone) if c]
        contacts += [f"{s.label}: {s.url}" for s in SocialLink.objects.all()[:6]]
        if contacts:
            lines.append("Contacts: " + "; ".join(contacts))
        lines.append(f"Site pages: home {site_url('/' + lang + '/')}, work {site_url('/' + lang + '/work/')}, "
                     f"about {site_url('/' + lang + '/about/')}, resume {site_url('/' + lang + '/cv/')}, "
                     f"contact {site_url('/' + lang + '/contact/')}")

        cur = Experience.objects.filter(is_published=True, end_date__isnull=True).first()
        if cur:
            lines.append(f"Current role: {cur.tr('role')} at {cur.company} (since {cur.start_date:%Y-%m}).")
        past = Experience.objects.filter(is_published=True, end_date__isnull=False)[:4]
        if past:
            lines.append("Past roles: " + "; ".join(
                f"{e.tr('role')} at {e.company} ({e.start_date:%Y}–{e.end_date:%Y})" for e in past))

        edu = Education.objects.all()[:3]
        if edu:
            lines.append("Education: " + "; ".join(
                f"{e.tr('degree')}, {e.tr('field_of_study')} — {e.institution}"
                + (f", {e.start_year}–{e.end_year}" if e.end_year else "")
                + (f", {e.grade}" if e.grade else "") for e in edu))

        groups = SkillGroup.objects.prefetch_related("skills")
        if groups:
            lines.append("Skills: " + " | ".join(
                f"{g.tr('name')}: " + ", ".join(s.name for s in g.skills.all()) for g in groups))

        langs = LanguageSkill.objects.all()
        if langs:
            lines.append("Languages: " + ", ".join(f"{x.tr('name')} ({x.tr('level')})" for x in langs))

        certs = Certificate.objects.filter(is_published=True)[:12]
        if certs:
            lines.append("Certificates: " + "; ".join(c.tr("title") for c in certs))
        awards = Award.objects.all()[:6]
        if awards:
            lines.append("Awards: " + "; ".join(
                f"{a.tr('title')}" + (f" ({a.year})" if a.year else "") for a in awards))

        projects = (Project.objects.filter(is_published=True)
                    .prefetch_related("technologies", "metrics"))
        lines.append(f"Projects ({projects.count()}), in site order:")
        for p in projects:
            tech = ", ".join(t.name for t in p.technologies.all()[:8])
            bits = [f"- {p.title} [{p.slug}] — {p.tr('tagline')}"]
            meta = []
            if p.period:
                meta.append(p.period)
            if p.organisation:
                meta.append(p.organisation)
            meta.append(p.get_status_display())
            if p.is_confidential:
                meta.append("private source code")
            bits.append(f"  ({'; '.join(meta)}) Tech: {tech}. URL: {project_url(p.slug, lang)}")
            metrics = [f"{m.tr('label')}: {m.value_before + ' -> ' if m.value_before else ''}{m.value_after}"
                       for m in p.metrics.all()[:3]]
            if metrics:
                bits.append("  Results: " + "; ".join(metrics))
            lines.append("\n".join(bits))
    return "\n".join(lines)


def state(lang):
    lang = lang if lang in ("en", "uz", "ru") else "en"
    key = f"ai:state:{lang}"
    text = cache.get(key)
    if text is None:
        text = build_state(lang)
        cache.set(key, text, STATE_TTL)
    return text


def invalidate():
    for lang in ("en", "uz", "ru"):
        cache.delete(f"ai:state:{lang}")
    cache.delete("ai:knowledge")


def knowledge(limit=40, max_chars=4000):
    text = cache.get("ai:knowledge")
    if text is None:
        rows = list(AiKnowledge.objects.filter(is_active=True).order_by("-created_at")[:limit])
        out, size = [], 0
        for r in rows:
            line = f"- {r.text.strip()}"
            if size + len(line) > max_chars:
                break
            out.append(line)
            size += len(line)
        text = "\n".join(reversed(out)) if out else "(none yet)"
        cache.set("ai:knowledge", text, KNOWLEDGE_TTL)
    return text
