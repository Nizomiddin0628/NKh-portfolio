"""Read-only public API.

Sayt Django template'lar bilan server tomonda render qilinadi (SEO va tezlik
uchun). Bu API qatlami — alohida ko'rgazma: `/api/docs/` manzilida OpenAPI
hujjati bilan birga turadi.
"""
from django.db.models import Count, Q
from drf_spectacular.utils import extend_schema, extend_schema_field
from rest_framework import serializers, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.core.models import SiteSettings
from apps.resume.models import Experience

from .models import Project, Technology


class TechnologySerializer(serializers.ModelSerializer):
    class Meta:
        model = Technology
        fields = ["name", "slug", "category"]


class ImageSerializer(serializers.Serializer):
    url = serializers.SerializerMethodField()
    alt = serializers.CharField(source="alt_text")
    caption = serializers.CharField()
    is_primary = serializers.BooleanField()
    width = serializers.IntegerField()
    height = serializers.IntegerField()

    @extend_schema_field(serializers.URLField)
    def get_url(self, obj):
        request = self.context.get("request")
        url = obj.image.url
        return request.build_absolute_uri(url) if request else url


class MetricSerializer(serializers.Serializer):
    label = serializers.CharField()
    before = serializers.CharField(source="value_before")
    after = serializers.CharField(source="value_after")


class ProjectListSerializer(serializers.ModelSerializer):
    tagline = serializers.CharField(read_only=True)
    role = serializers.CharField(read_only=True)
    technologies = TechnologySerializer(many=True, read_only=True)
    cover = serializers.SerializerMethodField()
    url = serializers.CharField(source="get_absolute_url", read_only=True)

    class Meta:
        model = Project
        fields = ["title", "slug", "tagline", "role", "status", "organisation",
                  "year_started", "year_finished", "technologies", "cover", "url"]

    @extend_schema_field(ImageSerializer)
    def get_cover(self, obj):
        cover = obj.cover
        return ImageSerializer(cover, context=self.context).data if cover else None


class SectionSerializer(serializers.Serializer):
    kind = serializers.CharField()
    heading = serializers.CharField(source="title")
    body = serializers.CharField()


class ProjectDetailSerializer(ProjectListSerializer):
    summary = serializers.CharField(read_only=True)
    context_text = serializers.CharField(source="context", read_only=True)
    images = ImageSerializer(many=True, read_only=True)
    sections = SectionSerializer(many=True, read_only=True)
    metrics = MetricSerializer(many=True, read_only=True)

    class Meta(ProjectListSerializer.Meta):
        fields = ProjectListSerializer.Meta.fields + [
            "summary", "context_text", "images", "sections", "metrics",
            "live_url", "repo_url", "team_size",
        ]


class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    """Barcha e'lon qilingan loyihalar. `?tech=django` bilan filtrlanadi."""
    lookup_field = "slug"
    serializer_class = ProjectListSerializer

    def get_queryset(self):
        qs = (Project.objects.filter(is_published=True)
              .prefetch_related("images", "technologies", "sections", "metrics"))
        tech = self.request.query_params.get("tech")
        return qs.filter(technologies__slug=tech).distinct() if tech else qs

    def get_serializer_class(self):
        return ProjectDetailSerializer if self.action == "retrieve" else ProjectListSerializer


class TechnologyViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"
    serializer_class = TechnologySerializer
    queryset = (Technology.objects
                .annotate(n=Count("projects", filter=Q(projects__is_published=True)))
                .filter(n__gt=0))
    pagination_class = None


class StatsSerializer(serializers.Serializer):
    name = serializers.CharField()
    title = serializers.CharField()
    availability = serializers.CharField()
    projects_published = serializers.IntegerField()
    projects_in_production = serializers.IntegerField()
    technologies = serializers.IntegerField()
    current_role = serializers.CharField(allow_null=True)
    current_company = serializers.CharField(allow_null=True)


@extend_schema(
    responses={200: StatsSerializer},
    description="Aggregate numbers used on the home page.",
)
@api_view(["GET"])
def stats(request):
    conf = SiteSettings.load()
    current = Experience.objects.filter(is_published=True, end_date__isnull=True).first()
    return Response({
        "name": conf.full_name,
        "title": conf.job_title,
        "availability": conf.availability,
        "projects_published": Project.objects.filter(is_published=True).count(),
        "projects_in_production": Project.objects.filter(
            is_published=True, status=Project.Status.PRODUCTION).count(),
        "technologies": Technology.objects.count(),
        "current_role": current.role if current else None,
        "current_company": current.company if current else None,
    })
