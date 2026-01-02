"""
URL configuration for Store app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    StoreCategoryViewSet,
    StoreItemViewSet,
    VendorViewSet,
    StockReceiveViewSet,
    StoreSaleViewSet,
    SaleItemViewSet,
    PrintJobViewSet,
    StoreCreditViewSet,
    SupplierMasterViewSet,
    CentralStoreViewSet,
    ProcurementRequirementViewSet,
    SupplierQuotationViewSet,
    PurchaseOrderViewSet,
    GoodsReceiptNoteViewSet,
    InspectionNoteViewSet,
    StoreIndentViewSet,
    MaterialIssueNoteViewSet,
    CentralStoreInventoryViewSet,
    InventoryTransactionViewSet,
)

router = DefaultRouter()
router.register(r'categories', StoreCategoryViewSet, basename='storecategory')
router.register(r'items', StoreItemViewSet, basename='storeitem')
router.register(r'vendors', VendorViewSet, basename='vendor')
router.register(r'stock-receipts', StockReceiveViewSet, basename='stockreceive')
router.register(r'sales', StoreSaleViewSet, basename='storesale')
router.register(r'sale-items', SaleItemViewSet, basename='saleitem')
router.register(r'print-jobs', PrintJobViewSet, basename='printjob')
router.register(r'credits', StoreCreditViewSet, basename='storecredit')

router.register(r'suppliers', SupplierMasterViewSet, basename='supplier')
router.register(r'central-stores', CentralStoreViewSet, basename='centralstore')
router.register(r'procurement/requirements', ProcurementRequirementViewSet, basename='procurement-requirement')
router.register(r'procurement/quotations', SupplierQuotationViewSet, basename='procurement-quotation')
router.register(r'procurement/purchase-orders', PurchaseOrderViewSet, basename='purchase-order')
router.register(r'procurement/goods-receipts', GoodsReceiptNoteViewSet, basename='goods-receipt')
router.register(r'procurement/inspections', InspectionNoteViewSet, basename='inspection-note')
router.register(r'indents', StoreIndentViewSet, basename='store-indent')
router.register(r'material-issues', MaterialIssueNoteViewSet, basename='material-issue')
router.register(r'central-inventory', CentralStoreInventoryViewSet, basename='central-inventory')
router.register(r'inventory-transactions', InventoryTransactionViewSet, basename='inventory-transaction')

urlpatterns = [
    path('', include(router.urls)),
]
