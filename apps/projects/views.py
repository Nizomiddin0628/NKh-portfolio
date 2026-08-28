import json

import json

from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render

from apps.core.models import SiteSettings

from .models import Project, Technology


def project_list(request):
    tech_slug = request.GET.get("tech", "").strip()

    qs = (Project.objects.filter(is_published=True)
          .prefetch_related("images", "technologies", "metrics"))
    if tech_slug:
        qs = qs.filter(technologies__slug=tech_slug)

    technologies = (Technology.objects
                    .annotate(n=Count("projects", filter=Q(projects__is_published=True)))
                    .filter(n__gt=0))

    return render(request, "pages/work_list.html", {
        "conf": SiteSettings.load(),
        "projects": qs.distinct(),
        "technologies": technologies,
        "active_tech": tech_slug,
        "total": Project.objects.filter(is_published=True).count(),
    })


def project_detail(request, slug):
    project = get_object_or_404(
        Project.objects.prefetch_related("images", "technologies", "sections", "metrics"),
        slug=slug, is_published=True,
    )
    siblings = list(Project.objects.filter(is_published=True).values_list("slug", "title"))
    slugs = [s for s, _t in siblings]
    idx = slugs.index(project.slug) if project.slug in slugs else -1
    nxt = siblings[(idx + 1) % len(siblings)] if len(siblings) > 1 and idx >= 0 else None

    images = list(project.images.all())
    cover = project.cover
    if cover and images and images[0].pk != cover.pk:
        images.remove(cover)
        images.insert(0, cover)

    gallery = [
        {
            "url": img.image.url,
            "alt": img.tr("alt_text"),
            "caption": img.tr("caption"),
            "width": img.width,
            "height": img.height,
        }
        for img in images
    ]

    return render(request, "pages/work_detail.html", {
        "conf": SiteSettings.load(),
        "project": project,
        "images": images,
        "gallery_json": json.dumps(gallery, ensure_ascii=False),
        "next_project": {"slug": nxt[0], "title": nxt[1]} if nxt else None,
    })
