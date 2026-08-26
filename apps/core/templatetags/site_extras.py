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
