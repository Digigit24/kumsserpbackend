"""Cache mixins for API ViewSets - DISABLED (using DummyCache)"""


class CachedListRetrieveMixin:
    """Mixin - caching disabled"""
    pass


class CachedReadOnlyMixin:
    """Mixin - caching disabled"""
    pass


class CachedStaticMixin:
    """Mixin - caching disabled"""
    pass


def invalidate_cache_pattern(pattern):
    """Helper - caching disabled"""
    pass
