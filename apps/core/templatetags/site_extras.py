import functools

import markdown as md_lib
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

_MD = md_lib.Markdown(extensions=["extra", "sane_lists", "nl2br"], output_format="html")


@register.filter(name="markdown")
def markdown_filter(value):
    if not value:
        return ""
    _MD.reset()
    return mark_safe(_MD.convert(value))  # noqa: S308 — kontent faqat admin tomonidan kiritiladi


# Projects that have a live SVG demo in static/js/demos/<slug>.js
DEMO_SLUGS = frozenset({
    "smart-yard-gate-automation", "medical-ai-cancer-detection", "ai-portfolio-assistant",
    "driver-drowsiness-detector", "restaurant-erp", "ai-kotib-restaurant",
    "live-truck-map", "roadside-service-locator",
})


@register.simple_tag
def module_importmap():
    """Import map that sends every ES module in static/js to its hashed URL.

    main.js is loaded through {% static %} (hashed, cached for a year), but
    its `import "./modules/ui.js"` and the demos' `import()` resolve to the
    plain, unhashed paths, which browsers may keep serving from cache after
    a deploy. The map rewrites those plain paths to the hashed files, so a
    deploy is picked up on the next page load. In DEBUG nothing is hashed
    and the map only carries the CDN entry.
    """
    return mark_safe(_importmap_json())


@functools.lru_cache(maxsize=1)
def _importmap_json_cached():
    return _build_importmap()


def _importmap_json():
    from django.conf import settings
    return _build_importmap() if settings.DEBUG else _importmap_json_cached()


def _build_importmap():
    import json
    from pathlib import Path

    from django.conf import settings
    from django.contrib.staticfiles.storage import staticfiles_storage

    imports = {"lenis": "https://cdn.jsdelivr.net/npm/lenis@1.1.18/+esm"}
    prefix = settings.STATIC_URL
    root = Path(settings.BASE_DIR) / "static"
    for f in sorted((root / "js").rglob("*.js")):
        rel = f.relative_to(root).as_posix()
        try:
            url = staticfiles_storage.url(rel)
        except ValueError:          # not collected yet
            continue
        if url != prefix + rel:
            imports[prefix + rel] = url
    return json.dumps({"imports": imports}, separators=(",", ":"))


@register.filter
def has_demo(project):
    """`{% if project|has_demo %}` — the card shows the live demo instead of the cover."""
    return getattr(project, "slug", "") in DEMO_SLUGS


@register.filter
def tr(obj, field):
    """`{{ project|tr:"tagline" }}` — shablonda aniq til maydonini olish."""
    return obj.tr(field) if hasattr(obj, "tr") else ""


@register.simple_tag(takes_context=True)
def switch_lang_url(context, lang_code):
    """Joriy sahifaning boshqa tildagi manzili."""
    from django.urls import resolve, reverse
    from django.utils import translation

    request = context["request"]
    try:
        match = resolve(request.path_info)
        with translation.override(lang_code):
            url = reverse(f"{match.namespace}:{match.url_name}" if match.namespace else match.url_name,
                          args=match.args, kwargs=match.kwargs)
    except Exception:
        url = f"/{lang_code}/"
    query = request.META.get("QUERY_STRING", "")
    return f"{url}?{query}" if query else url


@register.filter
def initials(value):
    parts = [p for p in str(value).split() if p]
    return "".join(p[0].upper() for p in parts[:2])
