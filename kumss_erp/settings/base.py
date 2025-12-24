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
    'apps.reports',

    'debug_toolbar',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS - must be before CommonMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.core.middleware.TenantMiddleware',  # Multi-tenant support

    'debug_toolbar.middleware.DebugToolbarMiddleware',

]
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
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',  # Use Spectacular for schema generation
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
}

# dj-rest-auth configuration
REST_AUTH = {
    'TOKEN_SERIALIZER': 'apps.accounts.serializers.TokenWithUserSerializer',
    'USER_DETAILS_SERIALIZER': 'apps.accounts.serializers.UserListSerializer',
}

# Legacy support (for older dj-rest-auth versions)
REST_AUTH_SERIALIZERS = {
    'TOKEN_SERIALIZER': 'apps.accounts.serializers.TokenWithUserSerializer',
    'USER_DETAILS_SERIALIZER': 'apps.accounts.serializers.UserListSerializer',
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
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]
CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://localhost:3000",
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
            'CollegeID': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'X-College-ID',
                'description': 'College identifier for college-scoped access (required for most endpoints)'
            },
            'TenantID': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'X-Tenant-ID',
                'description': '[LEGACY] Tenant identifier - use X-College-ID instead'
            }
        }
    },
    'SECURITY': [{'CollegeID': []}],  # Make X-College-ID globally available

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
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'debug.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 2,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'apps': { # Capture logs from all apps within the 'apps' directory
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'corsheaders': { # Specifically log corsheaders middleware
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        }
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'DEBUG',
    },
}
