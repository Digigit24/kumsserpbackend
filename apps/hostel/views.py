from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.core.mixins import CollegeScopedModelViewSet
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
    queryset = Hostel.objects.all()
    serializer_class = HostelSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['hostel_type', 'is_active']
    search_fields = ['name']
    ordering_fields = ['name', 'capacity', 'created_at']
    ordering = ['name']


class RoomTypeViewSet(viewsets.ModelViewSet):
    queryset = RoomType.objects.all()
    serializer_class = RoomTypeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['hostel', 'is_active']
    ordering_fields = ['created_at', 'monthly_fee']
    ordering = ['created_at']


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['hostel', 'room_type', 'is_active']
    ordering_fields = ['room_number', 'capacity', 'occupied_beds']
    ordering = ['room_number']


class BedViewSet(viewsets.ModelViewSet):
    queryset = Bed.objects.all()
    serializer_class = BedSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['room', 'status', 'is_active']
    ordering_fields = ['bed_number']
    ordering = ['bed_number']


class HostelAllocationViewSet(viewsets.ModelViewSet):
    queryset = HostelAllocation.objects.all()
    serializer_class = HostelAllocationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['student', 'hostel', 'room', 'bed', 'is_current', 'is_active']
    ordering_fields = ['from_date', 'created_at']
    ordering = ['-from_date']


class HostelFeeViewSet(viewsets.ModelViewSet):
    queryset = HostelFee.objects.all()
    serializer_class = HostelFeeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['allocation', 'month', 'year', 'is_paid', 'is_active']
    ordering_fields = ['due_date', 'created_at']
    ordering = ['-due_date']
