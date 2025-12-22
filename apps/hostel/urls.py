"""
URL configuration for Hostel app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    HostelViewSet,
    RoomTypeViewSet,
    RoomViewSet,
    BedViewSet,
    HostelAllocationViewSet,
    HostelFeeViewSet,
)

router = DefaultRouter()
router.register(r'hostels', HostelViewSet, basename='hostel')
router.register(r'room-types', RoomTypeViewSet, basename='roomtype')
router.register(r'rooms', RoomViewSet, basename='room')
router.register(r'beds', BedViewSet, basename='bed')
router.register(r'allocations', HostelAllocationViewSet, basename='hostelallocation')
router.register(r'fees', HostelFeeViewSet, basename='hostelfee')

urlpatterns = [
    path('', include(router.urls)),
]
