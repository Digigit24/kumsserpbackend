from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from apps.core.cache_mixins import CachedReadOnlyMixin

from apps.core.mixins import CollegeScopedModelViewSet, RelatedCollegeScopedModelViewSet
from .models import Hostel, RoomType, Room, Bed, HostelAllocation, HostelFee
from .serializers import (
    HostelSerializer,
    RoomTypeSerializer,
    RoomSerializer,
    BedSerializer,
    HostelAllocationSerializer,
    HostelFeeSerializer,
)


class HostelViewSet(CollegeScopedModelViewSet):
    queryset = Hostel.objects.all_colleges()
    serializer_class = HostelSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['hostel_type', 'is_active']
    search_fields = ['name']
    ordering_fields = ['name', 'capacity', 'created_at']
    ordering = ['name']


class RoomTypeViewSet(RelatedCollegeScopedModelViewSet):
    queryset = RoomType.objects.select_related('hostel')
    serializer_class = RoomTypeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['hostel', 'is_active']
    ordering_fields = ['created_at', 'monthly_fee']
    ordering = ['created_at']
    related_college_lookup = 'hostel__college_id'


class RoomViewSet(RelatedCollegeScopedModelViewSet):
    queryset = Room.objects.select_related('hostel', 'room_type')
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['hostel', 'room_type', 'is_active']
    ordering_fields = ['room_number', 'capacity', 'occupied_beds']
    ordering = ['room_number']
    related_college_lookup = 'hostel__college_id'


class BedViewSet(RelatedCollegeScopedModelViewSet):
    queryset = Bed.objects.select_related('room__hostel', 'room__room_type')
    serializer_class = BedSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['room', 'status', 'is_active']
    ordering_fields = ['bed_number']
    ordering = ['bed_number']
    related_college_lookup = 'room__hostel__college_id'


class HostelAllocationViewSet(RelatedCollegeScopedModelViewSet):
    queryset = HostelAllocation.objects.select_related('student', 'hostel', 'room', 'bed')
    serializer_class = HostelAllocationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['student', 'hostel', 'room', 'bed', 'is_current', 'is_active']
    ordering_fields = ['from_date', 'created_at']
    ordering = ['-from_date']
    related_college_lookup = 'hostel__college_id'


class HostelFeeViewSet(RelatedCollegeScopedModelViewSet):
    queryset = HostelFee.objects.select_related('allocation__hostel', 'allocation__student')
    serializer_class = HostelFeeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['allocation', 'month', 'year', 'is_paid', 'is_active']
    ordering_fields = ['due_date', 'created_at']
    ordering = ['-due_date']
    related_college_lookup = 'allocation__hostel__college_id'
