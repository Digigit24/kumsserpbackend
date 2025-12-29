from django.db.models import Sum, Count, Q, F
from django.db.models.functions import Coalesce
from django.utils import timezone
from decimal import Decimal

from apps.hostel.models import Hostel, Room, Bed, HostelAllocation, HostelFee


class HostelStatsService:
    """Service class for hostel statistics calculations"""

    def __init__(self, college_id, filters=None):
        self.college_id = college_id
        self.filters = filters or {}

    def get_occupancy_stats(self):
        """Calculate hostel occupancy statistics"""
        hostels = Hostel.objects.filter(college_id=self.college_id, is_active=True)

        total_hostels = hostels.count()

        rooms = Room.objects.filter(hostel__college_id=self.college_id, hostel__is_active=True)
        total_rooms = rooms.count()

        beds = Bed.objects.filter(room__hostel__college_id=self.college_id, room__hostel__is_active=True)
        total_beds = beds.count()
        occupied_beds = beds.filter(status='OCCUPIED').count()
        vacant_beds = beds.filter(status='VACANT').count()

        occupancy_rate = (occupied_beds / total_beds * 100) if total_beds > 0 else 0

        # Total students in hostel
        allocations = HostelAllocation.objects.filter(
            hostel__college_id=self.college_id,
            is_current=True
        )

        total_students = allocations.values('student').distinct().count()

        return {
            'total_hostels': total_hostels,
            'total_rooms': total_rooms,
            'total_beds': total_beds,
            'occupied_beds': occupied_beds,
            'vacant_beds': vacant_beds,
            'occupancy_rate': round(occupancy_rate, 2),
            'total_students': total_students,
        }

    def get_fee_stats(self):
        """Calculate hostel fee statistics"""
        fees = HostelFee.objects.filter(
            allocation__hostel__college_id=self.college_id
        )

        if self.filters.get('from_date'):
            fees = fees.filter(due_date__gte=self.filters['from_date'])
        if self.filters.get('to_date'):
            fees = fees.filter(due_date__lte=self.filters['to_date'])

        total_amount = fees.aggregate(
            total=Coalesce(Sum('amount'), Decimal('0'))
        )['total']

        collected_amount = fees.filter(is_paid=True).aggregate(
            total=Coalesce(Sum('amount'), Decimal('0'))
        )['total']

        outstanding_amount = total_amount - collected_amount

        collection_rate = (collected_amount / total_amount * 100) if total_amount > 0 else 0

        return {
            'total_amount': total_amount,
            'collected_amount': collected_amount,
            'outstanding_amount': outstanding_amount,
            'collection_rate': round(collection_rate, 2),
        }
