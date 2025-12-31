# -*- coding: utf-8 -*-
"""
Signals for approval system.
Handles automatic notifications and status updates.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType

from .models import ApprovalRequest, ApprovalAction, Notification


@receiver(post_save, sender=ApprovalRequest)
def approval_request_created(sender, instance, created, **kwargs):
    """
    Send notifications when approval request is created.
    This signal is fired when a new approval request is submitted.
    """
    if created:
        # Notifications are created in the view, so we don't duplicate here
        # This signal can be used for additional logic like logging, webhooks, etc.
        pass


@receiver(post_save, sender=ApprovalAction)
def approval_action_created(sender, instance, created, **kwargs):
    """
    Handle post-approval actions like updating related objects.
    """
    if created and instance.action in ['approve', 'reject']:
        approval_request = instance.approval_request

        # If this is a fee payment approval and it's approved
        if (approval_request.request_type == 'fee_payment' and
            approval_request.status == 'approved'):

            # Update the fee collection status
            try:
                from apps.fees.models import FeeCollection
                fee_collection_id = approval_request.metadata.get('fee_collection_id')
                if fee_collection_id:
                    fee_collection = FeeCollection.objects.get(id=fee_collection_id)
                    # Mark as approved (you may need to add this field to FeeCollection)
                    if hasattr(fee_collection, 'is_approved'):
                        fee_collection.is_approved = True
                        fee_collection.save(update_fields=['is_approved'])
            except Exception as e:
                # Log error but don't fail
                print(f"Error updating fee collection: {e}")
