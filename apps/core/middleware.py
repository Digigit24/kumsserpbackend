"""
Middleware for college identification and request context management.
"""
from django.utils.deprecation import MiddlewareMixin
from .models import College
from .utils import (
    set_current_college_id,
    get_current_college_id,
    clear_current_college_id,
    set_current_request,
    clear_current_request
)


class CollegeMiddleware(MiddlewareMixin):
    """
    Middleware that extracts college ID from X-College-ID (or legacy X-Tenant-ID)
    header and stores it in thread-local storage for the duration of the request.
    """

    header_candidates = ['HTTP_X_COLLEGE_ID', 'HTTP_X_TENANT_ID']

    def process_request(self, request):
        """
        Extract college_id from request header and store in thread-local storage.
        Also store the request object for use in signals and models.
        Supports special value 'all' for superadmin/central manager to access all colleges.
        """
        clear_current_college_id()
        set_current_request(request)
        request.current_college = None

        # Try to find a college header
        college_header = None
        for header in self.header_candidates:
            college_header = request.META.get(header)
            if college_header:
                break

        # If header exists, try to set college context
        if college_header:
            if college_header.lower() == 'all':
                set_current_college_id('all')
            else:
                try:
                    college = (
                        College.objects.all_colleges()
                        .only('id')
                        .get(pk=int(college_header))
                    )
                    set_current_college_id(college.id)
                    request.current_college = college
                except (College.DoesNotExist, TypeError, ValueError):
                    pass

        # Superadmin and Central Managers can bypass college scoping if no header is present
        # but if a header WAS present, we use it even for them.
        user = getattr(request, 'user', None)
        is_global_user = user and user.is_authenticated and (
            getattr(user, 'is_superadmin', False) or
            getattr(user, 'is_superuser', False) or
            getattr(user, 'user_type', None) == 'central_manager'
        )
        
        # If no college context set yet, and it's a global user, they see everything
        if is_global_user and not get_current_college_id():
            # In this case we don't set college context - they see everything
            pass

    def process_response(self, request, response):
        """
        Clean up thread-local storage after request is processed.
        """
        clear_current_college_id()
        clear_current_request()
        return response

    def process_exception(self, request, exception):
        """
        Clean up thread-local storage when an exception occurs.
        """
        clear_current_college_id()
        clear_current_request()


# Backward-compatibility alias
TenantMiddleware = CollegeMiddleware
