from django.db.models import Sum, Count, Q, F
from django.db.models.functions import Coalesce
from django.utils import timezone
from decimal import Decimal

from apps.store.models import StoreSale, SaleItem, StoreItem


class StoreStatsService:
    """Service class for store statistics calculations"""

    def __init__(self, college_id, filters=None):
        self.college_id = college_id
        self.filters = filters or {}

    def get_sales_stats(self):
        """Calculate store sales statistics"""
        sales = StoreSale.objects.all_colleges().filter(
            college_id=self.college_id,
            payment_status='PAID'
        )

        if self.filters.get('from_date'):
            sales = sales.filter(sale_date__gte=self.filters['from_date'])
        if self.filters.get('to_date'):
            sales = sales.filter(sale_date__lte=self.filters['to_date'])

        total_sales = sales.count()

        total_revenue = sales.aggregate(
            total=Coalesce(Sum('total_amount'), Decimal('0'))
        )['total']

        # Total items sold
        sale_items = SaleItem.objects.all_colleges().filter(sale__in=sales)
        total_items_sold = sale_items.aggregate(
            total=Coalesce(Sum('quantity'), 0)
        )['total']

        average_sale_amount = (total_revenue / total_sales) if total_sales > 0 else Decimal('0')

        # Popular items
        popular_items_qs = sale_items.values(
            'item__id',
            'item__name',
            'item__category__name'
        ).annotate(
            quantity_sold=Coalesce(Sum('quantity'), 0),
            revenue=Coalesce(Sum('total_price'), Decimal('0'))
        ).order_by('-quantity_sold')[:10]

        popular_items = []
        for item in popular_items_qs:
            popular_items.append({
                'item_id': item['item__id'],
                'item_name': item['item__name'],
                'category': item['item__category__name'] or 'Uncategorized',
                'quantity_sold': item['quantity_sold'],
                'revenue': item['revenue']
            })

        # Payment method breakdown
        cash_sales = sales.filter(payment_method='CASH').aggregate(
            total=Coalesce(Sum('total_amount'), Decimal('0'))
        )['total']

        online_sales = sales.filter(payment_method__in=['UPI', 'CARD', 'ONLINE']).aggregate(
            total=Coalesce(Sum('total_amount'), Decimal('0'))
        )['total']

        return {
            'total_sales': total_sales,
            'total_revenue': total_revenue,
            'total_items_sold': total_items_sold,
            'average_sale_amount': average_sale_amount,
            'popular_items': popular_items,
            'cash_sales': cash_sales,
            'online_sales': online_sales,
        }

    def get_inventory_stats(self):
        """Calculate inventory statistics"""
        items = StoreItem.objects.all_colleges().filter(college_id=self.college_id, is_active=True)

        total_items = items.count()
        low_stock_items = items.filter(stock_quantity__lte=F('min_stock_level')).count()
        out_of_stock_items = items.filter(stock_quantity=0).count()

        total_inventory_value = items.aggregate(
            total=Coalesce(Sum(F('stock_quantity') * F('price'), output_field=F('price').field), Decimal('0'))
        )['total']

        return {
            'total_items': total_items,
            'low_stock_items': low_stock_items,
            'out_of_stock_items': out_of_stock_items,
            'total_inventory_value': total_inventory_value,
        }
