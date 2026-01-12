"""
Django settings for kumss_erp project.
Base settings shared across all environments.
"""
import os
import sys
from pathlib import Path
from decouple import config
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Add apps directory to Python path
sys.path.insert(0, str(BASE_DIR / 'apps'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production-12345')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'grappelli',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'corsheaders',  # CORS headers for frontend integration
    'rest_framework',
    'rest_framework.authtoken',
    'dj_rest_auth',
    'drf_spectacular',  # API documentation
    'django_filters',
    'storages',  # AWS S3 storage
    'mptt',  # Django MPTT for tree structures

    'django_extensions',

    # Local apps
    'apps.core',
    'apps.accounts',
    'apps.academic',
    'apps.students',
    'apps.teachers',
    'apps.attendance',
    'apps.fees',
    'apps.accounting',
    'apps.examinations',
    'apps.online_exam',
    'apps.hostel',
    'apps.library',
    'apps.store',
    'apps.hr',
    'apps.communication',
    'apps.approvals',  # Approval and notification system
    'apps.reports',
    'apps.stats',
    #'apps.core.apps.CoreConfig',

    'channels',
    'debug_toolbar',

]

ASGI_APPLICATION = 'kumss_erp.asgi.application'

# Redis configuration for real-time messaging (SSE + Pub/Sub)
REDIS_URL = config('REDIS_URL', default='redis://127.0.0.1:6379')

# WebSocket Microservice URL
WEBSOCKET_SERVICE_URL = config('WEBSOCKET_SERVICE_URL', default='http://localhost:3001')

# Django Cache Configuration using Redis
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': REDIS_URL,
        'KEY_PREFIX': 'kumss',
        'TIMEOUT': 300,  # 5 minutes default
    }
}

# Channel Layers - Disabled (Using SSE instead of WebSocket)
# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': 'channels_redis.core.RedisChannelLayer',
#         'CONFIG': {
#             "hosts": [config('REDIS_URL', default='redis://127.0.0.1:6379')],
#         },
#     },
# }

MIDDLEWARE = [
    'django.middleware.gzip.GZipMiddleware',  # Compress all responses
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS - must be before CommonMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.core.middleware.CollegeMiddleware',  # Multi-college support

    'debug_toolbar.middleware.DebugToolbarMiddleware',

]

# GZip compression settings - compress all responses regardless of size
GZIP_MINIMUM_SIZE = 0  # Compress even tiny responses
# Debug Toolbar
INTERNAL_IPS = [
    "127.0.0.1",
]

ROOT_URLCONF = 'kumss_erp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'kumss_erp.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# Parse database URL from environment variable (Neon PostgreSQL)
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default='postgresql://postgres:postgres@localhost:5432/kumss_erp_db'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Use a local SQLite database when running tests to avoid touching Postgres
TESTING = any(arg in sys.argv for arg in ('test', 'pytest'))
if TESTING:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        "NAME": ":memory:",
    }

# Use local SQLite for tests to avoid touching remote Postgres and ensure NAME is a string
DATABASES['default']['TEST'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': str(BASE_DIR / 'test_db.sqlite3'),
}



# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# AWS S3 Configuration for django-storages
# S3Boto3Storage will automatically use these settings
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default='')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='main-bucket-digitech')
AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='ap-south-1')
AWS_S3_CUSTOM_DOMAIN = config('AWS_S3_CUSTOM_DOMAIN', default=None)
AWS_DEFAULT_ACL = 'private'
AWS_S3_FILE_OVERWRITE = False
AWS_QUERYSTRING_AUTH = True  # Generate signed URLs for private files

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Django REST Framework
# https://www.django-rest-framework.org/api-guide/settings/

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'apps.core.pagination.CustomPageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',  # Use Spectacular for schema generation
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
}

# dj-rest-auth
REST_AUTH_SERIALIZERS = {
    'TOKEN_SERIALIZER': 'apps.accounts.serializers.TokenWithUserSerializer',
}

# Custom user model
AUTH_USER_MODEL = 'accounts.User'


# DRF Spectacular Settings
# https://drf-spectacular.readthedocs.io/en/latest/settings.html

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'x-tenant-id',
    'x-college-id',
]

# Allow frontend apps (React/Vite/Next/etc.) to call the API locally
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://localhost:3000",
    "http://127.0.0.1:3030",
    "http://localhost:3030",
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "https://kumss.celiyo.com"
]
CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://localhost:3000",
    "http://127.0.0.1:3030",
    "http://localhost:3030",
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]

SPECTACULAR_SETTINGS = {
    'TITLE': 'KUMSS ERP API',
    'DESCRIPTION': 'Knowledge University Management System - Comprehensive ERP API Documentation',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': r'/api/v1/',
    'COMPONENT_SPLIT_REQUEST': True,

    # Swagger UI settings
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
        'filter': True,
    },

    # OpenAPI 3 settings
    'SERVERS': [
        {'url': 'http://localhost:8000', 'description': 'Development server'},
        {'url': 'https://api.kumss.edu', 'description': 'Production server'},
    ],

    # Security scheme
    'APPEND_COMPONENTS': {
        'securitySchemes': {
            'TenantID': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'X-Tenant-ID',
                'description': 'Tenant identifier for multi-tenant access'
            }
        }
    },

    # Auto-generate IDs
    'CAMELIZE_NAMES': False,
    'ENUM_NAME_OVERRIDES': {
        'HolidayTypeEnum': 'apps.core.models.Holiday.HOLIDAY_TYPE_CHOICES',
        'WeekDayEnum': 'apps.core.models.Weekend.DAY_CHOICES',
        'ActionTypeEnum': 'apps.core.models.ActivityLog.ACTION_CHOICES',
    },
}

# Logging Configuration
# https://docs.djangoproject.com/en/5.0/topics/logging/
LOG_TO_FILE = config('LOG_TO_FILE', default=False, cast=bool)
DEFAULT_LOG_HANDLERS = ['console']
if LOG_TO_FILE:
    DEFAULT_LOG_HANDLERS.append('file')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': DEFAULT_LOG_HANDLERS,
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': DEFAULT_LOG_HANDLERS,
            'level': 'INFO',
            'propagate': False,
        },
        'apps': { # Capture logs from all apps within the 'apps' directory
            'handlers': DEFAULT_LOG_HANDLERS,
            'level': 'INFO',
            'propagate': True,
        },
        'corsheaders': { # Specifically log corsheaders middleware
            'handlers': DEFAULT_LOG_HANDLERS,
            'level': 'INFO',
            'propagate': True,
        },
        'django.db.backends': { # Log SQL queries
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        }
    },
    'root': {
        'handlers': DEFAULT_LOG_HANDLERS,
        'level': 'INFO',
    },
}

if LOG_TO_FILE:
    LOGGING['handlers']['file'] = {
        'level': 'DEBUG',
        'class': 'logging.FileHandler',
        'filename': BASE_DIR / 'logs' / 'debug.log',
        'formatter': 'verbose',
    }
