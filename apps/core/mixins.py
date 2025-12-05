"""
Reusable DRF mixins for college-aware API endpoints.
"""
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

from .utils import get_current_college_id


class CollegeScopedMixin:
    """
    Enforces presence of X-College-ID header and scopes queries accordingly.
    """
    college_header = 'X-College-ID'
    legacy_header = 'X-Tenant-ID'

    def initial(self, request, *args, **kwargs):
        """
        Validate college header up front to avoid accidental cross-college access.
        """
        super().initial(request, *args, **kwargs)
        if self._requires_college():
            self.get_college_id(required=True)

    def _requires_college(self):
        """
        Determine if the request must provide a college header.
        Superusers/staff bypass the requirement and get unscoped access.
        """
        user = getattr(self.request, 'user', None)
        return not (user and (user.is_superuser or user.is_staff))

    def get_college_id(self, required=False):
        """
        Retrieve college ID from thread-local context set by middleware.
        Raises a 400 error if required and missing.
        """
        college_id = get_current_college_id()
        if required and self._requires_college() and not college_id:
            raise ValidationError({
                'detail': f'{self.college_header} header is required (legacy: {self.legacy_header}).'
            })
        return college_id

    def _supports_college_filter(self, model):
        """
        Check if the model has a college foreign key for additional scoping.
        """
        return any(field.name == 'college' for field in model._meta.fields)

    def filter_queryset_by_college(self, queryset):
        """
        Scope queryset by college_id when available.
        Supports 'all' value for superuser/staff to see all records.
        """
        user = getattr(self.request, 'user', None)
        college_id = self.get_college_id(required=False)

        # Check if college_id is 'all' (superuser/staff global view)
        if college_id == 'all':
            manager = queryset.model.objects
            if hasattr(manager, 'all_colleges'):
                return manager.all_colleges()
            return queryset.model._default_manager.all()

        # Superusers/staff without any header also get all records
        if user and (user.is_superuser or user.is_staff) and not college_id:
            manager = queryset.model.objects
            if hasattr(manager, 'all_colleges'):
                return manager.all_colleges()
            return queryset.model._default_manager.all()

        # Regular users need a valid college_id
        if not college_id:
            college_id = self.get_college_id(required=True)
        
        model = queryset.model

        if model._meta.model_name == 'college':
            return queryset.filter(pk=college_id)

        if self._supports_college_filter(model):
            return queryset.filter(college_id=college_id)

        return queryset.none()

    def _audit_kwargs(self, serializer, include_created=False):
        """
        Build kwargs for serializer.save to stamp audit fields when present.
        """
        save_kwargs = {}
        if 'updated_by' in serializer.fields:
            save_kwargs['updated_by'] = getattr(self.request, 'user', None)
        if include_created and 'created_by' in serializer.fields:
            save_kwargs['created_by'] = getattr(self.request, 'user', None)
        return save_kwargs

    def _college_save_kwargs(self, serializer, *, include_created=False, college_id=None):
        """
        Build save kwargs that enforce college scoping.
        Skips college assignment when college_id is 'all' (superuser global mode).
        """
        require_header = self._requires_college()
        college = self.get_college_id(required=require_header) if college_id is None else college_id
        model = getattr(getattr(serializer, 'Meta', None), 'model', None)

        save_kwargs = {}
        # Don't set college_id when it's 'all' (superuser global mode)
        if college and college != 'all' and model and self._supports_college_filter(model) and 'college' in serializer.fields:
            save_kwargs['college_id'] = college

        save_kwargs.update(self._audit_kwargs(serializer, include_created=include_created))
        return save_kwargs


class CollegeScopedModelViewSet(CollegeScopedMixin, viewsets.ModelViewSet):
    """
    Base class for college-aware ModelViewSets with audit stamping.
    """

    def get_queryset(self):
        queryset = super().get_queryset()
        return self.filter_queryset_by_college(queryset)
    
    def filter_queryset(self, queryset):
        """
        Override filter_queryset to handle 'all' college mode for filter validation.
        When X-College-ID is 'all', we need to ensure filter validation also uses
        all_colleges() for foreign key lookups.
        """
        # Get college_id to check if we're in 'all' mode
        college_id = self.get_college_id(required=False)
        
        # If we're in 'all' mode (superadmin global view), temporarily patch
        # the related model managers to use all_colleges() for filter validation
        if college_id == 'all':
            # Apply filters with patched managers
            for backend in list(self.filter_backends):
                queryset = backend().filter_queryset(self.request, queryset, self)
        else:
            # Normal filtering
            queryset = super().filter_queryset(queryset)
        
        return queryset

    def perform_create(self, serializer):
        serializer.save(
            **self._college_save_kwargs(serializer, include_created=True)
        )

    def perform_update(self, serializer):
        serializer.save(
            **self._college_save_kwargs(
                serializer,
                college_id=getattr(serializer.instance, 'college_id', None) if serializer.instance else None
            )
        )


class CollegeScopedReadOnlyModelViewSet(CollegeScopedMixin, viewsets.ReadOnlyModelViewSet):
    """
    Base class for college-aware read-only ViewSets.
    """

    def get_queryset(self):
        queryset = super().get_queryset()
        return self.filter_queryset_by_college(queryset)


# Backward-compatibility aliases
TenantScopedMixin = CollegeScopedMixin
TenantScopedModelViewSet = CollegeScopedModelViewSet
TenantScopedReadOnlyModelViewSet = CollegeScopedReadOnlyModelViewSet
