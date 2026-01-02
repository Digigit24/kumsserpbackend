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


@receiver(post_save, sender=ProcurementRequirement)
def procurement_requirement_post_save(sender, instance, created, **kwargs):
    """Phase 11.1: Create approval request when requirement is submitted"""
    if instance.status == 'submitted' and not instance.approval_request_id:
        try:
            # Get college ID from central store manager or use a default
            college_id = None
            if hasattr(instance.central_store.manager, 'college_id'):
                college_id = instance.central_store.manager.college_id
            elif hasattr(instance.central_store.manager, 'college'):
                college_id = instance.central_store.manager.college.id

            # If no college found, try to get the first available college or use a default
            if not college_id:
                from apps.core.models import College
                first_college = College.objects.first()
                college_id = first_college.id if first_college else 1

            requester = instance.created_by if hasattr(instance, 'created_by') and instance.created_by else instance.central_store.manager

            if requester:
                approval = ApprovalRequest.objects.create(
                    college_id=college_id,
                    requester=requester,
                    request_type='procurement_requirement',
                    title=f"Procurement Requirement {instance.requirement_number}",
                    description=instance.justification,
                    content_type=ContentType.objects.get_for_model(ProcurementRequirement),
                    object_id=instance.id,
                    priority=instance.urgency,
                )
                instance.approval_request = approval
                instance.status = 'pending_approval'
                instance.save(update_fields=['approval_request', 'status', 'updated_at'])
                print(f"[Store] Created approval request for procurement requirement {instance.requirement_number}")
        except Exception as exc:
            print(f"[Store] Could not create approval for requirement {instance.id}: {exc}")
            import traceback
            traceback.print_exc()


