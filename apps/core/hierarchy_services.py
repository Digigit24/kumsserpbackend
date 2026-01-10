"""Services for organizational hierarchy and permission management."""
from django.core.cache import cache
from .models import (
    UserRole,
    RolePermission,
    Team,
    HierarchyTeamMember,
    OrganizationNode
)


class PermissionChecker:
    """Real-time permission checking."""

    def __init__(self, user):
        self.user = user
        self._permission_cache = None

    def has_permission(self, permission_code, college=None):
        """
        Check if user has permission.
        Format: "students.create", "fees.approve_invoice"
        """
        if self.user.is_superuser:
            return True

        # Check cache first
        cache_key = f'user_perms_{self.user.id}'
        permissions = cache.get(cache_key)

        if permissions is None:
            permissions = self.get_user_permissions()
            cache.set(cache_key, permissions, timeout=3600)  # 1 hour

        return permission_code in permissions

    def get_user_permissions(self):
        """Get all permissions for user - CACHED."""
        if self._permission_cache is not None:
            return self._permission_cache

        permissions = set()

        # Get all active user roles
        user_roles = UserRole.objects.filter(
            user=self.user,
            is_active=True
        ).select_related('role')

        # Collect all permissions from roles
        for user_role in user_roles:
            role_perms = RolePermission.objects.filter(
                role=user_role.role
            ).select_related('permission')

            for role_perm in role_perms:
                permissions.add(role_perm.permission.code)

        self._permission_cache = list(permissions)
        return self._permission_cache

    @classmethod
    def clear_user_cache(cls, user_id):
        """Clear permission cache for specific user."""
        cache.delete(f'user_perms_{user_id}')


class TeamAutoAssignmentService:
    """Handles automatic team assignment based on hierarchy."""

    @staticmethod
    def assign_student_to_teams(student):
        """
        When student is created/updated:
        1. Find their class teacher
        2. Find teacher's team
        3. Add student to team
        """
        if not hasattr(student, 'section') or not student.section:
            return

        # Get class teacher if exists
        if hasattr(student.section, 'class_teacher') and student.section.class_teacher:
            class_teacher = student.section.class_teacher

            # Find teacher's organization node
            teacher_node = OrganizationNode.objects.filter(
                user=class_teacher.user,
                is_active=True
            ).first()

            if teacher_node and hasattr(teacher_node, 'team'):
                team = teacher_node.team

                # Add student to team
                HierarchyTeamMember.objects.get_or_create(
                    team=team,
                    user=student.user,
                    defaults={
                        'auto_assigned': True,
                        'assignment_reason': f'Student in {class_teacher.user.get_full_name()}\'s class',
                        'role_in_team': 'member'
                    }
                )

    @staticmethod
    def assign_teacher_to_teams(teacher):
        """
        When teacher is created:
        1. Find department head
        2. Find principal
        3. Add to their teams
        """
        if not hasattr(teacher, 'department') or not teacher.department:
            return

        # Find HOD node
        hod_nodes = OrganizationNode.objects.filter(
            node_type='hod',
            college=teacher.college,
            is_active=True
        )

        for hod_node in hod_nodes:
            if hasattr(hod_node, 'team'):
                HierarchyTeamMember.objects.get_or_create(
                    team=hod_node.team,
                    user=teacher.user,
                    defaults={
                        'auto_assigned': True,
                        'assignment_reason': 'Teacher under HOD',
                        'role_in_team': 'member'
                    }
                )

        # Find principal node
        principal_nodes = OrganizationNode.objects.filter(
            node_type='principal',
            college=teacher.college,
            is_active=True
        )

        for principal_node in principal_nodes:
            if hasattr(principal_node, 'team'):
                HierarchyTeamMember.objects.get_or_create(
                    team=principal_node.team,
                    user=teacher.user,
                    defaults={
                        'auto_assigned': True,
                        'assignment_reason': 'Teacher under Principal',
                        'role_in_team': 'member'
                    }
                )

    @staticmethod
    def create_team_for_node(node):
        """Create a team for an organization node."""
        if node.node_type in ['principal', 'hod', 'teacher']:
            team_type_map = {
                'principal': 'principal_team',
                'hod': 'department_team',
                'teacher': 'teacher_team'
            }

            team, created = Team.objects.get_or_create(
                node=node,
                defaults={
                    'name': f"{node.name} Team",
                    'team_type': team_type_map.get(node.node_type, 'administrative_team'),
                    'lead_user': node.user,
                    'college': node.college,
                    'is_active': True
                }
            )

            return team
        return None


class RoleManagementService:
    """Service for managing roles and permissions."""

    @staticmethod
    def assign_role_to_user(assigner, target_user, role, college=None):
        """
        Assign role to user with validation.
        Only allow if:
        1. Assigner has permission
        2. Assigner's role level >= target role level
        """
        from django.core.exceptions import PermissionDenied

        checker = PermissionChecker(assigner)

        if not checker.has_permission('users.assign_role'):
            raise PermissionDenied("No permission to assign roles")

        # Get assigner's max role level
        assigner_max_level = UserRole.objects.filter(
            user=assigner,
            is_active=True
        ).select_related('role').order_by('-role__level').first()

        if assigner_max_level and role.level > assigner_max_level.role.level:
            raise PermissionDenied("Cannot assign role with higher level")

        # Create user role
        user_role, created = UserRole.objects.get_or_create(
            user=target_user,
            role=role,
            college=college,
            defaults={
                'assigned_by': assigner,
                'is_active': True
            }
        )

        # Clear permission cache
        PermissionChecker.clear_user_cache(target_user.id)

        return user_role, created
