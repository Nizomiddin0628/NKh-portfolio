from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from apps.projects.api import ProjectViewSet, TechnologyViewSet, stats

router = DefaultRouter()
router.register("projects", ProjectViewSet, basename="project")
router.register("technologies", TechnologyViewSet, basename="technology")

urlpatterns = [
    path("v1/", include(router.urls)),
    path("v1/stats/", stats, name="api-stats"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="api-docs"),
]
