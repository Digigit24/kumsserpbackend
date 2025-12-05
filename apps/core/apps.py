from django.apps import AppConfig


class CoreConfig(AppConfig):
    """
    Configuration for the Core application.
    Contains abstract base models used across all other apps.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    verbose_name = 'Core'

    def ready(self):
        """
        Import signals when the app is ready.
        """
        import apps.core.signals  # noqa
