"""Cache mixins for API ViewSets"""
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache


class CachedListRetrieveMixin:
    """Mixin to add caching to list and retrieve methods"""
    cache_timeout = 60 * 5  # 5 minutes default

    @method_decorator(cache_page(60 * 5))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 5))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class CachedReadOnlyMixin:
    """For ViewSets with frequent updates - shorter cache"""

    @method_decorator(cache_page(60 * 2))  # 2 minutes
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 2))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class CachedStaticMixin:
    """For rarely changing data - longer cache"""

    @method_decorator(cache_page(60 * 15))  # 15 minutes
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 15))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


def invalidate_cache_pattern(pattern):
    """Helper to invalidate cache by pattern"""
    try:
        keys = cache.keys(f'*{pattern}*')
        if keys:
            cache.delete_many(keys)
    except:
        pass  # Fallback if Redis not available
