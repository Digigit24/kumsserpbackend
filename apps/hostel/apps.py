from django.apps import AppConfig


class HostelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.hostel'
    verbose_name = 'Hostel'

    def ready(self):
        try:
            import apps.hostel.signals  # noqa: F401
        except Exception:
            pass
