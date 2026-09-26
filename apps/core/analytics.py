"""Privacy-friendly visit counting: no cookies, no third parties.

A visitor is identified per day by a hash of (secret key, date, IP, user
agent). The raw IP is never stored, and because the date is part of the
hash, the same person cannot be followed across days.

Ignored: staff users (your own visits), bots, admin / static / API
requests and anything that is not a successful HTML page.
"""
import hashlib
import re
from urllib.parse import urlparse

from django.conf import settings
from django.db.models import F
from django.utils import timezone

BOTS = re.compile(
    r"bot|crawl|spider|slurp|preview|monitor|lighthouse|headless|curl|wget|python-requests", re.I)
SKIP = ("/admin", "/static", "/media", "/api", "/i18n", "/favicon",
        "/robots.txt", "/sitemap.xml")


def client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def device_of(user_agent):
    if re.search(r"iPad|Tablet", user_agent, re.I):
        return "tablet"
    if re.search(r"Mobi|Android|iPhone", user_agent, re.I):
        return "mobile"
    return "desktop"


class AnalyticsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            if self._should_track(request, response):
                record(request)
        except Exception:  # analytics must never break a page
            pass
        return response

    @staticmethod
    def _should_track(request, response):
        if request.method != "GET" or response.status_code != 200:
            return False
        if not response.get("Content-Type", "").startswith("text/html"):
            return False
        if request.path.startswith(SKIP) or request.path.startswith("/" + settings.ADMIN_URL):
            return False
        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated and user.is_staff:
            return False
        return not BOTS.search(request.META.get("HTTP_USER_AGENT", ""))


def record(request):
    from .models import DailyVisitor, PageView

    today = timezone.localdate()
    path = request.path[:300]

    if not PageView.objects.filter(path=path, date=today).update(count=F("count") + 1):
        PageView.objects.create(path=path, date=today)

    user_agent = request.META.get("HTTP_USER_AGENT", "")[:300]
    raw = f"{settings.SECRET_KEY}|{today}|{client_ip(request)}|{user_agent}"
    visitor = hashlib.sha256(raw.encode()).hexdigest()[:32]

    referrer = urlparse(request.META.get("HTTP_REFERER", "")).netloc.lower()
    if referrer == request.get_host().lower():
        referrer = ""

    DailyVisitor.objects.get_or_create(
        date=today, visitor=visitor,
        defaults={"device": device_of(user_agent), "referrer": referrer[:120],
                  "first_path": path},
    )
