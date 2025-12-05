"""
Thread-local utilities for college-scoped request context management.
"""
import threading

# Thread-local storage instance
_thread_locals = threading.local()


def set_current_college_id(college_id):
    """
    Store the current college ID in thread-local storage.

    Args:
        college_id (int | str): The college identifier to store
    """
    _thread_locals.college_id = college_id


def get_current_college_id():
    """
    Retrieve the current college ID from thread-local storage.

    Returns:
        int | str | None: The current college ID if set, None otherwise
    """
    return getattr(_thread_locals, 'college_id', None)


def clear_current_college_id():
    """
    Clear the current college ID from thread-local storage.
    """
    if hasattr(_thread_locals, 'college_id'):
        delattr(_thread_locals, 'college_id')


# Backward-compatibility aliases (deprecated)
set_current_tenant_id = set_current_college_id
get_current_tenant_id = get_current_college_id
clear_current_tenant_id = clear_current_college_id


def set_current_request(request):
    """
    Store the current request object in thread-local storage.

    Args:
        request: The Django request object to store
    """
    _thread_locals.request = request


def get_current_request():
    """
    Retrieve the current request object from thread-local storage.

    Returns:
        HttpRequest or None: The current request if set, None otherwise
    """
    return getattr(_thread_locals, 'request', None)


def clear_current_request():
    """
    Clear the current request object from thread-local storage.
    """
    if hasattr(_thread_locals, 'request'):
        delattr(_thread_locals, 'request')


def get_client_ip(request):
    """
    Extract client IP address from request, handling load balancer headers.

    Args:
        request: Django HttpRequest object

    Returns:
        str or None: Client IP address
    """
    if not request:
        return None

    # Check for X-Forwarded-For header (common with load balancers/proxies)
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # X-Forwarded-For can contain multiple IPs, take the first one (original client)
        ip = x_forwarded_for.split(',')[0].strip()
        return ip

    # Fallback to REMOTE_ADDR
    return request.META.get('REMOTE_ADDR')
