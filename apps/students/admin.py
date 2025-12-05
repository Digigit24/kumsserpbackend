from django.contrib import admin
from .models import (
    StudentCategory, StudentGroup, Student, Guardian, StudentGuardian,
    StudentAddress, StudentDocument, StudentMedicalRecord, PreviousAcademicRecord,
    StudentPromotion, Certificate, StudentIDCard
)


class BaseModelAdmin(admin.ModelAdmin):
    """Base admin that bypasses college scoping for superadmin."""
    
    def get_queryset(self, request):
        """Show all records regardless of college context."""
        qs = self.model.objects
        if hasattr(qs, 'all_colleges'):
            return qs.all_colleges()
        return super().get_queryset(request)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Override to show all FK options regardless of college context."""
        if db_field.remote_field and hasattr(db_field.remote_field.model.objects, 'all_colleges'):
            kwargs['queryset'] = db_field.remote_field.model.objects.all_colleges()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(StudentCategory)
class StudentCategoryAdmin(BaseModelAdmin):
    list_display = ('name', 'code', 'college', 'is_active')
    list_filter = ('college', 'is_active')
    search_fields = ('name', 'code')

@admin.register(StudentGroup)
class StudentGroupAdmin(BaseModelAdmin):
    list_display = ('name', 'college', 'is_active')
    list_filter = ('college', 'is_active')
    search_fields = ('name',)

@admin.register(Student)
class StudentAdmin(BaseModelAdmin):
    list_display = ('admission_number', 'get_full_name', 'email', 'program', 'current_class', 'is_active')
    list_filter = ('college', 'program', 'current_class', 'is_active', 'is_alumni')
    search_fields = ('first_name', 'last_name', 'admission_number', 'registration_number', 'email')
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'

@admin.register(Guardian)
class GuardianAdmin(BaseModelAdmin):
    list_display = ('get_full_name', 'relation', 'phone', 'email')
    list_filter = ('relation',)
    search_fields = ('first_name', 'last_name', 'phone', 'email')
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'

@admin.register(StudentGuardian)
class StudentGuardianAdmin(BaseModelAdmin):
    list_display = ('student', 'guardian', 'is_primary', 'is_emergency_contact')
    list_filter = ('is_primary', 'is_emergency_contact')
    search_fields = ('student__first_name', 'student__last_name', 'guardian__first_name', 'guardian__last_name')

@admin.register(StudentAddress)
class StudentAddressAdmin(admin.ModelAdmin):
    list_display = ('student', 'address_type', 'city', 'state')
    list_filter = ('address_type', 'state')
    search_fields = ('student__first_name', 'student__last_name', 'city')

@admin.register(StudentDocument)
class StudentDocumentAdmin(admin.ModelAdmin):
    list_display = ('student', 'document_type', 'document_name', 'uploaded_date', 'is_verified')
    list_filter = ('document_type', 'is_verified', 'is_active')
    search_fields = ('student__first_name', 'student__last_name', 'document_name')

@admin.register(StudentMedicalRecord)
class StudentMedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'blood_group', 'last_checkup_date', 'is_active')
    list_filter = ('blood_group', 'is_active')
    search_fields = ('student__first_name', 'student__last_name')

@admin.register(PreviousAcademicRecord)
class PreviousAcademicRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'level', 'institution_name', 'year_of_passing', 'percentage')
    list_filter = ('level', 'year_of_passing', 'is_active')
    search_fields = ('student__first_name', 'student__last_name', 'institution_name')

@admin.register(StudentPromotion)
class StudentPromotionAdmin(admin.ModelAdmin):
    list_display = ('student', 'from_class', 'to_class', 'promotion_date', 'academic_year')
    list_filter = ('academic_year', 'promotion_date', 'is_active')
    search_fields = ('student__first_name', 'student__last_name')

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_number', 'student', 'certificate_type', 'issue_date', 'is_active')
    list_filter = ('certificate_type', 'is_active')
    search_fields = ('certificate_number', 'student__first_name', 'student__last_name')

@admin.register(StudentIDCard)
class StudentIDCardAdmin(admin.ModelAdmin):
    list_display = ('card_number', 'student', 'issue_date', 'valid_until', 'is_active', 'is_reissue')
    list_filter = ('is_active', 'is_reissue')
    search_fields = ('card_number', 'student__first_name', 'student__last_name')
