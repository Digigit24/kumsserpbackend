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

    def _invalidate_cache(self):
        """Clear cache after mutations - use selective invalidation"""
        try:
            # Instead of clearing ALL cache, only clear view-specific cache
            # This prevents data loading issues and hard refresh requirements
            from django.core.cache.utils import make_template_fragment_key
            from .utils import get_current_college_id

            # Clear cache for this viewset's endpoints
            view_name = self.__class__.__name__.lower()
            college_id = get_current_college_id()

            # Build patterns to clear
            patterns = [
                f'views.decorators.cache.cache_page.*.{view_name}.*',
                f'*{view_name}*list*',
                f'*{view_name}*retrieve*',
            ]

            if college_id:
                patterns.extend([
                    f'*{college_id}*{view_name}*',
                    f'*college_{college_id}*',
                ])

            # Clear matching keys
            for pattern in patterns:
                try:
                    keys = cache.keys(pattern)
                    if keys:
                        cache.delete_many(keys)
                except:
                    pass

        except Exception as e:
            # Fallback: don't clear cache if there's an error
            # This prevents 500 errors from cache failures
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Cache invalidation failed: {e}")

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        self._invalidate_cache()
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        self._invalidate_cache()
        return response

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        self._invalidate_cache()
        return response

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        self._invalidate_cache()
        return response


class CachedReadOnlyMixin:
    """For ViewSets with frequent updates - shorter cache"""

    @method_decorator(cache_page(60 * 2))  # 2 minutes
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 2))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def _invalidate_cache(self):
        """Clear cache after mutations - use selective invalidation"""
        try:
            # Instead of clearing ALL cache, only clear view-specific cache
            # This prevents data loading issues and hard refresh requirements
            from django.core.cache.utils import make_template_fragment_key
            from .utils import get_current_college_id

            # Clear cache for this viewset's endpoints
            view_name = self.__class__.__name__.lower()
            college_id = get_current_college_id()

            # Build patterns to clear
            patterns = [
                f'views.decorators.cache.cache_page.*.{view_name}.*',
                f'*{view_name}*list*',
                f'*{view_name}*retrieve*',
            ]

            if college_id:
                patterns.extend([
                    f'*{college_id}*{view_name}*',
                    f'*college_{college_id}*',
                ])

            # Clear matching keys
            for pattern in patterns:
                try:
                    keys = cache.keys(pattern)
                    if keys:
                        cache.delete_many(keys)
                except:
                    pass

        except Exception as e:
            # Fallback: don't clear cache if there's an error
            # This prevents 500 errors from cache failures
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Cache invalidation failed: {e}")

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        self._invalidate_cache()
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        self._invalidate_cache()
        return response

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        self._invalidate_cache()
        return response

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        self._invalidate_cache()
        return response


class CachedStaticMixin:
    """For rarely changing data - longer cache"""

    @method_decorator(cache_page(60 * 15))  # 15 minutes
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 15))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def _invalidate_cache(self):
        """Clear cache after mutations - use selective invalidation"""
        try:
            # Instead of clearing ALL cache, only clear view-specific cache
            # This prevents data loading issues and hard refresh requirements
            from django.core.cache.utils import make_template_fragment_key
            from .utils import get_current_college_id

            # Clear cache for this viewset's endpoints
            view_name = self.__class__.__name__.lower()
            college_id = get_current_college_id()

            # Build patterns to clear
            patterns = [
                f'views.decorators.cache.cache_page.*.{view_name}.*',
                f'*{view_name}*list*',
                f'*{view_name}*retrieve*',
            ]

            if college_id:
                patterns.extend([
                    f'*{college_id}*{view_name}*',
                    f'*college_{college_id}*',
                ])

            # Clear matching keys
            for pattern in patterns:
                try:
                    keys = cache.keys(pattern)
                    if keys:
                        cache.delete_many(keys)
                except:
                    pass

        except Exception as e:
            # Fallback: don't clear cache if there's an error
            # This prevents 500 errors from cache failures
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Cache invalidation failed: {e}")

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        self._invalidate_cache()
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        self._invalidate_cache()
        return response

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        self._invalidate_cache()
        return response

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        self._invalidate_cache()
        return response


def invalidate_cache_pattern(pattern):
    """Helper to invalidate cache by pattern"""
    try:
        keys = cache.keys(f'*{pattern}*')
        if keys:
            cache.delete_many(keys)
    except:
        pass  # Fallback if Redis not available
