"""
URL configuration for Fees app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FeeGroupViewSet,
    FeeTypeViewSet,
    FeeMasterViewSet,
    FeeStructureViewSet,
    FeeDiscountViewSet,
    StudentFeeDiscountViewSet,
    FeeCollectionViewSet,
    FeeReceiptViewSet,
    FeeInstallmentViewSet,
    FeeFineViewSet,
    FeeRefundViewSet,
    BankPaymentViewSet,
    OnlinePaymentViewSet,
    FeeReminderViewSet,
)

router = DefaultRouter()
router.register(r'fee-groups', FeeGroupViewSet, basename='feegroup')
router.register(r'fee-types', FeeTypeViewSet, basename='feetype')
router.register(r'fee-masters', FeeMasterViewSet, basename='feemaster')
router.register(r'fee-structures', FeeStructureViewSet, basename='feestructure')
router.register(r'fee-discounts', FeeDiscountViewSet, basename='feediscount')
router.register(r'student-fee-discounts', StudentFeeDiscountViewSet, basename='studentfeediscount')
router.register(r'fee-collections', FeeCollectionViewSet, basename='feecollection')
router.register(r'fee-receipts', FeeReceiptViewSet, basename='feereceipt')
router.register(r'fee-installments', FeeInstallmentViewSet, basename='feeinstallment')
router.register(r'fee-fines', FeeFineViewSet, basename='feefine')
router.register(r'fee-refunds', FeeRefundViewSet, basename='feerefund')
router.register(r'bank-payments', BankPaymentViewSet, basename='bankpayment')
router.register(r'online-payments', OnlinePaymentViewSet, basename='onlinepayment')
router.register(r'fee-reminders', FeeReminderViewSet, basename='feereminder')

urlpatterns = [
    path('', include(router.urls)),
]
