"""Boshlang'ich kontentni bazaga yozadi.

    python manage.py seed          # bor yozuvlarga tegmaydi
    python manage.py seed --reset  # avval hammasini o'chiradi

Bir marta ishlatiladi. Keyin hamma narsa /admin orqali boshqariladi.
"""
from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.core.models import Principle, SiteSettings
from apps.projects.models import CaseSection, Metric, Project, Technology
from apps.resume.models import (
    Award,
    Education,
    Experience,
    ExperienceBullet,
    LanguageSkill,
    Skill,
    SkillGroup,
)

from . import _content as C


class Command(BaseCommand):
    help = "Load the initial portfolio content."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true",
                            help="Delete existing content first.")

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            for model in (CaseSection, Metric, Project, Technology, Principle,
                          ExperienceBullet, Experience, Education, Skill,
                          SkillGroup, LanguageSkill, Award):
                model.objects.all().delete()
            self.stdout.write(self.style.WARNING("Existing content deleted."))

        self._site()
        self._principles()
        techs = self._technologies()
        self._skills()
        self._languages()
        self._education()
        self._awards()
        self._experience()
        self._projects(techs)

        self.stdout.write(self.style.SUCCESS("\nContent loaded."))
        self.stdout.write(
            "\nNext:\n"
            "  1. python manage.py createsuperuser\n"
            "  2. open /admin and fill in the fields marked TODO\n"
            "     (email, phone, company name, exact dates)\n"
            "  3. upload project images — Projects → open a project → Images\n"
        )

    # ── bo'limlar ────────────────────────────────────────────────────────
    def _site(self):
        conf = SiteSettings.load()
        for key, value in C.SITE.items():
            setattr(conf, key, value)
        conf.save()
        self.stdout.write("· site settings")

    def _principles(self):
        for i, data in enumerate(C.PRINCIPLES):
            Principle.objects.update_or_create(
                title_en=data["title_en"], defaults={**data, "order": i})
        self.stdout.write(f"· {len(C.PRINCIPLES)} principles")

    def _technologies(self):
        techs = {}
        for i, (name, slug, category) in enumerate(C.TECHNOLOGIES):
            obj, _ = Technology.objects.update_or_create(
                slug=slug, defaults={"name": name, "category": category, "order": i})
            techs[name] = obj
        self.stdout.write(f"· {len(techs)} technologies")
        return techs

    def _skills(self):
        for i, data in enumerate(C.SKILL_GROUPS):
            skills = data.pop("skills", [])
            group, _ = SkillGroup.objects.update_or_create(
                name_en=data["name_en"], defaults={**data, "order": i})
            for j, (name, depth) in enumerate(skills):
                Skill.objects.update_or_create(
                    group=group, name=name, defaults={"depth": depth, "order": j})
            data["skills"] = skills
        self.stdout.write(f"· {len(C.SKILL_GROUPS)} skill groups")

    def _languages(self):
        for i, data in enumerate(C.LANGUAGES):
            LanguageSkill.objects.update_or_create(
                name_en=data["name_en"], defaults={**data, "order": i})
        self.stdout.write(f"· {len(C.LANGUAGES)} languages")

    def _education(self):
        for i, data in enumerate(C.EDUCATION):
            Education.objects.update_or_create(
                institution=data["institution"], defaults={**data, "order": i})
        self.stdout.write(f"· {len(C.EDUCATION)} education entries")

    def _awards(self):
        for i, data in enumerate(C.AWARDS):
            Award.objects.update_or_create(
                title_en=data["title_en"], defaults={**data, "order": i})
        self.stdout.write(f"· {len(C.AWARDS)} awards")

    def _experience(self):
        for i, data in enumerate(C.EXPERIENCE):
            data = dict(data)
            bullets = data.pop("bullets", [])
            data["start_date"] = date.fromisoformat(data["start_date"])
            if data.get("end_date"):
                data["end_date"] = date.fromisoformat(data["end_date"])
            job, _ = Experience.objects.update_or_create(
                company=data["company"], role_en=data["role_en"],
                defaults={**data, "order": i})
            job.bullets.all().delete()
            for j, bullet in enumerate(bullets):
                ExperienceBullet.objects.create(experience=job, order=j, **bullet)
        self.stdout.write(f"· {len(C.EXPERIENCE)} experience entries")

    def _projects(self, techs):
        for data in C.PROJECTS:
            data = dict(data)
            sections = data.pop("sections", [])
            metrics = data.pop("metrics", [])
            tech_names = data.pop("technologies", [])
            slug = data.pop("slug")

            project, _ = Project.objects.update_or_create(slug=slug, defaults=data)
            project.technologies.set([techs[n] for n in tech_names if n in techs])

            project.sections.all().delete()
            for section in sections:
                CaseSection.objects.create(project=project, **section)

            project.metrics.all().delete()
            for i, metric in enumerate(metrics):
                Metric.objects.create(project=project, order=i, **metric)

        self.stdout.write(f"· {len(C.PROJECTS)} projects with case studies")
