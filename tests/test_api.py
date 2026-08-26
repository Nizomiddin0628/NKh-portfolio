import pytest


@pytest.mark.django_db
def test_project_list_endpoint(seeded, client):
    data = client.get("/api/v1/projects/").json()
    assert data["count"] > 0
    assert "tagline" in data["results"][0]


@pytest.mark.django_db
def test_project_filter_by_technology(seeded, client):
    data = client.get("/api/v1/projects/?tech=django").json()
    assert data["count"] > 0


@pytest.mark.django_db
def test_stats_endpoint(seeded, client):
    data = client.get("/api/v1/stats/").json()
    assert data["projects_published"] > 0


@pytest.mark.django_db
def test_openapi_schema(seeded, client):
    assert client.get("/api/schema/").status_code == 200
