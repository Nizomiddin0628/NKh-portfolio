"""Yuklangan rasmlarni saytga moslash.

Admin panelga qanday rasm yuklanmasin — juda katta bo'lsa kichraytiriladi,
EXIF burilishi to'g'rilanadi, o'lchamlari bazaga yoziladi. O'lchamlar
`aspect-ratio` uchun kerak: shu tufayli sahifada layout sakramaydi (CLS = 0).
"""
import logging

from PIL import Image, ImageOps

logger = logging.getLogger(__name__)

MAX_BYTES_SKIP = 25 * 1024 * 1024


def process_upload(field_file, max_width: int = 1800):
    """Rasmni joyida optimallashtiradi. `(width, height)` qaytaradi."""
    if not field_file:
        return None
    try:
        path = field_file.path
    except (NotImplementedError, ValueError):
        return None

    try:
        with Image.open(path) as img:
            img = ImageOps.exif_transpose(img)
            changed = False

            if img.width > max_width:
                ratio = max_width / img.width
                img = img.resize((max_width, round(img.height * ratio)), Image.LANCZOS)
                changed = True

            if img.mode in ("P", "LA", "RGBA") and path.lower().endswith((".jpg", ".jpeg")):
                img = img.convert("RGB")
                changed = True

            size = (img.width, img.height)
            if changed:
                params = {"optimize": True}
                if path.lower().endswith((".jpg", ".jpeg")):
                    params["quality"] = 86
                    params["progressive"] = True
                img.save(path, **params)
        return size
    except Exception as exc:  # pragma: no cover
        logger.warning("Image processing failed for %s: %s", path, exc)
        return None
