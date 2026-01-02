"""
Signals for Store app.
Handles stock adjustments, credit tracking, and central store workflows.
"""
from decimal import Decimal

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType

from apps.approvals.models import ApprovalRequest
from apps.core.models import College
from .models import (
    StockReceive,
    StoreItem,
    StoreSale,
    SaleItem,
    StoreCredit,
    PrintJob,
    SupplierQuotation,
    PurchaseOrder,
    GoodsReceiptNote,
    GoodsReceiptItem,
    StoreIndent,
    MaterialIssueNote,
    CentralStoreInventory,
    InventoryTransaction,
)
from .utils import generate_document_number


def _adjust_stock_from_sale(sale):
    """Reduce stock based on sale items."""
    for line in sale.items.all():
        if line.item_id:
            line.item.adjust_stock(-line.quantity)


@receiver(post_save, sender=StockReceive)
def stock_receive_post_save(sender, instance, created, **kwargs):
    if not created:
        return
    item = instance.item
    if item:
        item.adjust_stock(instance.quantity)
        if item.stock_quantity <= item.min_stock_level:
            print(f"[Store] Stock low for {item.name}: {item.stock_quantity}")


@receiver(post_save, sender=StoreSale)
def store_sale_post_save(sender, instance, created, **kwargs):
    if not created:
        return

    _adjust_stock_from_sale(instance)

    if instance.payment_status != 'paid':
        buyer = instance.student or None
        if buyer:
            StoreCredit.objects.create(
                student=buyer,
                amount=instance.total_amount,
                transaction_type='credit',
                date=instance.sale_date,
                reference_type='store_sale',
                reference_id=instance.id,
                reason='Store sale on credit',
                balance_after=Decimal('0.00'),
                created_by=instance.created_by,
                updated_by=instance.updated_by,
            )


@receiver(post_save, sender=SaleItem)
def sale_item_post_save(sender, instance, created, **kwargs):
    if created and instance.sale:
        _adjust_stock_from_sale(instance.sale)


@receiver(post_save, sender=PrintJob)
def print_job_post_save(sender, instance, created, **kwargs):
    expected_total = Decimal(instance.pages) * Decimal(instance.copies) * Decimal(instance.per_page_cost)
    if instance.total_amount != expected_total:
        instance.total_amount = expected_total
        instance.save(update_fields=['total_amount', 'updated_at'])

    print(f"[Store] Print job '{instance.job_name}' for {instance.teacher} is {instance.status}.")


@receiver(post_save, sender=SupplierQuotation)
def quotation_post_save(sender, instance, created, **kwargs):
    if instance.is_selected:
        SupplierQuotation.objects.filter(requirement=instance.requirement).exclude(pk=instance.pk).update(is_selected=False, status='rejected')
        instance.requirement.status = 'quotations_received'
        instance.requirement.save(update_fields=['status', 'updated_at'])


@receiver(post_save, sender=PurchaseOrder)
def purchase_order_post_save(sender, instance, created, **kwargs):
    if created and instance.requirement:
        instance.requirement.status = 'po_created'
        instance.requirement.save(update_fields=['status', 'updated_at'])


@receiver(post_save, sender=GoodsReceiptNote)
def goods_receipt_post_save(sender, instance, created, **kwargs):
    if instance.status == 'posted_to_inventory':
        for grn_item in instance.items.all():
            try:
                po_item = grn_item.po_item
                po_item.received_quantity = (po_item.received_quantity or 0) + (grn_item.accepted_quantity or 0)
                po_item.save(update_fields=['received_quantity', 'pending_quantity', 'updated_at'])
            except Exception as exc:
                print(f"[Store] Failed to update PO item from GRN {instance.id}: {exc}")


@receiver(post_save, sender=StoreIndent)
def store_indent_post_save(sender, instance, created, **kwargs):
    if instance.status == 'submitted' and not instance.approval_request_id:
        college_id = getattr(instance.college, 'id', None)
        requester = instance.requesting_store_manager
        if college_id and requester:
            try:
                approval = ApprovalRequest.objects.create(
                    college_id=college_id,
                    requester=requester,
                    request_type='store_indent',
                    title=f"Store indent {instance.indent_number}",
                    description=instance.justification,
                    content_type=ContentType.objects.get_for_model(StoreIndent),
                    object_id=instance.id,
                    priority=instance.priority,
                )
                instance.approval_request = approval
                instance.status = 'pending_approval'
                instance.save(update_fields=['approval_request', 'status', 'updated_at'])
            except Exception as exc:
                print(f"[Store] Could not create approval for indent {instance.id}: {exc}")


@receiver(post_save, sender=MaterialIssueNote)
def material_issue_post_save(sender, instance, created, **kwargs):
    if instance.status == 'dispatched':
        for issue_item in instance.items.all():
            try:
                inventory, _ = CentralStoreInventory.objects.get_or_create(
                    central_store=instance.central_store,
                    item=issue_item.item,
                )
                inventory.update_stock(-issue_item.issued_quantity, 'issue', reference=issue_item, performed_by=instance.issued_by)
                issue_item.indent_item.update_issued_quantity(issue_item.issued_quantity)
            except Exception as exc:
                print(f"[Store] Failed to reduce inventory for issue item {issue_item.id}: {exc}")

    if instance.status == 'received':
        indent = instance.indent
        indent.check_fulfillment()


@receiver(post_save, sender=InventoryTransaction)
def inventory_transaction_post_save(sender, instance, created, **kwargs):
    if created:
        print(f"[Store] Inventory transaction {instance.transaction_number} recorded")
