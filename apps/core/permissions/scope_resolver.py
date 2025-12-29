"""
Scope resolver for KUMSS permission system.
Applies scope-based filtering to querysets.
"""


def get_team_member_ids(user, resource, college=None):
    """
    Returns list of user IDs in the user's team for the given resource.
    Superadmin returns empty list (they bypass filtering).

    Args:
        user: User instance
        resource: Resource name (e.g., 'attendance')
        college: College instance (optional)

    Returns:
        list: List of user IDs
    """
    if getattr(user, 'is_superadmin', False):
        return []  # Superadmin doesn't need team filtering

    from apps.core.models import TeamMembership

    memberships = TeamMembership.objects.filter(
        leader=user,
        resource=resource,
        is_active=True
    )

    if college:
        memberships = memberships.filter(college=college)

    return list(memberships.values_list('member_id', flat=True))


def get_department_user_ids(user, college=None):
    """
    Returns list of user IDs in the user's department.

    Args:
        user: User instance
        college: College instance (optional)

    Returns:
        list: List of user IDs
    """
    if getattr(user, 'is_superadmin', False):
        return []  # Superadmin doesn't need department filtering

    # Get user's department from profile
    if hasattr(user, 'profile') and user.profile and user.profile.department:
        from django.contrib.auth import get_user_model
        User = get_user_model()

        users = User.objects.filter(
            profile__department=user.profile.department,
            is_active=True
        )

        if college:
            users = users.filter(college=college)

        return list(users.values_list('id', flat=True))

    return []


def apply_scope_filter(user, resource, queryset, college=None, scope=None):
    """
    Apply scope-based filtering to queryset.

    Args:
        user: Request user
        resource: Resource name (e.g., 'attendance')
        queryset: Base queryset to filter
        college: College instance (optional)
        scope: Override scope (optional, otherwise fetched from permissions)

    Returns:
        Filtered queryset
    """
    # Superadmin bypasses all filtering
    if getattr(user, 'is_superadmin', False):
        # Return queryset without college scoping
        model = queryset.model
        if hasattr(model, 'objects'):
            if hasattr(model.objects, 'all_colleges'):
                return model.objects.all_colleges()
        return queryset

    # Get scope from permissions if not provided
    if scope is None:
        from apps.core.permissions.manager import get_scope_for_action
        # Assume 'read' action for queryset filtering
        scope = get_scope_for_action(user, resource, 'read', college)

    # Apply scope filtering
    if scope == 'none':
        return queryset.none()

    elif scope == 'mine':
        # Filter to user's own records
        # Try different ownership patterns
        if hasattr(queryset.model, 'created_by'):
            return queryset.filter(created_by=user)
        elif hasattr(queryset.model, 'user'):
            return queryset.filter(user=user)
        elif hasattr(queryset.model, 'student') and hasattr(user, 'student_profile'):
            # For models with student FK
            return queryset.filter(student__user=user)
        elif hasattr(queryset.model, 'teacher') and hasattr(user, 'teacher_profile'):
            # For models with teacher FK
            return queryset.filter(teacher__user=user)
        # Fallback: if user_id field exists
        if hasattr(queryset.model, 'user_id'):
            return queryset.filter(user_id=user.id)
        return queryset

    elif scope == 'team':
        # Filter to team members
        team_ids = get_team_member_ids(user, resource, college)

        # Determine the field to filter on based on model
        model_name = queryset.model.__name__.lower()

        # Attendance models
        if 'attendance' in model_name:
            if hasattr(queryset.model, 'student'):
                return queryset.filter(student__user_id__in=team_ids)
            elif hasattr(queryset.model, 'student_id'):
                return queryset.filter(student_id__in=team_ids)

        # Student-related models
        elif model_name in ['student', 'studentprofile']:
            if hasattr(queryset.model, 'user'):
                return queryset.filter(user_id__in=team_ids)
            elif hasattr(queryset.model, 'user_id'):
                return queryset.filter(user_id__in=team_ids)

        # Fee models
        elif 'fee' in model_name:
            if hasattr(queryset.model, 'student'):
                return queryset.filter(student__user_id__in=team_ids)

        # Exam models
        elif 'exam' in model_name or 'result' in model_name:
            if hasattr(queryset.model, 'student'):
                return queryset.filter(student__user_id__in=team_ids)

        # Library models
        elif 'library' in model_name or 'book' in model_name:
            if hasattr(queryset.model, 'student'):
                return queryset.filter(student__user_id__in=team_ids)
            elif hasattr(queryset.model, 'issued_to'):
                return queryset.filter(issued_to_id__in=team_ids)

        # Generic fallback
        if hasattr(queryset.model, 'user'):
            return queryset.filter(user_id__in=team_ids)

        # If no team members or can't determine field, return empty
        if not team_ids:
            return queryset.none()

        return queryset

    elif scope == 'department':
        # Department-level filtering
        dept_user_ids = get_department_user_ids(user, college)

        if not dept_user_ids:
            return queryset.none()

        # Apply department filtering based on model
        if hasattr(queryset.model, 'department'):
            # Direct department FK
            if hasattr(user, 'profile') and user.profile and user.profile.department:
                return queryset.filter(department=user.profile.department)

        # For user-related models
        elif hasattr(queryset.model, 'user'):
            return queryset.filter(user_id__in=dept_user_ids)

        # For student-related models
        elif hasattr(queryset.model, 'student'):
            return queryset.filter(student__user_id__in=dept_user_ids)

        # For teacher-related models
        elif hasattr(queryset.model, 'teacher'):
            return queryset.filter(teacher__user_id__in=dept_user_ids)

        return queryset

    elif scope == 'all':
        # All records in college (already filtered by CollegeScopedModel)
        return queryset

    return queryset.none()
