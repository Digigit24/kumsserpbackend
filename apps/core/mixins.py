import logging
from rest_framework import viewsets, filters
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .utils import get_current_college_id

logger = logging.getLogger(__name__)


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
            college_id = self.get_college_id(required=True)
            logger.debug(f"Received college_id in header: {college_id}")

    def _requires_college(self):
        """
        Determine if the request must provide a college header.
        Superadmins/central managers bypass the requirement and get unscoped access.
        """
        user = getattr(self.request, 'user', None)
        is_global_user = (
            getattr(user, 'is_superadmin', False) or
            getattr(user, 'is_superuser', False) or
            getattr(user, 'user_type', None) == 'central_manager'
        )
        # If user is tied to a single college, header isn't required
        if user and not is_global_user and getattr(user, 'college_id', None):
            return False
        return not (user and is_global_user)

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
        Supports 'all' value for superadmin/central manager to see all records.
        """
        user = getattr(self.request, 'user', None)
        college_id = self.get_college_id(required=False)

        # Log the college_id being used
        logger.debug(f"Filtering by college_id: {college_id}")

        # Global users (superadmins, central managers) without any header also get all records
        is_global_user = (
            getattr(user, 'is_superadmin', False) or
            getattr(user, 'is_superuser', False) or
            getattr(user, 'user_type', None) == 'central_manager'
        )

        # Non-global users are always scoped to their own college when available
        if user and not is_global_user and getattr(user, 'college_id', None):
            college_id = user.college_id

        # Check if college_id is 'all' (superadmin/central manager global view)
        if college_id == 'all':
            if not (user and is_global_user):
                raise ValidationError({
                    'detail': f"{self.college_header}: 'all' is allowed only for superadmin or central manager."
                })
            logger.debug("Using 'all' mode for superadmin/central manager")
            manager = queryset.model.objects
            if hasattr(manager, 'all_colleges'):
                return manager.all_colleges()
            return queryset.model._default_manager.all()

        if user and is_global_user and not college_id:
            logger.debug("Superadmin/central manager detected, no college_id passed")
            manager = queryset.model.objects
            if hasattr(manager, 'all_colleges'):
                return manager.all_colleges()
            return queryset.model._default_manager.all()

        # Regular users need a valid college_id
        if not college_id:
            logger.debug("Missing college_id, requiring it")
            college_id = self.get_college_id(required=True)

        model = queryset.model
        logger.debug(f"Filtering for specific college_id: {college_id}")

        if model._meta.model_name == 'college':
            logger.debug(f"Filtering college model with college_id={college_id}")
            return queryset.filter(pk=college_id)

        if self._supports_college_filter(model):
            logger.debug(f"Filtering model with college_id={college_id}")
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
        # Set college_id for models that support it, regardless of whether it's in serializer fields
        # This ensures the college_id is ALWAYS set from the request header
        if college and college != 'all' and model and self._supports_college_filter(model):
            save_kwargs['college_id'] = college

        save_kwargs.update(self._audit_kwargs(serializer, include_created=include_created))
        return save_kwargs

    def get_serializer(self, *args, **kwargs):
        """
        Overwrite get_serializer to dynamically handle college field requirements.
        Sets 'college' as optional and injects it from context if missing.
        """
        # 1. Determine the college ID from context
        context_college_id = self.get_college_id(required=False)
        
        # 2. Inject college ID into data for creation/update if missing
        if self.request.method in ['POST', 'PUT', 'PATCH'] and 'data' in kwargs:
            data = kwargs.get('data')
            if data is not None:
                # If 'all' is provided, we need a specific college for creation.
                # For superadmins/central managers, we fallback to the first college if unspecified.
                target_id = context_college_id
                if target_id == 'all':
                    user = getattr(self.request, 'user', None)
                    if user and (user.is_superuser or user.user_type == 'central_manager'):
                        # Fallback to the first active college for global users in 'all' mode
                        from apps.core.models import College
                        first_college = College.objects.all_colleges().filter(is_active=True).first()
                        if first_college:
                            target_id = first_college.id
                
                if target_id and target_id != 'all':
                    # Convert QueryDict to mutable dict if necessary
                    if hasattr(data, 'copy'):
                        if 'college' not in data or not data.get('college'):
                            data = data.copy()
                            data['college'] = str(target_id)
                            kwargs['data'] = data
                    elif isinstance(data, dict):
                        if 'college' not in data or not data.get('college'):
                            data['college'] = target_id
                            kwargs['data'] = data

        # 3. Instantiate the serializer
        serializer = super().get_serializer(*args, **kwargs)
        
        # 4. Make college field optional in the serializer instance to bypass DRF validation
        if hasattr(serializer, 'fields') and 'college' in serializer.fields:
             serializer.fields['college'].required = False
             serializer.fields['college'].allow_null = True
                 
        return serializer


class CollegeScopedModelViewSet(CollegeScopedMixin, viewsets.ModelViewSet):
    """
    Base class for college-aware ModelViewSets with audit stamping.

    Optionally supports permission-based scope filtering when resource_name is defined.
    """

    def get_queryset(self):
        queryset = super().get_queryset()

        # Apply college filtering first
        queryset = self.filter_queryset_by_college(queryset)

        # If resource_name is defined, apply permission-based scope filtering
        if hasattr(self, 'resource_name') and self.resource_name:
            queryset = self._apply_permission_scope_filter(queryset)

        # Apply default is_active filter for list action if not specified
        if self.action == 'list':
            # Check if model has is_active field
            has_is_active = any(field.name == 'is_active' for field in queryset.model._meta.fields)
            if has_is_active:
                is_active_param = self.request.query_params.get('is_active')
                if is_active_param is None:
                    queryset = queryset.filter(is_active=True)

        return queryset

    def _apply_permission_scope_filter(self, queryset):
        """
        Apply scope-based filtering when resource_name is defined.
        """
        from apps.core.permissions.scope_resolver import apply_scope_filter
        from apps.core.utils import get_current_college_id
        from apps.core.models import College

        # Superadmin gets unfiltered queryset
        if getattr(self.request.user, 'is_superadmin', False):
            model = queryset.model
            if hasattr(model, 'objects') and hasattr(model.objects, 'all_colleges'):
                return model.objects.all_colleges()
            return queryset

        # Get college
        college = None
        college_id = get_current_college_id()
        if college_id and college_id != 'all':
            try:
                college = College.objects.filter(id=college_id).first()
            except Exception:
                pass

        # Apply scope filtering
        return apply_scope_filter(self.request.user, self.resource_name, queryset, college)
    
    def filter_queryset(self, queryset):
        """
        Override filter_queryset to handle 'all' college mode for filter validation.
        When X-College-ID is 'all', we need to ensure filter validation also uses
        all_colleges() for foreign key lookups.
        """
        # Get college_id to check if we're in 'all' mode
        college_id = self.get_college_id(required=False)
        
        # Log the college_id being used
        logger.debug(f"Filter query with college_id: {college_id}")
        
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
        """Create with proper error handling"""
        try:
            serializer.save(
                **self._college_save_kwargs(serializer, include_created=True)
            )
        except Exception as e:
            logger.error(f"Error creating {serializer.Meta.model.__name__}: {str(e)}")
            raise

    def perform_update(self, serializer):
        """Update with proper error handling"""
        try:
            serializer.save(
                **self._college_save_kwargs(
                    serializer,
                    college_id=getattr(serializer.instance, 'college_id', None) if serializer.instance else None
                )
            )
        except Exception as e:
            logger.error(f"Error updating {serializer.Meta.model.__name__}: {str(e)}")
            raise


class CollegeScopedReadOnlyModelViewSet(CollegeScopedMixin, viewsets.ReadOnlyModelViewSet):
    """
    Base class for college-aware read-only ViewSets.

    Optionally supports permission-based scope filtering when resource_name is defined.
    """

    def get_queryset(self):
        queryset = super().get_queryset()

        # Apply college filtering first
        queryset = self.filter_queryset_by_college(queryset)

        # If resource_name is defined, apply permission-based scope filtering
        if hasattr(self, 'resource_name') and self.resource_name:
            queryset = self._apply_permission_scope_filter(queryset)

        # Apply default is_active filter for list action if not specified
        if self.action == 'list':
            # Check if model has is_active field
            has_is_active = any(field.name == 'is_active' for field in queryset.model._meta.fields)
            if has_is_active:
                is_active_param = self.request.query_params.get('is_active')
                if is_active_param is None:
                    queryset = queryset.filter(is_active=True)

        return queryset

    def _apply_permission_scope_filter(self, queryset):
        """
        Apply scope-based filtering when resource_name is defined.
        """
        from apps.core.permissions.scope_resolver import apply_scope_filter
        from apps.core.utils import get_current_college_id
        from apps.core.models import College

        # Superadmin gets unfiltered queryset
        if getattr(self.request.user, 'is_superadmin', False):
            model = queryset.model
            if hasattr(model, 'objects') and hasattr(model.objects, 'all_colleges'):
                return model.objects.all_colleges()
            return queryset

        # Get college
        college = None
        college_id = get_current_college_id()
        if college_id and college_id != 'all':
            try:
                college = College.objects.filter(id=college_id).first()
            except Exception:
                pass

        # Apply scope filtering
        return apply_scope_filter(self.request.user, self.resource_name, queryset, college)


class RelatedCollegeScopedModelViewSet(CollegeScopedMixin, viewsets.ModelViewSet):
    """
    Scopes by college via a related lookup path when model lacks direct college FK.
    Example: related_college_lookup = 'student__college_id'
    """
    related_college_lookup = None
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    def get_queryset(self):
        queryset = super().get_queryset()
        college_id = self.get_college_id(required=False)
        user = getattr(self.request, 'user', None)
        is_global_user = (
            getattr(user, 'is_superadmin', False) or
            getattr(user, 'is_superuser', False) or
            getattr(user, 'user_type', None) == 'central_manager'
        )

        if user and not is_global_user and getattr(user, 'college_id', None):
            college_id = user.college_id

        if college_id == 'all' or (user and is_global_user and not college_id):
            return queryset

        if not college_id:
            college_id = self.get_college_id(required=True)

        if not self.related_college_lookup:
            return queryset.none()

        queryset = queryset.filter(**{self.related_college_lookup: college_id})

        # Apply default is_active filter for list action if not specified
        if self.action == 'list':
            # Check if model has is_active field
            has_is_active = any(field.name == 'is_active' for field in queryset.model._meta.fields)
            if has_is_active:
                is_active_param = self.request.query_params.get('is_active')
                if is_active_param is None:
                    queryset = queryset.filter(is_active=True)

        return queryset

    def perform_create(self, serializer):
        """Handle audit fields during creation."""
        serializer.save(**self._audit_kwargs(serializer, include_created=True))

    def perform_update(self, serializer):
        """Handle audit fields during update."""
        serializer.save(**self._audit_kwargs(serializer))

