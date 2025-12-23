from django.apps import AppConfig


class RohitConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.rohit'
    verbose_name = 'Rohit'

    def ready(self):
        import apps.rohit.signals  # noqa
