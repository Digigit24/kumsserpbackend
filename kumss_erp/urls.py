"""
URL configuration for kumss_erp project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from apps.accounts.views import LoginViewNoAuth

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # Auth overrides
    path('api/v1/auth/login/', LoginViewNoAuth.as_view(), name='rest_login'),

    # API v1 Endpoints
    path('api/v1/core/', include('apps.core.urls', namespace='core')),
    path('api/v1/accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('api/v1/academic/', include('apps.academic.urls')),
    path('api/v1/students/', include('apps.students.urls')),
    path('api/v1/teachers/', include('apps.teachers.urls')),
    path('api/v1/attendance/', include('apps.attendance.urls')),
    path('api/v1/auth/', include('dj_rest_auth.urls')),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # DRF Browsable API Authentication
    path('api-auth/', include('rest_framework.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Customize admin site headers
admin.site.site_header = 'KUMSS ERP Administration'
admin.site.site_title = 'KUMSS ERP Admin'
admin.site.index_title = 'Welcome to KUMSS ERP Administration'
