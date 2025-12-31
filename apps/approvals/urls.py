# -*- coding: utf-8 -*-
"""
URL routing for approval and notification endpoints.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ApprovalRequestViewSet,
    FeePaymentApprovalView,
    NotificationViewSet,
    BulkNotificationView,
)

app_name = 'approvals'

# Create router and register viewsets
router = DefaultRouter()
router.register(r'requests', ApprovalRequestViewSet, basename='approval-request')
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),

    # Fee payment approval
    path('fee-payment/', FeePaymentApprovalView.as_view(), name='fee-payment-approval'),

    # Bulk notifications
    path('notifications/bulk/', BulkNotificationView.as_view(), name='bulk-notification'),
]
