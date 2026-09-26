"""Numbers for the admin dashboard.

60 days are loaded so every 7-day figure can be compared with the 7 days
before it. The daily series go to the page as JSON for Chart.js.
"""
from datetime import timedelta

from django import template
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone

from apps.core.models import ContactMessage, DailyVisitor, PageView

register = template.Library()

DAYS = 60


def _by_day(queryset, field, value):
    return dict(queryset.order_by().values_list(field).annotate(n=value))


def _card(label, series):
    current = sum(series[-7:])
    previous = sum(series[-14:-7])
    # No previous data: a percentage would be meaningless (division by zero)
    trend = None if previous == 0 else round((current - previous) * 100 / previous)
    return {"label": label, "value": current, "trend": trend,
            "today": series[-1], "d30": sum(series[-30:])}


@register.simple_tag
def portfolio_stats():
    today = timezone.localdate()
    start = today - timedelta(days=DAYS - 1)
    days = [start + timedelta(days=i) for i in range(DAYS)]

    views = _by_day(PageView.objects.filter(date__gte=start), "date", Sum("count"))
    people = _by_day(DailyVisitor.objects.filter(date__gte=start), "date", Count("id"))
    messages = _by_day(
        ContactMessage.objects.filter(created_at__date__gte=start)
        .annotate(day=TruncDate("created_at")), "day", Count("id"))

    s_views = [views.get(d, 0) for d in days]
    s_people = [people.get(d, 0) for d in days]
    s_messages = [messages.get(d, 0) for d in days]

    since_30 = today - timedelta(days=29)
    recent = DailyVisitor.objects.filter(date__gte=since_30).order_by()

    devices = [{"label": (row["device"] or "unknown").capitalize(), "n": row["n"]}
               for row in recent.values("device").annotate(n=Count("id")).order_by("-n")]

    sources = [{"label": row["referrer"], "n": row["n"]}
               for row in recent.exclude(referrer="").values("referrer")
               .annotate(n=Count("id")).order_by("-n")[:5]]
    direct = recent.filter(referrer="").count()
    if direct:
        sources.insert(0, {"label": "Direct", "n": direct})

    pages = list(PageView.objects.filter(date__gte=since_30).order_by()
                 .values("path").annotate(n=Sum("count")).order_by("-n")[:8])
    top = pages[0]["n"] if pages else 1
    for page in pages:
        page["pct"] = round(page["n"] * 100 / top)

    return {
        "cards": [_card("Visitors", s_people), _card("Page views", s_views),
                  _card("Messages", s_messages)],
        "unread": ContactMessage.objects.filter(is_read=False).count(),
        "total_messages": ContactMessage.objects.count(),
        "top_pages": pages,
        "latest": ContactMessage.objects.all()[:6],
        "has_traffic": any(s_views[-30:]),
        "series": {
            "labels": [d.isoformat() for d in days],
            "people": s_people,
            "views": s_views,
            "devices": devices,
            "sources": sources,
        },
    }
