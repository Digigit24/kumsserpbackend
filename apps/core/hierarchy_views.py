"""ViewSets for Organization Hierarchy System."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from .models import (
    OrganizationNode,
    DynamicRole,
    HierarchyPermission,
    RolePermission,
    UserRole,
    Team,
    HierarchyTeamMember
)
from .hierarchy_serializers import (
    OrganizationNodeSerializer,
    OrganizationNodeTreeSerializer,
    DynamicRoleSerializer,
    HierarchyPermissionSerializer,
    RolePermissionSerializer,
    UserRoleSerializer,
    TeamSerializer,
    HierarchyTeamMemberSerializer
)


class OrganizationNodeViewSet(viewsets.ModelViewSet):
    """CRUD operations for organization nodes."""
    queryset = OrganizationNode.objects.all()
    serializer_class = OrganizationNodeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = OrganizationNode.objects.filter(is_active=True)
        college_id = self.request.headers.get('X-College-Id')
        if college_id:
            queryset = queryset.filter(college_id=college_id)
        return queryset

    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Return full tree structure."""
        cache_key = f'org_tree_{request.headers.get("X-College-Id", "all")}'
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        root_nodes = self.get_queryset().filter(parent__isnull=True)
        serializer = OrganizationNodeTreeSerializer(root_nodes, many=True)
        cache.set(cache_key, serializer.data, timeout=300)  # 5 minutes
        return Response(serializer.data)

    def perform_create(self, serializer):
        cache.delete_pattern('org_tree_*')
        serializer.save()

    def perform_update(self, serializer):
        cache.delete_pattern('org_tree_*')
        serializer.save()


class DynamicRoleViewSet(viewsets.ModelViewSet):
    """CRUD operations for roles."""
    queryset = DynamicRole.objects.all()
    serializer_class = DynamicRoleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = DynamicRole.objects.filter(is_active=True)
        college_id = self.request.headers.get('X-College-Id')
        if college_id:
            queryset = queryset.filter(college_id=college_id) | queryset.filter(is_global=True)
        return queryset

    @action(detail=True, methods=['patch'])
    def update_permissions(self, request, pk=None):
        """Add or remove permissions from a role."""
        role = self.get_object()
        add_perms = request.data.get('add', [])
        remove_perms = request.data.get('remove', [])

        # Add permissions
        for perm_id in add_perms:
            RolePermission.objects.get_or_create(
                role=role,
                permission_id=perm_id,
                defaults={'can_delegate': False, 'scope': 'college'}
            )

        # Remove permissions
        RolePermission.objects.filter(
            role=role,
            permission_id__in=remove_perms
        ).delete()

        # Clear cache for users with this role
        self._clear_user_permission_cache(role)

        return Response({'status': 'permissions updated'})

    def _clear_user_permission_cache(self, role):
        """Clear permission cache for all users with this role."""
        user_ids = UserRole.objects.filter(role=role, is_active=True).values_list('user_id', flat=True)
        for user_id in user_ids:
            cache.delete(f'user_perms_{user_id}')


class HierarchyPermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only permissions list."""
    queryset = HierarchyPermission.objects.all()
    serializer_class = HierarchyPermissionSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Group permissions by category."""
        categories = {}
        for perm in self.get_queryset():
            cat = perm.category or 'Other'
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(HierarchyPermissionSerializer(perm).data)
        return Response(categories)


class UserRoleViewSet(viewsets.ModelViewSet):
    """Assign/revoke roles to users."""
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserRole.objects.filter(is_active=True)

    @action(detail=False, methods=['post'])
    def assign(self, request):
        """Assign role to user."""
        user_id = request.data.get('user_id')
        role_id = request.data.get('role_id')
        college_id = request.data.get('college_id')

        user_role, created = UserRole.objects.get_or_create(
            user_id=user_id,
            role_id=role_id,
            college_id=college_id,
            defaults={
                'assigned_by': request.user,
                'is_active': True
            }
        )

        cache.delete(f'user_perms_{user_id}')
        return Response(UserRoleSerializer(user_role).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def revoke(self, request):
        """Revoke role from user."""
        user_id = request.data.get('user_id')
        role_id = request.data.get('role_id')

        UserRole.objects.filter(
            user_id=user_id,
            role_id=role_id
        ).update(is_active=False)

        cache.delete(f'user_perms_{user_id}')
        return Response({'status': 'role revoked'})


class TeamViewSet(viewsets.ModelViewSet):
    """Team management."""
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Team.objects.filter(is_active=True)
        college_id = self.request.headers.get('X-College-Id')
        if college_id:
            queryset = queryset.filter(college_id=college_id)
        return queryset

    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Get team members."""
        team = self.get_object()
        members = team.team_members.all()
        serializer = HierarchyTeamMemberSerializer(members, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """Add member to team."""
        team = self.get_object()
        user_id = request.data.get('user_id')

        member, created = HierarchyTeamMember.objects.get_or_create(
            team=team,
            user_id=user_id,
            defaults={
                'role_in_team': 'member',
                'auto_assigned': False
            }
        )

        return Response(
            HierarchyTeamMemberSerializer(member).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )
