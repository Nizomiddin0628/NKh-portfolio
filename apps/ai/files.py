"""Attachments (images, PDFs, audio) prepared for Gemini.

Images are rotated by EXIF, shrunk to MAX_SIDE px and re-encoded as JPEG so
a 6 MB phone photo becomes ~300 KB. PDFs and audio are passed as they are.
"""
import io

from PIL import Image, ImageOps

from .gemini import AiError, inline_part

MAX_SIDE = 2000
MAX_BYTES = 20 * 1024 * 1024
IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/heic", "image/heif", "image/gif"}
AUDIO_TYPES = {"audio/ogg", "audio/mpeg", "audio/mp4", "audio/webm", "audio/wav", "audio/x-m4a",
               "audio/aac", "audio/flac", "video/webm", "video/mp4"}
PDF = "application/pdf"


def sniff(raw, hint=""):
    """Guess the mime type from the first bytes; fall back to the hint."""
    head = raw[:16]
    if head.startswith(b"\xff\xd8"):
        return "image/jpeg"
    if head.startswith(b"\x89PNG"):
        return "image/png"
    if head[:4] == b"RIFF" and raw[8:12] == b"WEBP":
        return "image/webp"
    if head.startswith(b"GIF8"):
        return "image/gif"
    if head.startswith(b"%PDF"):
        return PDF
    if head.startswith(b"OggS"):
        return "audio/ogg"
    if head.startswith(b"ID3") or head[:2] in (b"\xff\xfb", b"\xff\xf3"):
        return "audio/mpeg"
    if head[:4] == b"\x1aE\xdf\xa3":
        return "audio/webm"
    if raw[4:8] == b"ftyp":
        return "image/heic" if raw[8:12] in (b"heic", b"heix", b"mif1") else "audio/mp4"
    return (hint or "").split(";")[0].strip().lower()


def shrink_image(raw):
    try:
        img = Image.open(io.BytesIO(raw))
        img = ImageOps.exif_transpose(img)
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        w, h = img.size
        scale = MAX_SIDE / max(w, h)
        if scale < 1:
            img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        out = io.BytesIO()
        img.save(out, "JPEG", quality=85, optimize=True)
        return out.getvalue(), "image/jpeg"
    except Exception:
        return raw, None


def prepare(raw, hint="", allow_audio=False):
    """Bytes -> (gemini part, kind) where kind is image | pdf | audio.

    Raises AiError("file") for unsupported or oversized files.
    """
    if not raw:
        raise AiError("file", "empty")
    if len(raw) > MAX_BYTES:
        raise AiError("file", "too large")
    mime = sniff(raw, hint)
    if mime in IMAGE_TYPES:
        if mime in ("image/heic", "image/heif"):
            return inline_part(raw, mime), "image"  # Gemini reads HEIC natively
        data, new_mime = shrink_image(raw)
        return inline_part(data, new_mime or mime), "image"
    if mime == PDF:
        return inline_part(raw, PDF), "pdf"
    if allow_audio and mime in AUDIO_TYPES:
        return inline_part(raw, mime), "audio"
    raise AiError("file", f"unsupported type {mime or 'unknown'}")
