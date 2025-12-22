from django.apps import AppConfig


class OnlineExamConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.online_exam'
    verbose_name = 'Online Exam'

    def ready(self):
        try:
            import apps.online_exam.signals  # noqa: F401
        except Exception:
            pass
