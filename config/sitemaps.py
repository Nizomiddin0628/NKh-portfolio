from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.projects.models import Project


class StaticSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8
    i18n = True

    def items(self):
        return ["core:home", "core:about", "core:contact", "core:cv", "projects:list"]

    def location(self, item):
        return reverse(item)


class ProjectSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.9
    i18n = True

    def items(self):
        return Project.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at


SITEMAPS = {"static": StaticSitemap, "projects": ProjectSitemap}
