import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_pages_render(seeded, client):
    for name in ["core:home", "core:about", "core:cv", "core:contact", "projects:list"]:
        assert client.get(reverse(name)).status_code == 200


@pytest.mark.django_db
def test_project_detail(seeded, client):
    from apps.projects.models import Project
    project = Project.objects.filter(is_published=True).first()
    response = client.get(project.get_absolute_url())
    assert response.status_code == 200
    assert project.title.encode() in response.content


@pytest.mark.django_db
def test_unpublished_project_is_404(seeded, client):
    from apps.projects.models import Project
    project = Project.objects.first()
    project.is_published = False
    project.save()
    assert client.get(project.get_absolute_url()).status_code == 404


@pytest.mark.django_db
def test_language_prefixes(seeded, client):
    for lang in ["en", "uz", "ru"]:
        assert client.get(f"/{lang}/").status_code == 200


@pytest.mark.django_db
def test_sitemap_and_robots(seeded, client):
    assert client.get("/sitemap.xml").status_code == 200
    assert client.get("/robots.txt").status_code == 200


def test_every_demo_slug_has_a_scene():
    from pathlib import Path

    from apps.core.templatetags.site_extras import DEMO_SLUGS
    root = Path(__file__).resolve().parent.parent / "static" / "js" / "demos"
    assert (root / "engine.js").exists()
    for slug in DEMO_SLUGS:
        assert (root / f"{slug}.js").exists(), slug


@pytest.mark.django_db
def test_demo_on_card_and_detail(seeded, client):
    from apps.projects.models import Project
    project = Project.objects.filter(slug="smart-yard-gate-automation").first()
    if project is None:
        project = Project.objects.filter(is_published=True).first()
        project.slug = "smart-yard-gate-automation"
    project.is_published = project.is_featured = True
    project.save()
    detail = client.get(project.get_absolute_url()).content.decode()
    assert 'data-demo="smart-yard-gate-automation"' in detail and "data-demo-steps" in detail
    home = client.get(reverse("core:home")).content.decode()
    assert 'class="card__img card__img--demo"' in home

    # a project without a scene keeps its normal card and no demo panel
    other = Project.objects.filter(is_published=True).exclude(pk=project.pk).first()
    other.slug = "no-demo-here"
    other.save()
    assert "data-demo-panel" not in client.get(other.get_absolute_url()).content.decode()


@pytest.mark.django_db
def test_contact_page_has_flow_demo(seeded, client):
    html = client.get(reverse("core:contact")).content.decode()
    assert 'data-demo="contact-flow"' in html


@pytest.mark.django_db
def test_about_has_facts_and_work(seeded, client):
    html = client.get(reverse("core:about")).content.decode()
    assert "about-facts" in html and "data-carousel" in html
