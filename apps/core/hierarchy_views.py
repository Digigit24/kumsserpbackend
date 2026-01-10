"""ViewSets for Organization Hierarchy System."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.core.permissions.drf_permissions import IsSuperAdmin
from django.core.cache import cache
from django.db import models
from django.db.models import Count, Q
from django.contrib.auth import get_user_model
from apps.core.permissions.registry import PERMISSION_REGISTRY
from apps.accounts.models import Role as AccountRole, UserRole as AccountUserRole
from .models import (
    OrganizationNode,
    DynamicRole,
    HierarchyPermission,
    RolePermission,
    HierarchyUserRole,
    Team,
    HierarchyTeamMember,
    Permission,
    College
)
from .hierarchy_serializers import (
    OrganizationNodeSerializer,
    OrganizationNodeTreeSerializer,
    DynamicRoleSerializer,
    HierarchyPermissionSerializer,
    RolePermissionSerializer,
    HierarchyUserRoleSerializer,
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

        # Handle 'all' or invalid college_id
        if college_id and college_id.lower() != 'all':
            try:
                queryset = queryset.filter(college_id=int(college_id))
            except (ValueError, TypeError):
                pass  # Invalid college_id, return all nodes

        return queryset

    def _build_virtual_tree(self):
        """Build optimized virtual tree with role counts only."""
        colleges = College.objects.filter(is_active=True).order_by('name')
        dynamic_roles = DynamicRole.objects.filter(is_active=True).select_related('college')
        account_roles = AccountRole.objects.filter(is_active=True).select_related('college', 'parent')
        User = get_user_model()

        # Fetch all role counts efficiently
        account_role_counts = dict(
            AccountUserRole.objects.filter(is_active=True)
            .values('role_id', 'college_id')
            .annotate(total=Count('id'))
            .values_list('role_id', 'total')
        )
        dynamic_role_counts = dict(
            HierarchyUserRole.objects.filter(is_active=True)
            .values('role_id', 'college_id')
            .annotate(total=Count('id'))
            .values_list('role_id', 'total')
        )
        user_type_counts = {
            (row['college_id'], row['user_type']): row['total']
            for row in User.objects.filter(is_active=True)
            .exclude(user_type='super_admin')
            .values('college_id', 'user_type')
            .annotate(total=Count('id'))
        }

        role_by_code = {role.code.lower(): role for role in dynamic_roles if role.code}
        node_type_codes = {code for code, _label in OrganizationNode.NODE_TYPES}

        ceo_role = role_by_code.get('ceo')

        root = {
            'id': 'virtual-ceo',
            'name': 'CEO',
            'node_type': 'ceo',
            'description': 'Super Admin',
            'role': DynamicRoleSerializer(ceo_role).data if ceo_role else None,
            'user': None,
            'children': [],
            'is_active': True,
            'order': 0
        }

        def serialize_account_role(role):
            return {
                'id': role.id,
                'name': role.name,
                'code': role.code,
                'description': role.description or '',
                'level': role.level,
                'college': role.college_id
            }

        def get_user_type_count(role_code, college_id):
            if not role_code or not college_id:
                return 0
            return user_type_counts.get((college_id, role_code), 0)

        def get_account_members_count(role, college_id):
            role_code = (role.code or '').lower()
            role_count = account_role_counts.get(role.id, 0)
            user_type_count = get_user_type_count(role_code, college_id)
            return max(role_count, user_type_count)

        def get_dynamic_members_count(role, college_id):
            role_code = (role.code or '').lower()
            role_count = dynamic_role_counts.get(role.id, 0)
            user_type_count = get_user_type_count(role_code, college_id)
            return max(role_count, user_type_count)

        def role_to_node(role, role_payload, members_count):
            role_code = (role.code or '').lower()
            node_type = role_code if role_code in node_type_codes else 'staff'
            return {
                'id': f'virtual-role-{role.id}',
                'name': role.name,
                'node_type': node_type,
                'description': role.description or '',
                'role': role_payload,
                'user': None,
                'children': [],
                'members_count': members_count,
                'is_active': True,
                'order': role.level
            }

        def attach_roles_by_level(parent_node, role_list, college_id):
            sorted_roles = sorted(role_list, key=lambda r: (r.level, r.name.lower()))
            stack = []
            for role in sorted_roles:
                count = get_dynamic_members_count(role, college_id)
                # Always show all roles with their counts (even if 0)
                node = role_to_node(role, DynamicRoleSerializer(role).data, count)
                while stack and role.level <= stack[-1][0]:
                    stack.pop()
                if stack:
                    stack[-1][1]['children'].append(node)
                else:
                    parent_node['children'].append(node)
                stack.append((role.level, node))

        def attach_roles_by_parent(parent_node, role_list, college_id):
            nodes = {}
            for role in role_list:
                count = get_account_members_count(role, college_id)
                # Always show all roles with their counts (even if 0)
                role_payload = serialize_account_role(role)
                nodes[role.id] = role_to_node(role, role_payload, count)

            for role in role_list:
                node = nodes.get(role.id)
                if not node:
                    continue
                if role.parent_id and role.parent_id in nodes:
                    nodes[role.parent_id]['children'].append(node)
                else:
                    parent_node['children'].append(node)

        for college in colleges:
            college_node = {
                'id': f'virtual-college-{college.id}',
                'name': college.name,
                'node_type': 'college',
                'description': college.short_name or '',
                'role': None,
                'user': None,
                'children': [],
                'is_active': True,
                'order': 0
            }

            account_roles_college = [role for role in account_roles if role.college_id == college.id]
            if account_roles_college:
                attach_roles_by_parent(college_node, account_roles_college, college.id)
                if college_node['children']:
                    root['children'].append(college_node)
                    continue
                college_node['children'] = []

            dynamic_roles_college = [
                role for role in dynamic_roles
                if role.college_id == college.id or (role.college_id is None and role.is_global)
            ]

            principal_role = None
            for candidate in dynamic_roles_college:
                if candidate.code and candidate.code.lower() in ['college_admin', 'principal']:
                    principal_role = candidate
                    break

            filtered_roles = [
                r for r in dynamic_roles_college
                if r != principal_role and r != ceo_role
            ]

            # Always show all roles, including those with 0 count
            if principal_role or filtered_roles:
                if principal_role:
                    principal_count = get_dynamic_members_count(principal_role, college.id)
                    principal_node = role_to_node(
                        principal_role,
                        DynamicRoleSerializer(principal_role).data,
                        principal_count
                    )
                    principal_node['id'] = f'virtual-principal-{college.id}'
                    college_node['children'].append(principal_node)
                    attach_roles_by_level(principal_node, filtered_roles, college.id)
                else:
                    attach_roles_by_level(college_node, filtered_roles, college.id)

            if college_node['children']:
                root['children'].append(college_node)

        return [root]

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def roles_summary(self, request):
        """Get summary of all roles and their counts per college."""
        college_id = request.headers.get('X-College-Id')
        cache_key = f'roles_summary_{college_id or "all"}'
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        User = get_user_model()
        summary = {}

        # Get colleges to query
        if college_id and college_id.lower() != 'all':
            try:
                colleges = College.objects.filter(id=int(college_id), is_active=True)
            except (ValueError, TypeError):
                colleges = College.objects.filter(is_active=True)
        else:
            colleges = College.objects.filter(is_active=True)

        for college in colleges:
            college_summary = {
                'college_id': college.id,
                'college_name': college.name,
                'roles': []
            }

            # Get all role types with counts
            role_counts = {}

            # Dynamic roles
            dynamic_roles = DynamicRole.objects.filter(
                Q(college_id=college.id) | Q(is_global=True),
                is_active=True
            )

            for role in dynamic_roles:
                count = HierarchyUserRole.objects.filter(
                    role=role,
                    college_id=college.id,
                    is_active=True
                ).count()

                # Also check user_type counts
                if role.code:
                    user_type_count = User.objects.filter(
                        college_id=college.id,
                        user_type=role.code.lower(),
                        is_active=True
                    ).count()
                    count = max(count, user_type_count)

                if count > 0:
                    role_counts[role.name] = {
                        'role_name': role.name,
                        'role_code': role.code,
                        'count': count,
                        'level': role.level
                    }

            # Account roles
            account_roles = AccountRole.objects.filter(
                college_id=college.id,
                is_active=True
            )

            for role in account_roles:
                count = AccountUserRole.objects.filter(
                    role=role,
                    is_active=True
                ).count()

                # Also check user_type counts
                if role.code:
                    user_type_count = User.objects.filter(
                        college_id=college.id,
                        user_type=role.code.lower(),
                        is_active=True
                    ).count()
                    count = max(count, user_type_count)

                if count > 0:
                    role_counts[role.name] = {
                        'role_name': role.name,
                        'role_code': role.code,
                        'count': count,
                        'level': role.level
                    }

            college_summary['roles'] = sorted(
                role_counts.values(),
                key=lambda x: (x['level'], x['role_name'])
            )
            college_summary['total_roles'] = len(college_summary['roles'])

            summary[college.name] = college_summary

        cache.set(cache_key, summary, timeout=300)
        return Response(summary)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsSuperAdmin])
    def tree(self, request):
        """Return full tree structure."""
        college_id = request.headers.get('X-College-Id')
        cache_key = f'org_tree_{college_id or "all"}'
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        root_nodes = self.get_queryset().filter(parent__isnull=True)
        if root_nodes.exists():
            serializer = OrganizationNodeTreeSerializer(root_nodes, many=True)
            cache.set(cache_key, serializer.data, timeout=300)  # 5 minutes
            return Response(serializer.data)

        virtual_tree = self._build_virtual_tree()
        cache.set(cache_key, virtual_tree, timeout=300)  # 5 minutes
        return Response(virtual_tree)

    def perform_create(self, serializer):
        cache.delete_pattern('org_tree_*')
        cache.delete_pattern('roles_summary_*')
        serializer.save()

    def perform_update(self, serializer):
        cache.delete_pattern('org_tree_*')
        cache.delete_pattern('roles_summary_*')
        serializer.save()


class DynamicRoleViewSet(viewsets.ModelViewSet):
    """CRUD operations for roles."""
    queryset = DynamicRole.objects.all()
    serializer_class = DynamicRoleSerializer
    permission_classes = [IsAuthenticated]

    def _normalize_permissions_json(self, payload):
        normalized = {}

        if not isinstance(payload, dict):
            return normalized

        for resource, config in PERMISSION_REGISTRY.items():
            resource_payload = payload.get(resource)
            if not isinstance(resource_payload, dict):
                continue

            actions = {}
            for action in config['actions']:
                if action not in resource_payload:
                    continue

                action_payload = resource_payload[action]
                if isinstance(action_payload, dict):
                    enabled = bool(action_payload.get('enabled', False))
                    scope = action_payload.get('scope', 'none')
                else:
                    enabled = bool(action_payload)
                    scope = 'all' if enabled else 'none'

                actions[action] = {
                    'scope': scope,
                    'enabled': enabled
                }

            if actions:
                normalized[resource] = actions

        return normalized

    def _get_permission_college(self, role):
        if role.college_id:
            return role.college

        college_id = self.request.headers.get('X-College-Id')
        if college_id and college_id.lower() != 'all':
            try:
                return College.objects.filter(id=int(college_id)).first()
            except (ValueError, TypeError):
                return None

        return None

    def _update_permission_record(self, role, permissions_payload):
        permissions_json = self._normalize_permissions_json(permissions_payload)
        if not permissions_json:
            return None

        college = self._get_permission_college(role)
        if not college:
            return None

        permission, created = Permission.objects.get_or_create(
            college=college,
            role=role.code,
            defaults={'permissions_json': permissions_json, 'is_active': True}
        )

        if not created:
            permission.permissions_json = permissions_json
            permission.is_active = True
            permission.save()

        return permission

    def perform_create(self, serializer):
        role = serializer.save()
        permissions_payload = self.request.data.get('permissions_json')
        if permissions_payload:
            self._update_permission_record(role, permissions_payload)

    def perform_update(self, serializer):
        role = serializer.save()
        permissions_payload = self.request.data.get('permissions_json')
        if permissions_payload:
            self._update_permission_record(role, permissions_payload)

    def get_queryset(self):
        queryset = DynamicRole.objects.filter(is_active=True)
        college_id = self.request.headers.get('X-College-Id')

        if college_id and college_id.lower() != 'all':
            try:
                queryset = queryset.filter(college_id=int(college_id)) | queryset.filter(is_global=True)
            except (ValueError, TypeError):
                queryset = queryset.filter(is_global=True)

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

        permissions_payload = request.data.get('permissions_json')
        if permissions_payload:
            self._update_permission_record(role, permissions_payload)

        # Clear cache for users with this role
        self._clear_user_permission_cache(role)

        return Response({'status': 'permissions updated'})

    def _clear_user_permission_cache(self, role):
        """Clear permission cache for all users with this role."""
        user_ids = HierarchyUserRole.objects.filter(role=role, is_active=True).values_list('user_id', flat=True)
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


class HierarchyUserRoleViewSet(viewsets.ModelViewSet):
    """Assign/revoke hierarchy roles to users."""
    queryset = HierarchyUserRole.objects.all()
    serializer_class = HierarchyUserRoleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return HierarchyUserRole.objects.filter(is_active=True)

    @action(detail=False, methods=['post'])
    def assign(self, request):
        """Assign role to user."""
        user_id = request.data.get('user_id')
        role_id = request.data.get('role_id')
        college_id = request.data.get('college_id')

        user_role, created = HierarchyUserRole.objects.get_or_create(
            user_id=user_id,
            role_id=role_id,
            college_id=college_id,
            defaults={
                'assigned_by': request.user,
                'is_active': True
            }
        )

        cache.delete(f'user_perms_{user_id}')
        return Response(HierarchyUserRoleSerializer(user_role).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def revoke(self, request):
        """Revoke role from user."""
        user_id = request.data.get('user_id')
        role_id = request.data.get('role_id')

        HierarchyUserRole.objects.filter(
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

        if college_id and college_id.lower() != 'all':
            try:
                queryset = queryset.filter(college_id=int(college_id))
            except (ValueError, TypeError):
                pass

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
