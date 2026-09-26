from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "apps.core"
    verbose_name = "Site"

    def ready(self):
        from django.conf import settings
        from django.utils.autoreload import autoreload_started

        from . import checks  # noqa: F401  (registers the startup checks)

        # Restart the dev server when .env changes, like it does for .py files.
        # Otherwise a running server keeps the old settings without a word.
        def watch_env(sender, **kwargs):
            sender.watch_dir(settings.BASE_DIR, ".env")

        autoreload_started.connect(watch_env, weak=False)
