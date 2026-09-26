"""Attach illustrative diagrams to projects that have no images yet.

Safe to run any number of times: a project that already has at least one
image (for example a real screenshot uploaded in the admin) is skipped.

    python manage.py load_project_diagrams
"""
from django.core.files import File
from django.core.management.base import BaseCommand

from apps.projects.models import Project, ProjectImage

from .load_portfolio import ASSETS, L, lang_fields

DIAGRAMS = {
    "roadside-service-locator": (
        "roadside-locator-diagram.png",
        L(
            "Illustration: a truck's GPS position, a 150-mile search radius and service points ranked by past outcomes",
            "Illustratsiya: yuk mashinasining GPS nuqtasi, 150 mil radius va oldingi natijalar bo'yicha saralangan servislar",
            "Иллюстрация: GPS-точка грузовика, радиус 150 миль и сервисы, отсортированные по прошлым результатам",
        ),
        L(
            "Illustration of the flow: GPS point → 150-mile radius search → ranking by how past call-outs went.",
            "Ishlash tartibi: GPS nuqta → 150 mil radiusda qidiruv → oldingi chaqiruvlar natijasiga ko'ra saralash.",
            "Схема работы: GPS-точка → поиск в радиусе 150 миль → ранжирование по итогам прошлых вызовов.",
        ),
    ),
    "driver-drowsiness-detector": (
        "drowsiness-ear-diagram.png",
        L(
            "Diagram: six eye landmarks, the eye aspect ratio formula and an EAR-over-time chart with an alert",
            "Diagramma: ko'zdagi oltita nuqta, EAR formulasi va ogohlantirish bilan EAR grafigi",
            "Диаграмма: шесть точек глаза, формула EAR и график EAR во времени с сигналом тревоги",
        ),
        L(
            "Eye aspect ratio from six landmarks. Blinks are ignored; a sustained drop below the threshold triggers the alert.",
            "Ko'z nisbati (EAR) oltita nuqtadan hisoblanadi. Qisqa pirpirash hisobga olinmaydi, uzoq yumilganda signal chalinadi.",
            "EAR считается по шести точкам. Моргание игнорируется; длительное падение ниже порога включает сигнал.",
        ),
    ),
}


class Command(BaseCommand):
    help = "Attach illustrative diagrams to projects that have no images."

    def handle(self, *args, **options):
        say = self.stdout.write if options.get("verbosity", 1) else (lambda *a, **k: None)
        for slug, (filename, alt, caption) in DIAGRAMS.items():
            project = Project.objects.filter(slug=slug).first()
            if project is None:
                say(f"· {slug}: not found, skipped")
                continue
            if project.images.exists():
                say(f"· {slug}: already has images, skipped")
                continue
            img = ProjectImage(project=project, order=0, is_primary=True,
                               **lang_fields("alt_text", alt), **lang_fields("caption", caption))
            with open(ASSETS / filename, "rb") as fh:
                img.image.save(filename, File(fh), save=False)
            img.save()
            say(f"· {slug}: diagram added")
        say(self.style.SUCCESS("Done."))
