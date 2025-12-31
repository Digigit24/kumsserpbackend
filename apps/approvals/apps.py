# -*- coding: utf-8 -*-
"""
App configuration for approvals app.
"""
from django.apps import AppConfig


class ApprovalsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.approvals'
    verbose_name = 'Approvals'

    def ready(self):
        """Import signals when app is ready."""
        import apps.approvals.signals
