"""Services for organizational hierarchy and permission management."""
from .models import (
    HierarchyUserRole,
    RolePermission,
    Team,
    HierarchyTeamMember,
    OrganizationNode
)
from apps.core.permissions.manager import check_permission as existing_check_permission


class PermissionChecker:
    """
    Real-time permission checking - integrates with existing Permission system.
    The hierarchy determines user's role, existing system checks permissions.
    """

    def __init__(self, user):
        self.user = user
        self._permission_cache = None
        self._hierarchy_role_cache = None

    def has_permission(self, module, action):
        """
        Check if user has permission using EXISTING permission system.
        Format: module='students', action='create'
        """
        if getattr(self.user, 'is_superadmin', False) or getattr(self.user, 'is_superuser', False):
            return True

        has_perm, _scope = existing_check_permission(self.user, module, action)
        return has_perm

    def get_hierarchy_roles(self):
        """Get all hierarchy roles assigned to the user."""
        if self._hierarchy_role_cache is not None:
            return self._hierarchy_role_cache

        roles = HierarchyUserRole.objects.filter(
            user=self.user,
            is_active=True
        ).select_related('role')

        self._hierarchy_role_cache = [ur.role for ur in roles]
        return self._hierarchy_role_cache

    def get_primary_hierarchy_role(self):
        """Get the user's primary (highest level) hierarchy role."""
        cache_key = f'user_primary_role_{self.user.id}'
        # Get the role with the highest level
        user_role = HierarchyUserRole.objects.filter(
            user=self.user,
            is_active=True
        ).select_related('role').order_by('-role__level').first()

        if user_role:
            return user_role.role

        return None

    def get_user_permissions_from_hierarchy(self):
        """
        Get granular permissions from hierarchy roles (for hierarchy-specific features).
        This is SEPARATE from the main permission system.
        """
        if self._permission_cache is not None:
            return self._permission_cache

        permissions = set()

        # Get all active user roles
        user_roles = HierarchyUserRole.objects.filter(
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

    def has_hierarchy_permission(self, permission_code):
        """
        Check hierarchy-specific permissions (for org management features).
        Format: permission_code='system.manage_roles'
        """
        if getattr(self.user, 'is_superadmin', False) or getattr(self.user, 'is_superuser', False):
            return True

        cache_key = f'user_hierarchy_perms_{self.user.id}'

        if permissions is None:
            permissions = self.get_user_permissions_from_hierarchy()

        return permission_code in permissions

    @classmethod
    def clear_user_cache(cls, user_id):
        """Clear permission cache for specific user."""




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
        1. Assigner has permission (using existing permission system)
        2. Assigner's role level >= target role level
        """
        from django.core.exceptions import PermissionDenied

        checker = PermissionChecker(assigner)

        # Check using existing permission system (hr.update or system.manage_users)
        if not (checker.has_permission('hr', 'update') or
                checker.has_permission('system', 'update') or
                checker.has_hierarchy_permission('system.manage_users')):
            raise PermissionDenied("No permission to assign roles")

        # Get assigner's max role level
        assigner_max_level = HierarchyUserRole.objects.filter(
            user=assigner,
            is_active=True
        ).select_related('role').order_by('-role__level').first()

        if assigner_max_level and role.level > assigner_max_level.role.level:
            raise PermissionDenied("Cannot assign role with higher level")

        # Create user role
        user_role, created = HierarchyUserRole.objects.get_or_create(
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

        # Sync with existing permission system
        RoleManagementService.sync_hierarchy_role_to_permissions(target_user, role, college)

        return user_role, created

    @staticmethod
    def sync_hierarchy_role_to_permissions(user, hierarchy_role, college):
        """
        Sync hierarchy role to the existing Permission system.
        Creates/updates Permission record for the user's college and role.
        """
        from .models import Permission
        from .permissions_utils import _get_default_permissions_dict

        if not college:
            return

        # Map hierarchy role code to permission role
        role_code = hierarchy_role.code
        if role_code not in ['admin', 'teacher', 'student', 'principal', 'hod', 'accountant', 'librarian']:
            # For custom roles, map to 'admin' by default
            role_code = 'admin'

        # Get or create Permission record for this college and role
        permission, created = Permission.objects.get_or_create(
            college=college,
            role=role_code,
            defaults={
                'permissions_json': _get_default_permissions_dict(role_code),
                'is_active': True
            }
        )

        # Clear cache
        PermissionChecker.clear_user_cache(user.id)
