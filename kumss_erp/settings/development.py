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

# CORS settings for development (if needed)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3030",
    "https://kumss.celiyo.com"

]   
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True


# Force console logging in development for easier debugging.
LOG_TO_FILE = False
LOGGING['handlers']['console']['level'] = 'DEBUG'
LOGGING['loggers']['apps']['level'] = 'DEBUG'
LOGGING['loggers']['django.request']['level'] = 'DEBUG'
LOGGING['loggers']['django.server'] = {
    'handlers': ['console'],
    'level': 'INFO',
    'propagate': False,
}

# Disable some security features for easier development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# WebSocket Channel Layer - use InMemory for development to avoid Redis dependency
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}
# Cache - use local memory in development to avoid Redis dependency
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "kumss-dev-cache",
    }
}
