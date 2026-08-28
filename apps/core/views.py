from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.utils import translation
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods

from apps.projects.models import Project,Technology
from apps.resume.models import Award, Education, Experience, LanguageSkill, SkillGroup

from .forms import ContactForm
from .models import PageView, Principle, SiteSettings

RATE_LIMIT_PER_HOUR = 5


def _track(request):
    """Yengil ichki hisoblagich (tashqi analitikasiz, cookie'siz)."""
    if request.method != "GET" or request.path.startswith("/admin"):
        return
    try:
        obj, created = PageView.objects.get_or_create(path=request.path[:300])
        if not created:
            PageView.objects.filter(pk=obj.pk).update(count=obj.count + 1)
    except Exception:
        pass


def _base_context(request):
    _track(request)
    return {"conf": SiteSettings.load()}


def home(request):
    ctx = _base_context(request)
    ctx.update({
        "featured_projects": (
            Project.objects.filter(is_published=True, is_featured=True)
            .prefetch_related("images", "technologies", "metrics")[:4]
        ),
        "project_total": Project.objects.filter(is_published=True).count(),
        "principles": Principle.objects.filter(is_published=True)[:3],
        "technologies": Technology.objects.filter(projects__is_published=True).distinct()[:14],
        "current_role": Experience.objects.filter(is_published=True, end_date__isnull=True).first(),
    })
    return render(request, "pages/home.html", ctx)


def about(request):
    ctx = _base_context(request)
    ctx.update({
        "experiences": Experience.objects.filter(is_published=True).prefetch_related("bullets"),
        "education": Education.objects.all(),
        "skill_groups": SkillGroup.objects.prefetch_related("skills"),
        "languages": LanguageSkill.objects.all(),
        "awards": Award.objects.all(),
        "principles": Principle.objects.filter(is_published=True),
    })
    return render(request, "pages/about.html", ctx)


def cv(request):
    ctx = _base_context(request)
    ctx.update({
        "experiences": Experience.objects.filter(is_published=True).prefetch_related("bullets"),
        "education": Education.objects.all(),
        "skill_groups": SkillGroup.objects.prefetch_related("skills"),
        "languages": LanguageSkill.objects.all(),
        "awards": Award.objects.all(),
        "projects": Project.objects.filter(is_published=True).prefetch_related("technologies")[:5],
    })
    return render(request, "pages/cv.html", ctx)


@require_http_methods(["GET", "POST"])
def contact(request):
    ctx = _base_context(request)
    form = ContactForm(request.POST or None)

    if request.method == "POST":
        ip = _client_ip(request)
        key = f"contact:{ip}"
        sent = cache.get(key, 0)
        if sent >= RATE_LIMIT_PER_HOUR:
            messages.error(request, _("Too many messages from this address. Please try again later."))
        elif form.is_valid():
            msg = form.save(commit=False)
            msg.ip_address = ip
            msg.user_agent = request.META.get("HTTP_USER_AGENT", "")[:300]
            msg.language = translation.get_language() or ""
            msg.save()
            cache.set(key, sent + 1, 3600)
            _notify(msg)
            messages.success(request, _("Thanks — your message arrived. I usually reply within a day."))
            return redirect("core:contact")

    ctx["form"] = form
    return render(request, "pages/contact.html", ctx)


def _client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _notify(msg):
    to = settings.CONTACT_NOTIFY_EMAIL or (SiteSettings.load().email or "")
    if not to:
        return
    try:
        send_mail(
            subject=f"[Portfolio] {msg.subject or 'New message'} — {msg.name}",
            message=f"From: {msg.name} <{msg.email}>\nLanguage: {msg.language}\n\n{msg.message}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to],
            fail_silently=True,
        )
    except Exception:
        pass


def robots(request):
    from django.http import HttpResponse
    host = request.get_host()
    body = "\n".join([
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        f"Sitemap: {request.scheme}://{host}/sitemap.xml",
        "",
    ])
    return HttpResponse(body, content_type="text/plain")


def error_404(request, exception):
    return render(request, "pages/404.html", {"conf": SiteSettings.load()}, status=404)


def error_500(request):
    return render(request, "pages/500.html", {"conf": SiteSettings.load()}, status=500)
