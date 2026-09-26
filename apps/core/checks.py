"""Startup checks: say out loud when a notification channel is off.

Without these, a contact message is saved but nobody is told, and the
missing setting is only discovered when an important message never arrives.
Shown on `runserver` and `manage.py check`.
"""
from django.conf import settings
from django.core import checks


@checks.register()
def notification_channels(app_configs, **kwargs):
    issues = []
    if not (getattr(settings, "TELEGRAM_BOT_TOKEN", "") and getattr(settings, "TELEGRAM_CHAT_ID", "")):
        issues.append(checks.Warning(
            "Telegram notifications are off.",
            hint="Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env, then run: python manage.py notify_test",
            id="core.W001",
        ))
    if "smtp" not in settings.EMAIL_BACKEND:
        issues.append(checks.Warning(
            "Email notifications are off.",
            hint="Set EMAIL_HOST_PASSWORD (a Gmail app password) in .env.",
            id="core.W002",
        ))
    return issues
