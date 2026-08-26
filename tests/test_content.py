import pytest
from django.utils import translation


@pytest.mark.django_db
def test_translation_falls_back_to_english(seeded):
    """Tarjima bo'sh bo'lsa — inglizcha matn ko'rsatiladi, bo'sh joy emas."""
    from apps.projects.models import Project

    project = Project.objects.first()
    project.tagline_de = ""
    project.save()

    with translation.override("de"):
        assert project.tr("tagline") == project.tagline_en
        assert project.tagline == project.tagline_en


@pytest.mark.django_db
def test_only_one_primary_image_per_project(seeded, tmp_path, settings):
    """Yangi asosiy rasm belgilanganda eskisi avtomatik bekor qilinadi."""
    settings.MEDIA_ROOT = tmp_path
    from django.core.files.uploadedfile import SimpleUploadedFile
    from PIL import Image

    from apps.projects.models import Project, ProjectImage

    project = Project.objects.first()

    def make(name):
        path = tmp_path / name
        Image.new("RGB", (400, 300), "navy").save(path)
        return SimpleUploadedFile(name, path.read_bytes(), content_type="image/jpeg")

    first = ProjectImage.objects.create(project=project, image=make("a.jpg"),
                                        alt_text_en="a", is_primary=True)
    second = ProjectImage.objects.create(project=project, image=make("b.jpg"),
                                         alt_text_en="b", is_primary=True)

    first.refresh_from_db()
    assert not first.is_primary
    assert second.is_primary
    assert project.cover.pk == second.pk
    # O'lchamlar avtomatik saqlanadi (CLS = 0 uchun kerak)
    assert second.width == 400 and second.height == 300


@pytest.mark.django_db
def test_contact_form_rejects_honeypot(seeded, client):
    from django.urls import reverse

    from apps.core.models import ContactMessage

    client.post(reverse("core:contact"), {
        "name": "Bot", "email": "bot@spam.test", "subject": "hi",
        "message": "x" * 40, "website": "http://spam.example",
    })
    assert ContactMessage.objects.count() == 0


@pytest.mark.django_db
def test_contact_form_saves_valid_message(seeded, client):
    from django.urls import reverse

    from apps.core.models import ContactMessage

    response = client.post(reverse("core:contact"), {
        "name": "Recruiter", "email": "hr@company.test", "subject": "Role",
        "message": "We would like to talk about a backend position.",
    })
    assert response.status_code == 302
    assert ContactMessage.objects.count() == 1
