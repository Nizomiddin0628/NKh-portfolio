"""`{% ai_widget %}` — the chat button and panel, rendered once in base.html."""
import json

from django import template
from django.urls import reverse
from django.utils.translation import get_language

from apps.ai import gemini
from apps.ai.ui import texts

register = template.Library()


@register.inclusion_tag("ai/widget.html", takes_context=True)
def ai_widget(context):
    request = context.get("request")
    lang = (get_language() or "en").split("-")[0]
    lang = lang if lang in ("en", "uz", "ru") else "en"
    ui = texts(lang)
    user = getattr(request, "user", None)
    owner = bool(user is not None and user.is_authenticated and user.is_superuser)
    site = context.get("site")
    initials = "".join(p[0].upper() for p in str(getattr(site, "full_name", "N K")).split()[:2]) or "NK"
    config = {
        "lang": lang, "owner": owner, "enabled": gemini.enabled(),
        "urls": {"status": reverse("ai:status"), "ask": reverse("ai:ask"),
                 "transcribe": reverse("ai:transcribe"), "actions": reverse("ai:actions")},
        "contact": reverse("core:contact"),
        "ui": ui,
    }
    return {"ui": ui, "owner": owner, "initials": initials, "lang": lang,
            "config_json": json.dumps(config, ensure_ascii=False)}
