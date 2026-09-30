"""Model text -> safe HTML for the site and Telegram.

Everything is escaped first; then a small whitelist is restored (<b>, <i>,
<code>) and light markdown is converted. The result is safe to inject into
the page and valid for Telegram's parse_mode=HTML.
"""
import html
import re

from django.conf import settings

NOINFO = "[[NOINFO]]"
_ALLOWED = ("b", "i", "code")
_URL = re.compile(r"(?<![\"'>=])\b(https?://[^\s<>\"']+[^\s<>\"'.,;:!?)\]])")
_MD_LINK = re.compile(r"\[([^\]]{1,120})\]\((https?://[^\s)]+|/[^\s)]*)\)")
_BOLD = re.compile(r"\*\*(.+?)\*\*")
_CODE = re.compile(r"`([^`\n]{1,200})`")
_HEAD = re.compile(r"^\s{0,3}#{1,6}\s+(.+)$", re.M)
_BULLET = re.compile(r"^\s{0,6}[-*•]\s+", re.M)
_SECRETS = [
    re.compile(r"\b\d{8,11}:[A-Za-z0-9_-]{30,}\b"),   # telegram bot token
    re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b"),         # google api key
    re.compile(r"\b185\.196\.215\.179\b"),
]


def scrub(text):
    """Remove anything that looks like a secret, whatever the model did."""
    for rx in _SECRETS:
        text = rx.sub("[hidden]", text)
    admin = (getattr(settings, "ADMIN_URL", "") or "").strip("/")
    if admin and admin != "admin":
        text = text.replace(admin, "[hidden]")
    return text


def strip_marker(text):
    flag = NOINFO in text
    return text.replace(NOINFO, "").strip(), flag


def clean(text, channel="site"):
    text = scrub(text or "")
    text = _MD_LINK.sub(lambda m: f"\x00A{m.group(2)}\x00T{m.group(1)}\x00E", text)  # protect links
    text = html.escape(text, quote=False)
    for tag in _ALLOWED:
        text = text.replace(f"&lt;{tag}&gt;", f"<{tag}>").replace(f"&lt;/{tag}&gt;", f"</{tag}>")
    text = _HEAD.sub(r"<b>\1</b>", text)
    text = _BOLD.sub(r"<b>\1</b>", text)
    text = _CODE.sub(r"<code>\1</code>", text)
    text = _BULLET.sub("• ", text)

    def link(url, label):
        url = html.escape(url, quote=True)
        if channel == "site" and not url.startswith("/") and "khalilovn.uz" not in url:
            return f'<a href="{url}" target="_blank" rel="noopener">{label}</a>'
        return f'<a href="{url}">{label}</a>'

    text = re.sub("\x00A(.*?)\x00T(.*?)\x00E", lambda m: link(m.group(1), m.group(2)), text)
    text = _URL.sub(lambda m: link(html.unescape(m.group(1)), m.group(1)), text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def text_only(html_text):
    """For history/context: tags out, entities back."""
    return html.unescape(re.sub(r"<[^>]+>", "", html_text or "")).strip()


def split_telegram(text, limit=4000):
    """Split long HTML for Telegram without breaking a tag."""
    if len(text) <= limit:
        return [text]
    parts, cur = [], ""
    for para in text.split("\n"):
        if len(cur) + len(para) + 1 > limit:
            parts.append(cur)
            cur = para
        else:
            cur = f"{cur}\n{para}" if cur else para
    if cur:
        parts.append(cur)
    return [p for p in parts if p.strip()]
