from django.db.models import Sum, Count, Avg, Q, F
from django.db.models.functions import Coalesce
from django.utils import timezone
from decimal import Decimal

from apps.communication.models import BulkMessage, MessageLog, Event, EventRegistration


class CommunicationStatsService:
    """Service class for communication statistics calculations"""

    def __init__(self, college_id, filters=None):
        self.college_id = college_id
        self.filters = filters or {}

    def get_message_stats(self):
        """Calculate message delivery statistics"""
        messages = BulkMessage.objects.filter(college_id=self.college_id)

        if self.filters.get('from_date'):
            messages = messages.filter(created_at__gte=self.filters['from_date'])
        if self.filters.get('to_date'):
            messages = messages.filter(created_at__lte=self.filters['to_date'])

        total_messages = messages.count()
        sent_count = messages.aggregate(total=Coalesce(Sum('sent_count'), 0))['total']
        failed_count = messages.aggregate(total=Coalesce(Sum('failed_count'), 0))['total']

        # Message logs for detailed stats
        logs = MessageLog.objects.filter(bulk_message__college_id=self.college_id)

        if self.filters.get('from_date'):
            logs = logs.filter(created_at__gte=self.filters['from_date'])
        if self.filters.get('to_date'):
            logs = logs.filter(created_at__lte=self.filters['to_date'])

        delivered_count = logs.filter(status='DELIVERED').count()
        pending_count = logs.filter(status='PENDING').count()

        total_logs = logs.count()
        delivery_rate = (delivered_count / total_logs * 100) if total_logs > 0 else 0

        return {
            'total_messages': total_messages,
            'sent_count': sent_count,
            'delivered_count': delivered_count,
            'failed_count': failed_count,
            'pending_count': pending_count,
            'delivery_rate': round(delivery_rate, 2),
        }

    def get_event_stats(self):
        """Calculate event statistics"""
        events = Event.objects.filter(college_id=self.college_id)

        if self.filters.get('from_date'):
            events = events.filter(event_date__gte=self.filters['from_date'])
        if self.filters.get('to_date'):
            events = events.filter(event_date__lte=self.filters['to_date'])

        total_events = events.count()
        upcoming_events = events.filter(event_date__gte=timezone.now().date()).count()
        completed_events = events.filter(event_date__lt=timezone.now().date()).count()

        # Registration stats
        registrations = EventRegistration.objects.filter(event__college_id=self.college_id)

        if self.filters.get('from_date'):
            registrations = registrations.filter(event__event_date__gte=self.filters['from_date'])
        if self.filters.get('to_date'):
            registrations = registrations.filter(event__event_date__lte=self.filters['to_date'])

        total_registrations = registrations.count()

        # Average attendance
        attended_registrations = registrations.filter(status='ATTENDED').count()
        average_attendance = (attended_registrations / total_registrations * 100) if total_registrations > 0 else 0

        return {
            'total_events': total_events,
            'upcoming_events': upcoming_events,
            'completed_events': completed_events,
            'total_registrations': total_registrations,
            'average_attendance': round(average_attendance, 2),
        }

    def get_all_stats(self):
        """Get all communication statistics combined"""
        return {
            'messages': self.get_message_stats(),
            'events': self.get_event_stats(),
            'generated_at': timezone.now(),
        }
