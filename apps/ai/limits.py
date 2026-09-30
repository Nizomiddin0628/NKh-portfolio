"""Rate limits, so one visitor (or a bot) cannot burn the whole quota.

- per visitor: AI_GUEST_HOURLY questions per hour (cache counter) and
  AI_GUEST_DAILY per day (counted in AiLog);
- everyone together: AI_DAILY_LIMIT per day for guests. The owner is never
  limited but is still logged.
"""
import hashlib

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from .models import AiLog


def ip_hash(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    ip = forwarded.split(",")[0].strip() if forwarded else request.META.get("REMOTE_ADDR", "")
    return hashlib.sha256(f"{settings.SECRET_KEY}|ai|{ip}".encode()).hexdigest()[:32]


def _today_count(**flt):
    start = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
    return AiLog.objects.filter(created_at__gte=start, **flt).count()


def guest_allowed(iphash):
    """Return None when the guest may ask, else an error code."""
    hourly = int(getattr(settings, "AI_GUEST_HOURLY", 20))
    daily = int(getattr(settings, "AI_GUEST_DAILY", 60))
    total = int(getattr(settings, "AI_DAILY_LIMIT", 400))

    key = f"ai:hour:{iphash}"
    n = cache.get(key, 0)
    if n >= hourly:
        return "limit"
    if _today_count(ip_hash=iphash, role="guest") >= daily:
        return "limit"
    if _today_count(role="guest", kind__in=("ask", "voice", "file")) >= total:
        return "quota"
    return None


def count_guest(iphash):
    key = f"ai:hour:{iphash}"
    try:
        cache.add(key, 0, 3600)
        cache.incr(key)
    except Exception:
        cache.set(key, cache.get(key, 0) + 1, 3600)
