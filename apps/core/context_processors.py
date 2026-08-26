import json

from django.conf import settings as dj_settings
from django.urls import reverse
from django.utils.translation import gettext as _

from apps.projects.models import Project

from .models import SiteSettings, SocialLink


def site(request):
    try:
        conf = SiteSettings.load()
    except Exception:  # migratsiyalar hali yugurmagan bo'lsa
        return {"site": None, "social_links": [], "LANGUAGES": dj_settings.LANGUAGES}

    projects = list(Project.objects.filter(is_published=True).values("slug", "title")[:30])

    commands = [
        {"group": _("Pages"), "label": _("Home"), "url": reverse("core:home"), "keywords": "start"},
        {"group": _("Pages"), "label": _("Work"), "url": reverse("projects:list"), "keywords": "projects"},
        {"group": _("Pages"), "label": _("About"), "url": reverse("core:about"), "keywords": "bio cv"},
        {"group": _("Pages"), "label": _("Résumé"), "url": reverse("core:cv"), "keywords": "cv pdf"},
        {"group": _("Pages"), "label": _("Contact"), "url": reverse("core:contact"), "keywords": "email hire"},
    ]
    commands += [
        {"group": _("Projects"), "label": p["title"],
         "url": reverse("projects:detail", kwargs={"slug": p["slug"]}),
         "hint": "↵", "keywords": p["slug"]}
        for p in projects
    ]
    commands += [
        {"group": _("Links"), "label": link.label, "url": link.url, "hint": "↗"}
        for link in SocialLink.objects.all()
    ]

    return {
        "site": conf,
        "social_links": SocialLink.objects.all(),
        "header_links": SocialLink.objects.filter(show_in_header=True),
        "LANGUAGES": dj_settings.LANGUAGES,
        "cmdk_json": json.dumps(commands, ensure_ascii=False),
    }