@receiver(post_save, sender=GoodsReceiptNote)
def goods_receipt_post_save(sender, instance, created, **kwargs):
    """Phase 11.1: GRN signal to create StockReceive, update inventory, create transactions"""
    if instance.status == 'posted_to_inventory':
        # Prevent duplicate processing
        if hasattr(instance, '_inventory_posted') and instance._inventory_posted:
            return

        instance._inventory_posted = True

        for grn_item in instance.items.all():
            try:
                po_item = grn_item.po_item

                # 1. Update PurchaseOrderItem received_quantity
                po_item.received_quantity = (po_item.received_quantity or 0) + (grn_item.accepted_quantity or 0)
                po_item.save(update_fields=['received_quantity', 'pending_quantity', 'updated_at'])

                # 2. Find or create the StoreItem for central store
                # This is simplified - in production, you'd need proper item matching logic
                central_item = None
                if po_item.quotation_item and po_item.quotation_item.requirement_item:
                    req_item = po_item.quotation_item.requirement_item
                    if req_item.category:
                        # Try to find existing item in central store's college
                        central_item = StoreItem.objects.filter(
                            name__icontains=po_item.item_description.split()[0],
                            category=req_item.category,
                            managed_by='central'
                        ).first()

                # If no item found, we need to create one or skip (based on business logic)
                # For now, we'll skip if no matching item found
                if not central_item:
                    print(f"[Store] No central item found for GRN item {grn_item.id}, skipping inventory update")
                    continue

                # 3. Update/Create CentralStoreInventory
                inventory, _ = CentralStoreInventory.objects.get_or_create(
                    central_store=instance.central_store,
                    item=central_item,
                    defaults={'unit_cost': po_item.unit_price}
                )

                # Update stock using the model method (creates transaction automatically)
                inventory.update_stock(
                    grn_item.accepted_quantity,
                    'receipt',
                    reference=grn_item,
                    performed_by=instance.received_by
                )

                # 4. Create StockReceive for tracking (legacy compatibility)
                StockReceive.objects.create(
                    item=central_item,
                    vendor=None,  # Using SupplierMaster now, not Vendor
                    quantity=grn_item.accepted_quantity,
                    unit_price=po_item.unit_price,
                    total_amount=grn_item.accepted_quantity * po_item.unit_price,
                    receive_date=instance.receipt_date,
                    invoice_number=instance.invoice_number,
                    remarks=f'From GRN {instance.grn_number}, PO {instance.purchase_order.po_number}'
                )

                print(f"[Store] Posted GRN item {grn_item.id} to inventory: {grn_item.accepted_quantity} units")

            except Exception as exc:
                print(f"[Store] Failed to post GRN item {grn_item.id} to inventory: {exc}")
                import traceback
                traceback.print_exc()

        # Check PO fulfillment after all items processed
        try:
            instance.purchase_order.check_fulfillment_status()
        except Exception as exc:
            print(f"[Store] Failed to check PO fulfillment: {exc}")


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
    """Phase 11.1: MaterialIssueNote signal - reduce central stock on dispatch, create college stock on receipt"""

    if instance.status == 'dispatched':
        # Prevent duplicate processing
        if hasattr(instance, '_stock_reduced') and instance._stock_reduced:
            return

        instance._stock_reduced = True

        for issue_item in instance.items.all():
            try:
                inventory, _ = CentralStoreInventory.objects.get_or_create(
                    central_store=instance.central_store,
                    item=issue_item.item,
                )
                inventory.update_stock(
                    -issue_item.issued_quantity,
                    'issue',
                    reference=issue_item,
                    performed_by=instance.issued_by
                )
                issue_item.indent_item.update_issued_quantity(issue_item.issued_quantity)
                print(f"[Store] Reduced central inventory for MIN {instance.min_number}: {issue_item.issued_quantity} units")
            except Exception as exc:
                print(f"[Store] Failed to reduce inventory for issue item {issue_item.id}: {exc}")
                import traceback
                traceback.print_exc()

    if instance.status == 'received':
        # Prevent duplicate processing
        if hasattr(instance, '_college_stock_created') and instance._college_stock_created:
            return

        instance._college_stock_created = True

        for issue_item in instance.items.all():
            try:
                # 1. Find or create college store item
                college_item, created_item = StoreItem.objects.get_or_create(
                    college=instance.receiving_college,
                    code=issue_item.item.code,
                    defaults={
                        'name': issue_item.item.name,
                        'category': issue_item.item.category,
                        'unit': issue_item.unit,
                        'price': issue_item.item.price,
                        'managed_by': 'college',
                        'description': issue_item.item.description,
                        'min_stock_level': issue_item.item.min_stock_level,
                    }
                )

                if created_item:
                    print(f"[Store] Created new college item: {college_item.name} for {instance.receiving_college.name}")

                # 2. Create StockReceive for college
                stock_receive = StockReceive.objects.create(
                    item=college_item,
                    vendor=None,  # From central store, not vendor
                    quantity=issue_item.issued_quantity,
                    unit_price=issue_item.item.price,
                    total_amount=issue_item.issued_quantity * issue_item.item.price,
                    receive_date=instance.receipt_date.date() if instance.receipt_date else instance.issue_date,
                    invoice_number=instance.min_number,
                    remarks=f'From MIN {instance.min_number}, Central Store {instance.central_store.name}'
                )

                # 3. Update college item stock (StockReceive signal will handle this automatically)
                # But we'll do it explicitly to be sure
                college_item.adjust_stock(issue_item.issued_quantity)

                print(f"[Store] Created college stock for MIN {instance.min_number}: {issue_item.issued_quantity} units of {college_item.name}")

            except Exception as exc:
                print(f"[Store] Failed to create college stock for issue item {issue_item.id}: {exc}")
                import traceback
                traceback.print_exc()

        # Check indent fulfillment
        try:
            indent = instance.indent
            indent.check_fulfillment()
        except Exception as exc:
            print(f"[Store] Failed to check indent fulfillment: {exc}")


@receiver(post_save, sender=InventoryTransaction)
def inventory_transaction_post_save(sender, instance, created, **kwargs):
    if created:
        print(f"[Store] Inventory transaction {instance.transaction_number} recorded")
