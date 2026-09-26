"""Portrait rendering for the hero section.

The admin cropper stores a box (x,y,width,height) in pixels of the original
image. Here that box is cut out, resized to at most 900x1125 (4:5) and saved
as a compressed JPEG. Without a stored box a centred crop is used, shifted
upward because faces sit in the upper part of most portraits.
"""
import io
import logging

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from PIL import Image, ImageOps

logger = logging.getLogger(__name__)

RATIO = 4 / 5
TARGET = (900, 1125)
DISPLAY_NAME = "site/avatar_display.jpg"


def _parse_box(value, size):
    try:
        x, y, w, h = (int(float(v)) for v in value.split(","))
    except (ValueError, AttributeError):
        return None
    width, height = size
    x, y = max(0, x), max(0, y)
    w, h = min(w, width - x), min(h, height - y)
    if w < 20 or h < 20:
        return None
    return (x, y, x + w, y + h)


def _default_box(size):
    width, height = size
    if width / height > RATIO:
        crop_w = int(height * RATIO)
        x = (width - crop_w) // 2
        return (x, 0, x + crop_w, height)
    crop_h = int(width / RATIO)
    y = int((height - crop_h) * 0.25)
    return (0, y, width, y + crop_h)


def render_portrait(conf) -> str:
    """Return the storage name of the rendered portrait ('' if none)."""
    if not conf.avatar:
        if conf.avatar_display and default_storage.exists(conf.avatar_display.name):
            default_storage.delete(conf.avatar_display.name)
        return ""

    try:
        conf.avatar.open("rb")
        img = Image.open(conf.avatar)
        img = ImageOps.exif_transpose(img).convert("RGB")
        img.load()
    except Exception as exc:  # pragma: no cover
        logger.warning("Portrait could not be read: %s", exc)
        return conf.avatar_display.name or ""
    finally:
        conf.avatar.close()

    box = _parse_box(conf.avatar_crop, img.size) or _default_box(img.size)
    img = img.crop(box)
    img.thumbnail(TARGET, Image.LANCZOS)

    buffer = io.BytesIO()
    img.save(buffer, "JPEG", quality=88, optimize=True, progressive=True)

    if default_storage.exists(DISPLAY_NAME):
        default_storage.delete(DISPLAY_NAME)
    return default_storage.save(DISPLAY_NAME, ContentFile(buffer.getvalue()))
