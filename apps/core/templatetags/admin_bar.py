"""Links from the public site into the admin, shown to staff only."""
from django import template
from django.urls import NoReverseMatch, reverse

from apps.core.models import ContactMessage

register = template.Library()

PAGE_TO_ADMIN = {
    "projects:list": ("admin:projects_project_changelist", None),
    "core:home": ("admin:core_sitesettings_change", 1),
    "core:about": ("admin:core_sitesettings_change", 1),
    "core:cv": ("admin:resume_experience_changelist", None),
    "core:contact": ("admin:core_contactmessage_changelist", None),
}


@register.simple_tag(takes_context=True)
def admin_links(context):
    """Where "Edit this page" should go, and how many messages are unread."""
    request = context.get("request")
    match = getattr(request, "resolver_match", None)
    edit_url = None

    if match is not None:
        name = f"{match.namespace}:{match.url_name}" if match.namespace else match.url_name
        try:
            if name == "projects:detail":
                from apps.projects.models import Project
                project = Project.objects.filter(slug=match.kwargs.get("slug")).only("pk").first()
                if project:
                    edit_url = reverse("admin:projects_project_change", args=[project.pk])
            elif name in PAGE_TO_ADMIN:
                route, pk = PAGE_TO_ADMIN[name]
                edit_url = reverse(route, args=[pk] if pk else None)
        except NoReverseMatch:
            edit_url = None

    return {
        "edit_url": edit_url,
        "unread": ContactMessage.objects.filter(is_read=False).count(),
    }
