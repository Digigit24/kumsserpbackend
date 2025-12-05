"""
Custom model managers for college-aware query filtering.
"""
from django.db import models
from .utils import get_current_college_id


class CollegeQuerySet(models.QuerySet):
    """
    QuerySet that enforces college scoping unless explicitly bypassed.
    """

    def _apply_college_filters(self, college_id=None):
        """
        Build and apply college filters based on available context.
        """
        if not college_id:
            return self.none()

        # College model scopes by PK, others by FK
        if self.model._meta.model_name == 'college':
            return self.filter(pk=college_id)

        if any(field.name == 'college' for field in self.model._meta.fields):
            return self.filter(college_id=college_id)

        return self.none()

    def for_current_college(self):
        """
        Scope queryset to the college found in thread-local storage.
        Returns an empty queryset if no college is set to avoid leaking data.
        """
        college_id = get_current_college_id()
        return self._apply_college_filters(college_id=college_id)

    def for_college(self, college_id):
        """
        Explicitly filter by a specific college ID.
        """
        return self._apply_college_filters(college_id=college_id)


class CollegeManager(models.Manager):
    """
    Custom manager that automatically filters queries by current college.
    """

    def get_queryset(self):
        """
        Override get_queryset to automatically filter by college_id.
        Returns all records when college_id is 'all' (superadmin mode).
        Falls back to an empty queryset when college_id is missing.
        """
        base_qs = CollegeQuerySet(self.model, using=self._db)
        if self.model._meta.model_name == 'college':
            return base_qs
        
        # Check if college_id is 'all' (superadmin global mode)
        college_id = get_current_college_id()
        if college_id == 'all':
            return base_qs  # Return unfiltered queryset for superadmin
        
        return base_qs.for_current_college()

    def all_colleges(self):
        """
        Bypass college filtering to get records from all colleges.
        Use with caution - only for admin/system operations.
        """
        return CollegeQuerySet(self.model, using=self._db)

    def for_college(self, college_id):
        """
        Explicitly filter by a specific college ID.

        Args:
            college_id (int | str): The college identifier

        Returns:
            QuerySet: Filtered queryset for the specified college
        """
        return CollegeQuerySet(self.model, using=self._db).for_college(college_id)


# Backward-compatibility aliases
TenantQuerySet = CollegeQuerySet
TenantManager = CollegeManager
