"""
Signal handlers for accounts app.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from .models import User, UserProfile, UserRole
from apps.core.models import TeamMembership
from apps.core.permissions.registry import PERMISSION_REGISTRY


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create a UserProfile when a User is created.
    Only creates profile if the user has a college assigned.
    """
    if created and instance.college_id:
        UserProfile.objects.get_or_create(
            user=instance,
            defaults={'college': instance.college}
        )
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create a UserProfile when a User is created.
    Only creates profile if the user has a college assigned.
    """
    if created and instance.college_id:
        # Check if profile already exists
        if not hasattr(instance, 'profile'):
            UserProfile.objects.create(
                user=instance,
                college=instance.college
            )


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save the UserProfile when User is saved (if profile exists).
    """
    if hasattr(instance, 'profile') and instance.profile:
        # Update college if it changed
        if instance.college_id and instance.profile.college_id != instance.college_id:
            instance.profile.college = instance.college
            instance.profile.save()


# ---------------------------------------------------------------------------
# TEAM MEMBERSHIP AUTO-LINKING VIA ROLE HIERARCHY
# ---------------------------------------------------------------------------


def _resource_keys():
    return list(PERMISSION_REGISTRY.keys())


def _create_memberships(college_id, leader_ids, member_ids):
    resources = _resource_keys()
    for leader_id in leader_ids:
        for member_id in member_ids:
            if leader_id == member_id:
                continue
            for resource in resources:
                TeamMembership.objects.get_or_create(
                    college_id=college_id,
                    leader_id=leader_id,
                    member_id=member_id,
                    relationship_type='hierarchy',
                    resource=resource,
                    defaults={
                        'is_active': True,
                    }
                )


def _delete_memberships(college_id, leader_ids, member_ids):
    resources = _resource_keys()
    if not leader_ids or not member_ids:
        return
    TeamMembership.objects.filter(
        college_id=college_id,
        leader_id__in=leader_ids,
        member_id__in=member_ids,
        resource__in=resources,
        relationship_type='hierarchy'
    ).delete()


@receiver(post_save, sender=UserRole)
def update_team_membership_on_role_assignment(sender, instance, created, **kwargs):
    """
    Auto-create or cleanup TeamMembership based on role hierarchy.
    - On create: link ancestors as leaders and descendants as members.
    - On deactivate: remove hierarchy memberships for this user.
    """
    if not instance.college_id:
        return

    role = instance.role
    if not role:
        return

    # Cleanup on deactivation
    if not instance.is_active:
        ancestor_roles = role.get_ancestors(include_self=False)
        descendant_roles = role.get_descendants(include_self=False)
        ancestor_user_ids = list(UserRole.objects.filter(
            college_id=instance.college_id,
            role__in=ancestor_roles,
            is_active=True
        ).values_list('user_id', flat=True))
        descendant_user_ids = list(UserRole.objects.filter(
            college_id=instance.college_id,
            role__in=descendant_roles,
            is_active=True
        ).values_list('user_id', flat=True))
        _delete_memberships(instance.college_id, ancestor_user_ids, [instance.user_id])
        _delete_memberships(instance.college_id, [instance.user_id], descendant_user_ids)
        return

    if not created:
        return

    ancestor_roles = role.get_ancestors(include_self=False)
    descendant_roles = role.get_descendants(include_self=False)

    ancestor_user_ids = list(UserRole.objects.filter(
        college_id=instance.college_id,
        role__in=ancestor_roles,
        is_active=True
    ).values_list('user_id', flat=True))

    descendant_user_ids = list(UserRole.objects.filter(
        college_id=instance.college_id,
        role__in=descendant_roles,
        is_active=True
    ).values_list('user_id', flat=True))

    with transaction.atomic():
        # Ancestors lead this new user
        _create_memberships(instance.college_id, ancestor_user_ids, [instance.user_id])
        # This new user leads descendants
        _create_memberships(instance.college_id, [instance.user_id], descendant_user_ids)


@receiver(post_delete, sender=UserRole)
def cleanup_team_membership_on_role_removal(sender, instance, **kwargs):
    """Remove hierarchy memberships when a role assignment is deleted."""
    if not instance.college_id:
        return
    role = instance.role
    if not role:
        return
    ancestor_roles = role.get_ancestors(include_self=False)
    descendant_roles = role.get_descendants(include_self=False)
    ancestor_user_ids = list(UserRole.objects.filter(
        college_id=instance.college_id,
        role__in=ancestor_roles,
        is_active=True
    ).values_list('user_id', flat=True))
    descendant_user_ids = list(UserRole.objects.filter(
        college_id=instance.college_id,
        role__in=descendant_roles,
        is_active=True
    ).values_list('user_id', flat=True))
    _delete_memberships(instance.college_id, ancestor_user_ids, [instance.user_id])
    _delete_memberships(instance.college_id, [instance.user_id], descendant_user_ids)
