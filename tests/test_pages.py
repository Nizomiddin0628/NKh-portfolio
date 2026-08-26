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
    for lang in ["en", "uz", "de", "ru"]:
        assert client.get(f"/{lang}/").status_code == 200


@pytest.mark.django_db
def test_sitemap_and_robots(seeded, client):
    assert client.get("/sitemap.xml").status_code == 200
    assert b"Disallow: /admin/" in client.get("/robots.txt").content
