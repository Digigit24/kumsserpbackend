"""
Signals for Hostel app.
Lightweight updates for occupancy and fees; extend with full logic as needed.
"""
from datetime import date
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from .models import HostelAllocation, HostelFee, Bed, Room


def _update_room_and_bed(allocation, occupy=True):
    bed = allocation.bed
    room = allocation.room
    if bed:
        bed.status = 'occupied' if occupy else 'vacant'
        bed.save(update_fields=['status', 'updated_at'])
    if room:
        delta = 1 if occupy else -1
        room.occupied_beds = max(0, room.occupied_beds + delta)
        room.save(update_fields=['occupied_beds', 'updated_at'])


@receiver(post_save, sender=HostelAllocation)
def hostel_allocation_post_save(sender, instance, created, **kwargs):
    if created:
        _update_room_and_bed(instance, occupy=True)
        # Create a single current month fee record as a placeholder
        if not instance.fees.exists():
            today = date.today()
            HostelFee.objects.create(
                allocation=instance,
                month=today.month,
                year=today.year,
                amount=instance.room.room_type.monthly_fee if instance.room and instance.room.room_type else 0,
                due_date=today,
                created_by=instance.created_by,
                updated_by=instance.updated_by,
            )


@receiver(pre_delete, sender=HostelAllocation)
def hostel_allocation_pre_delete(sender, instance, using, **kwargs):
    _update_room_and_bed(instance, occupy=False)


@receiver(post_save, sender=HostelFee)
def hostel_fee_post_save(sender, instance, created, **kwargs):
    # Placeholder for payment receipt/notification logic when paid
    return
