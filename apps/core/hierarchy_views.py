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

        # Role display names and levels for common user types
        user_type_labels = {
            'student': ('Student', 10),
            'teacher': ('Teacher', 5),
            'hod': ('HOD', 4),
            'principal': ('Principal', 2),
            'staff': ('Staff', 7),
            'store_manager': ('Store Manager', 6),
            'librarian': ('Librarian', 7),
            'accountant': ('Accountant', 6),
            'lab_assistant': ('Lab Assistant', 8),
            'clerk': ('Clerk', 8),
            'college_admin': ('College Admin', 3),
        }

        def build_user_type_node(college_id, user_type, count):
            """Build a virtual node from user_type data."""
            label, level = user_type_labels.get(user_type, (user_type.replace('_', ' ').title(), 9))
            return {
                'id': f'virtual-role-{college_id}-{user_type}',
                'name': label,
                'node_type': user_type,
                'description': f'{count} {label.lower()}(s)',
                'role': {
                    'id': f'virtual-{user_type}',
                    'name': label,
                    'code': user_type,
                    'level': level
                },
                'user': None,
                'children': [],
                'members_count': count,
                'is_active': True,
                'order': level
            }

        # Handle global users (users without college_id or college_id=None)
        global_user_items = [
            (user_type, count)
            for (college_id, user_type), count in user_type_counts.items()
            if college_id is None and count > 0 and user_type not in ['ceo', 'super_admin']
        ]

        for user_type, count in sorted(global_user_items, key=lambda x: user_type_labels.get(x[0], (x[0], 9))[1]):
            global_node = {
                'id': f'virtual-user-type-global-{user_type}',
                'name': user_type_labels.get(user_type, (user_type.replace('_', ' ').title(), 9))[0],
                'node_type': 'staff',
                'description': '',
                'role': {
                    'code': user_type,
                    'name': user_type_labels.get(user_type, (user_type.replace('_', ' ').title(), 9))[0]
                },
                'user': None,
                'children': [],
                'members_count': count,
                'is_active': True,
                'order': 0
            }
            root['children'].append(global_node)

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

            # ALWAYS create roles from actual users based on college_id
            user_type_items = [
                (user_type, count)
                for (college_id, user_type), count in user_type_counts.items()
                if college_id == college.id and count > 0
            ]

            if user_type_items:
                # Check for principal/college_admin user type
                principal_item = next((item for item in user_type_items if item[0] in ['college_admin', 'principal']), None)
                other_items = [item for item in user_type_items if item[0] not in ['college_admin', 'principal']]

                if principal_item:
                    # Create principal node as parent
                    principal_node = build_user_type_node(college.id, principal_item[0], principal_item[1])
                    principal_node['id'] = f'virtual-principal-{college.id}'
                    college_node['children'].append(principal_node)
                    parent_node = principal_node
                else:
                    parent_node = college_node

                # Add other user type nodes sorted by hierarchy level
                for user_type, count in sorted(other_items, key=lambda x: user_type_labels.get(x[0], (x[0], 9))[1]):
                    parent_node['children'].append(build_user_type_node(college.id, user_type, count))

            if college_node['children']:
                root['children'].append(college_node)

        return [root]

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def roles_summary(self, request):
        """Get summary of all roles and their counts per college based on actual users."""
        college_id = request.headers.get('X-College-Id')
        cache_key = f'roles_summary_{college_id or "all"}'
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        User = get_user_model()
        summary = {}

        # Role display names and levels
        user_type_labels = {
            'student': ('Student', 10),
            'teacher': ('Teacher', 5),
            'hod': ('HOD', 4),
            'principal': ('Principal', 2),
            'staff': ('Staff', 7),
            'store_manager': ('Store Manager', 6),
            'librarian': ('Librarian', 7),
            'accountant': ('Accountant', 6),
            'lab_assistant': ('Lab Assistant', 8),
            'clerk': ('Clerk', 8),
            'college_admin': ('College Admin', 3),
        }

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

            # Get actual user counts by type from database
            user_type_data = User.objects.filter(
                college_id=college.id,
                is_active=True
            ).exclude(
                user_type='super_admin'
            ).values('user_type').annotate(count=Count('id'))

            role_list = []
            for row in user_type_data:
                user_type = row['user_type']
                count = row['count']
                label, level = user_type_labels.get(user_type, (user_type.replace('_', ' ').title(), 9))

                role_list.append({
                    'role_name': label,
                    'role_code': user_type,
                    'count': count,
                    'level': level
                })

            college_summary['roles'] = sorted(role_list, key=lambda x: (x['level'], x['role_name']))
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
