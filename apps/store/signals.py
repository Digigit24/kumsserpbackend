"""
Signals for Store app.
Handles stock adjustments, credit tracking, and print job totals.
"""
from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import StockReceive, StoreItem, StoreSale, SaleItem, StoreCredit, PrintJob


def _adjust_stock_from_sale(sale):
    """
    Reduce stock based on sale items. Safe for missing related items.
    """
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
        # Placeholder: trigger low-stock alert if needed
        if item.stock_quantity <= item.min_stock_level:
            print(f"[Store] Stock low for {item.name}: {item.stock_quantity}")


@receiver(post_save, sender=StoreSale)
def store_sale_post_save(sender, instance, created, **kwargs):
    if not created:
        return

    # Update stock from existing sale items
    _adjust_stock_from_sale(instance)

    # Create a basic credit entry for unpaid sales
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
    """
    Adjust stock when sale items are added after sale creation.
    """
    if created and instance.sale:
        _adjust_stock_from_sale(instance.sale)


@receiver(post_save, sender=PrintJob)
def print_job_post_save(sender, instance, created, **kwargs):
    """
    Compute total cost and send placeholder notification.
    """
    expected_total = Decimal(instance.pages) * Decimal(instance.copies) * Decimal(instance.per_page_cost)
    if instance.total_amount != expected_total:
        instance.total_amount = expected_total
        instance.save(update_fields=['total_amount', 'updated_at'])

    print(f"[Store] Print job '{instance.job_name}' for {instance.teacher} is {instance.status}.")
