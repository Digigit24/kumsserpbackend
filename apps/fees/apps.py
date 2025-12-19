from django.apps import AppConfig


class FeesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.fees'
    verbose_name = 'Fees'

    def ready(self):
        # Register signals
        try:
            import apps.fees.signals  # noqa: F401
        except Exception:
            # Avoid hard crash during app loading; real errors will surface in logs/tests.
            pass
