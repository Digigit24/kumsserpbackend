"""
Middleware for college identification and request context management.
"""
from django.utils.deprecation import MiddlewareMixin
from .models import College
from .utils import (
    set_current_college_id,
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
        Superadmins bypass college scoping entirely.
        """
        clear_current_college_id()

        # Superadmin and Central Managers bypass college scoping
        user = getattr(request, 'user', None)
        is_global_user = user and user.is_authenticated and (
            getattr(user, 'is_superadmin', False) or
            getattr(user, 'is_superuser', False) or
            getattr(user, 'user_type', None) == 'central_manager'
        )
        if is_global_user:
            # Don't set college context - they see everything
            set_current_request(request)
            request.current_college = None
            return

        college_header = None
        for header in self.header_candidates:
            college_header = request.META.get(header)
            if college_header:
                break

        if college_header:
            # Check for special 'all' value; enforcement happens in view mixins
            if college_header.lower() == 'all':
                set_current_college_id('all')
                request.current_college = None
            else:
                # Normal integer college ID
                college = None
                try:
                    college = (
                        College.objects.all_colleges()
                        .only('id')
                        .get(pk=int(college_header))
                    )
                except (College.DoesNotExist, TypeError, ValueError):
                    college = None

                if college:
                    set_current_college_id(college.id)
                    request.current_college = college

        set_current_request(request)

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
