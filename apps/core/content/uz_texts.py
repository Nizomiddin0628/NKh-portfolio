"""Apply a set of Uzbek texts to the database.

Used by the `polish_uz` command and by data migrations. Objects are looked up
by stable keys (project slug + order, company name, ...), never by id, so the
same file works on any copy of the database. Current values are saved to
backups/ before anything is changed.
"""
import json
from datetime import datetime
from pathlib import Path

from django.conf import settings

MODELS = {
    "SiteSettings": "core.SiteSettings",
    "Principle": "core.Principle",
    "Project": "projects.Project",
    "CaseSection": "projects.CaseSection",
    "Metric": "projects.Metric",
    "ProjectImage": "projects.ProjectImage",
    "Experience": "resume.Experience",
    "ExperienceBullet": "resume.ExperienceBullet",
    "Education": "resume.Education",
    "SkillGroup": "resume.SkillGroup",
    "LanguageSkill": "resume.LanguageSkill",
    "Award": "resume.Award",
}


def apply_texts(get_model, path, backup=True, log=print):
    """Write the `uz` values from `path`. Returns the number of changed fields."""
    rows = json.loads(Path(path).read_text(encoding="utf-8"))
    saved, changed = [], 0
    for row in rows:
        model = get_model(*MODELS[row["model"]].split("."))
        qs = model.objects.filter(**row["key"]) if row["key"] else model.objects.all()
        obj = qs.first()
        if obj is None:
            continue
        field = f"{row['field']}_uz"
        current = getattr(obj, field)
        saved.append({**row, "uz": current})
        if current != row["uz"]:
            setattr(obj, field, row["uz"])
            obj.save(update_fields=[field])
            changed += 1

    if backup and saved:
        folder = Path(settings.BASE_DIR) / "backups"
        folder.mkdir(exist_ok=True)
        out = folder / f"uz_before_{datetime.now():%Y%m%d_%H%M%S}.json"
        out.write_text(json.dumps(saved, ensure_ascii=False, indent=1), encoding="utf-8")
        log(f"  Uzbek texts: {changed} changed, backup saved to {out}")
    return changed
