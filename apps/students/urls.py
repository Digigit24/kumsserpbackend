"""
URL configuration for Students app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StudentCategoryViewSet,
    StudentGroupViewSet,
    StudentViewSet,
    GuardianViewSet,
    StudentGuardianViewSet,
    StudentAddressViewSet,
    StudentDocumentViewSet,
    StudentMedicalRecordViewSet,
    PreviousAcademicRecordViewSet,
    StudentPromotionViewSet,
    CertificateViewSet,
    StudentIDCardViewSet,
)

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'categories', StudentCategoryViewSet, basename='studentcategory')
router.register(r'groups', StudentGroupViewSet, basename='studentgroup')
router.register(r'students', StudentViewSet, basename='student')
router.register(r'guardians', GuardianViewSet, basename='guardian')
router.register(r'student-guardians', StudentGuardianViewSet, basename='studentguardian')
router.register(r'addresses', StudentAddressViewSet, basename='studentaddress')
router.register(r'documents', StudentDocumentViewSet, basename='studentdocument')
router.register(r'medical-records', StudentMedicalRecordViewSet, basename='studentmedicalrecord')
router.register(r'previous-records', PreviousAcademicRecordViewSet, basename='previousacademicrecord')
router.register(r'promotions', StudentPromotionViewSet, basename='studentpromotion')
router.register(r'certificates', CertificateViewSet, basename='certificate')
router.register(r'id-cards', StudentIDCardViewSet, basename='studentidcard')

urlpatterns = [
    path('', include(router.urls)),
]
