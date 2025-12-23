from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

# Register your viewsets here
# router.register(r'endpoint', YourViewSet, basename='endpoint')

app_name = 'rohit'

urlpatterns = [
    path('', include(router.urls)),
]
