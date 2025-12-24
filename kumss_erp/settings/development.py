"""
Development-specific settings for kumss_erp project.
"""
from .base import *

# Debug mode enabled for development
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']

# Development-specific installed apps
# INSTALLED_APPS += [
#     'django_extensions',  # If you want to use shell_plus and other tools
# ]

# Database - can override if needed for local development
# DATABASES['default']['NAME'] = 'kumss_erp_dev'

# Email backend for development (console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# CORS settings for development - allow all origins for easier testing
CORS_ALLOW_ALL_ORIGINS = True  # Allow requests from any origin in development
CORS_ALLOW_CREDENTIALS = True

# Disable some security features for easier development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
