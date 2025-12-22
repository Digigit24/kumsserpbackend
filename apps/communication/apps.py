from django.apps import AppConfig


class CommunicationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.communication'
    verbose_name = 'Communication Management'

    def ready(self):
        import apps.communication.signals  # noqa
