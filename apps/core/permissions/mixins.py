"""
Mixins for scope-based queryset filtering.
"""
from apps.core.permissions.scope_resolver import apply_scope_filter
from apps.core.utils import get_current_college_id


class ScopedQuerysetMixin:
    """
    Mixin to apply scope-based filtering to querysets.

    ViewSet must define:
    - resource_name: str
    """

    def get_queryset(self):
        # Get base queryset from parent
        queryset = super().get_queryset()

        # Superadmin gets unfiltered queryset
        if getattr(self.request.user, 'is_superadmin', False):
            # Bypass college scoping
            model = queryset.model
            if hasattr(model, 'objects') and hasattr(model.objects, 'all_colleges'):
                return model.objects.all_colleges()
            return queryset

        # Get resource name
        resource = getattr(self, 'resource_name', None)
        if not resource:
            # If no resource_name, return queryset as-is
            return queryset

        # Get college
        college = None
        college_id = get_current_college_id()
        if college_id and college_id != 'all':
            from apps.core.models import College
            try:
                college = College.objects.filter(id=college_id).first()
            except Exception:
                pass

        # Apply scope filtering
        return apply_scope_filter(self.request.user, resource, queryset, college)
