from django.apps import AppConfig


class TeachersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.teachers'
    verbose_name = 'Teacher Management'

    def ready(self):
        import apps.teachers.signals  # noqa
