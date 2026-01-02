"""
Phase 9.12: Reports endpoints for Store app
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Avg, F, Q

from .models import (
    ProcurementRequirement,
    StoreIndent,
    CentralStoreInventory,
    SupplierMaster,
)
from .serializers import StoreIndentListSerializer
from .permissions import IsCentralStoreManager


@api_view(['GET'])
@permission_classes([IsCentralStoreManager])
def procurement_pipeline(request):
    """Phase 9.12: Overview of procurement stages"""
    data = {
        'draft': ProcurementRequirement.objects.filter(status='draft').count(),
        'pending_approval': ProcurementRequirement.objects.filter(status='pending_approval').count(),
        'approved': ProcurementRequirement.objects.filter(status='approved').count(),
        'quotations_received': ProcurementRequirement.objects.filter(status='quotations_received').count(),
        'po_created': ProcurementRequirement.objects.filter(status='po_created').count(),
        'fulfilled': ProcurementRequirement.objects.filter(status='fulfilled').count(),
        'cancelled': ProcurementRequirement.objects.filter(status='cancelled').count(),
    }
    return Response(data)


@api_view(['GET'])
@permission_classes([IsCentralStoreManager])
def transfer_history(request):
    """Phase 9.12: History of inter-store transfers"""
    indents = StoreIndent.objects.select_related('college', 'central_store').order_by('-indent_date')[:50]
    data = StoreIndentListSerializer(indents, many=True).data
    return Response(data)


@api_view(['GET'])
@permission_classes([IsCentralStoreManager])
def stock_valuation(request):
    """Phase 9.12: Total inventory value"""
    total_value = CentralStoreInventory.objects.aggregate(
        total=Sum(F('quantity_on_hand') * F('unit_cost'))
    )
    return Response({'total_inventory_value': total_value['total'] or 0})


@api_view(['GET'])
@permission_classes([IsCentralStoreManager])
def supplier_performance(request):
    """Phase 9.12: Supplier ratings, delivery times"""
    suppliers = SupplierMaster.objects.annotate(
        total_orders=Count('purchase_orders'),
        avg_rating=Avg('rating')
    ).values('id', 'name', 'supplier_code', 'rating', 'total_orders', 'supplier_type', 'is_verified')
    return Response(list(suppliers))


@api_view(['GET'])
@permission_classes([IsCentralStoreManager])
def indent_fulfillment_rate(request):
    """Phase 9.12: % of indents fulfilled on time"""
    total = StoreIndent.objects.count()
    if total == 0:
        return Response({
            'total_indents': 0,
            'fulfilled_on_time': 0,
            'fulfillment_rate': 0
        })

    # Indents fulfilled
    fulfilled = StoreIndent.objects.filter(status='fulfilled').count()

    # Approximation: Indents with material issues received on/before required date
    fulfilled_on_time = StoreIndent.objects.filter(
        status='fulfilled',
        material_issues__receipt_date__lte=F('required_by_date')
    ).distinct().count()

    rate = (fulfilled_on_time / total * 100) if total > 0 else 0

    return Response({
        'total_indents': total,
        'fulfilled': fulfilled,
        'fulfilled_on_time': fulfilled_on_time,
        'fulfillment_rate': round(rate, 2)
    })
