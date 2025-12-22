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

urlpatterns = [
    path('', include(router.urls)),
]
