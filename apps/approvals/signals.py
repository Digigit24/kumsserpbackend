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
    if created:
        # Notifications are created in the view layer; keep hook for extensions
        pass


@receiver(post_save, sender=ApprovalAction)
def approval_action_created(sender, instance, created, **kwargs):
    if not created or instance.action not in ['approve', 'reject']:
        return

    approval_request = instance.approval_request

    # Fee payment example
    if approval_request.request_type == 'fee_payment' and approval_request.status == 'approved':
        try:
            from apps.fees.models import FeeCollection
            fee_collection_id = approval_request.metadata.get('fee_collection_id')
            if fee_collection_id:
                fee_collection = FeeCollection.objects.get(id=fee_collection_id)
                if hasattr(fee_collection, 'is_approved'):
                    fee_collection.is_approved = True
                    fee_collection.save(update_fields=['is_approved'])
        except Exception as e:
            print(f"Error updating fee collection: {e}")

    # Procurement requirement approval
    if approval_request.request_type == 'procurement_requirement':
        try:
            from apps.store.models import ProcurementRequirement
            req = ProcurementRequirement.objects.filter(id=approval_request.object_id).first()
            if req and approval_request.status == 'approved':
                req.approve()
            elif req and approval_request.status == 'rejected':
                req.cancel()
        except Exception as exc:
            print(f"[Approvals] Error updating procurement requirement: {exc}")

    # Goods inspection approval
    if approval_request.request_type == 'goods_inspection':
        try:
            from apps.store.models import GoodsReceiptNote
            grn = GoodsReceiptNote.objects.filter(id=approval_request.object_id).first()
            if grn and approval_request.status == 'approved':
                grn.status = 'approved'
                grn.save(update_fields=['status', 'updated_at'])
        except Exception as exc:
            print(f"[Approvals] Error updating GRN: {exc}")

    # Store indent approval
    if approval_request.request_type == 'store_indent':
        try:
            from apps.store.models import StoreIndent
            indent = StoreIndent.objects.filter(id=approval_request.object_id).first()
            if indent and approval_request.status == 'approved':
                indent.approve(user=instance.actor)
            elif indent and approval_request.status == 'rejected':
                indent.reject(user=instance.actor, reason=instance.comment)
        except Exception as exc:
            print(f"[Approvals] Error updating indent: {exc}")
