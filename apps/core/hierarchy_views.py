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
        """Build dynamic virtual tree based on actual users in database."""
        User = get_user_model()

        # Get college_id from request header for filtering
        college_id_header = self.request.headers.get('X-College-Id') if hasattr(self, 'request') else None

        # Fetch actual user counts by college and user_type
        user_query = User.objects.filter(is_active=True).exclude(user_type='super_admin')

        # Apply college filter if specified
        if college_id_header and college_id_header.lower() != 'all':
            try:
                college_id_filter = int(college_id_header)
                user_query = user_query.filter(
                    Q(college_id=college_id_filter) | Q(college_id__isnull=True)
                )
            except (ValueError, TypeError):
                pass

        user_type_counts = {
            (row['college_id'], row['user_type']): row['total']
            for row in user_query.values('college_id', 'user_type').annotate(total=Count('id'))
        }

        # Get role assignments from HierarchyUserRole (role.code as user_type equivalent)
        hierarchy_role_query = HierarchyUserRole.objects.filter(is_active=True).select_related('role', 'user')
        if college_id_header and college_id_header.lower() != 'all':
            try:
                college_id_filter = int(college_id_header)
                hierarchy_role_query = hierarchy_role_query.filter(
                    Q(college_id=college_id_filter) | Q(college_id__isnull=True)
                )
            except (ValueError, TypeError):
                pass

        hierarchy_role_counts = {}
        for hr in hierarchy_role_query.filter(user__is_active=True):
            role_code = (hr.role.code or '').lower()
            key = (hr.college_id, role_code)
            hierarchy_role_counts[key] = hierarchy_role_counts.get(key, 0) + 1

        # Get role assignments from AccountUserRole (role.code as user_type equivalent)
        account_role_query = AccountUserRole.objects.filter(is_active=True).select_related('role', 'user')
        if college_id_header and college_id_header.lower() != 'all':
            try:
                college_id_filter = int(college_id_header)
                account_role_query = account_role_query.filter(
                    Q(college_id=college_id_filter) | Q(college_id__isnull=True)
                )
            except (ValueError, TypeError):
                pass

        account_role_counts = {}
        for ar in account_role_query.filter(user__is_active=True):
            role_code = (ar.role.code or '').lower()
            key = (ar.college_id, role_code)
            account_role_counts[key] = account_role_counts.get(key, 0) + 1

        # Merge all counts: user_type + hierarchy_roles + account_roles
        all_role_counts = {}
        # Add user_type counts
        for key, count in user_type_counts.items():
            all_role_counts[key] = count
        # Add hierarchy role counts
        for key, count in hierarchy_role_counts.items():
            all_role_counts[key] = all_role_counts.get(key, 0) + count
        # Add account role counts
        for key, count in account_role_counts.items():
            all_role_counts[key] = all_role_counts.get(key, 0) + count

        # Comprehensive role display names with levels (lower number = higher authority)
        user_type_labels = {
            'ceo': ('CEO', 0),
            'college_admin': ('Principal', 2),
            'principal': ('Principal', 2),
            'admin': ('Admin', 3),
            'viceprincipal': ('Vice Principal', 3),
            'viceprincipal_super': ('Vice Principal/Superintendent', 3),
            'hod': ('HOD', 4),
            'teacher': ('Teacher', 5),
            'professor': ('Professor', 5),
            'associate_professor': ('Associate Professor', 5),
            'assistant_professor': ('Assistant Professor', 5),
            'store_manager': ('Store Manager', 6),
            'central_manager': ('Central Store Manager', 6),
            'accountant': ('Accountant', 6),
            'librarian': ('Librarian', 7),
            'hostel_warden': ('Hostel Warden', 7),
            'warden': ('Warden', 7),
            'hostel_incharge': ('Hostel Incharge', 7),
            'hostel_rector': ('Hostel Rector', 7),
            'staff': ('Staff', 8),
            'peon': ('Peon', 8),
            'lab_assistant': ('Lab Assistant', 8),
            'clerk': ('Clerk', 8),
            'telecaller': ('Telecaller', 8),
            'jr_engineer': ('Jr Engineer', 8),
            'admission': ('Admission Officer', 8),
            'student': ('Student', 10),
            'parent': ('Parent', 11),
        }

        node_type_codes = {code for code, _label in OrganizationNode.NODE_TYPES}

        # Build CEO root node
        root = {
            'id': 'virtual-ceo',
            'name': 'CEO',
            'node_type': 'ceo',
            'description': 'Super Admin',
            'role': {'code': 'ceo', 'name': 'CEO', 'level': 0},
            'user': None,
            'children': [],
            'is_active': True,
            'order': 0
        }

        def build_user_type_node(college_id, user_type, count):
            """Build a virtual node from actual user_type data."""
            label, level = user_type_labels.get(user_type, (user_type.replace('_', ' ').title(), 9))
            node_type = user_type if user_type in node_type_codes else 'staff'

            return {
                'id': f'virtual-role-{college_id or "global"}-{user_type}',
                'name': label,
                'node_type': node_type,
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

        # Handle global users (college_id is None)
        global_user_items = [
            (user_type, count)
            for (cid, user_type), count in all_role_counts.items()
            if cid is None and count > 0
        ]

        for user_type, count in sorted(global_user_items, key=lambda x: user_type_labels.get(x[0], (x[0], 9))[1]):
            root['children'].append(build_user_type_node(None, user_type, count))

        # Get colleges to display
        colleges_query = College.objects.filter(is_active=True).order_by('name')
        if college_id_header and college_id_header.lower() != 'all':
            try:
                colleges_query = colleges_query.filter(id=int(college_id_header))
            except (ValueError, TypeError):
                pass

        # Build college nodes with their users
        for college in colleges_query:
            # Get user types for this college
            user_type_items = [
                (user_type, count)
                for (cid, user_type), count in all_role_counts.items()
                if cid == college.id and count > 0
            ]

            # Skip colleges with no users
            if not user_type_items:
                continue

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

            # Find principal/college_admin first (they are the top of college hierarchy)
            principal_item = next(
                (item for item in user_type_items if item[0] in ['college_admin', 'principal']),
                None
            )
            other_items = [
                item for item in user_type_items
                if item[0] not in ['college_admin', 'principal']
            ]

            if principal_item:
                # Principal is direct child of college
                principal_node = build_user_type_node(college.id, principal_item[0], principal_item[1])
                principal_node['id'] = f'virtual-principal-{college.id}'
                college_node['children'].append(principal_node)
                # Other roles are children of principal
                parent_node = principal_node
            else:
                # No principal, attach roles directly to college
                parent_node = college_node

            # Add all other roles sorted by level
            for user_type, count in sorted(other_items, key=lambda x: user_type_labels.get(x[0], (x[0], 9))[1]):
                parent_node['children'].append(build_user_type_node(college.id, user_type, count))

            root['children'].append(college_node)

        return [root]

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def roles_summary(self, request):
        """Get summary of all roles and their counts per college based on actual users and role assignments."""
        college_id = request.headers.get('X-College-Id')
        cache_key = f'roles_summary_{college_id or "all"}'
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        User = get_user_model()
        summary = {}

        # Comprehensive role display names with levels (must match tree building)
        user_type_labels = {
            'ceo': ('CEO', 0),
            'college_admin': ('Principal', 2),
            'principal': ('Principal', 2),
            'admin': ('Admin', 3),
            'viceprincipal': ('Vice Principal', 3),
            'viceprincipal_super': ('Vice Principal/Superintendent', 3),
            'hod': ('HOD', 4),
            'teacher': ('Teacher', 5),
            'professor': ('Professor', 5),
            'associate_professor': ('Associate Professor', 5),
            'assistant_professor': ('Assistant Professor', 5),
            'store_manager': ('Store Manager', 6),
            'central_manager': ('Central Store Manager', 6),
            'accountant': ('Accountant', 6),
            'librarian': ('Librarian', 7),
            'hostel_warden': ('Hostel Warden', 7),
            'warden': ('Warden', 7),
            'hostel_incharge': ('Hostel Incharge', 7),
            'hostel_rector': ('Hostel Rector', 7),
            'staff': ('Staff', 8),
            'peon': ('Peon', 8),
            'lab_assistant': ('Lab Assistant', 8),
            'clerk': ('Clerk', 8),
            'telecaller': ('Telecaller', 8),
            'jr_engineer': ('Jr Engineer', 8),
            'admission': ('Admission Officer', 8),
            'student': ('Student', 10),
            'parent': ('Parent', 11),
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

            # Collect all role counts from multiple sources
            role_counts = {}

            # 1. Get counts from user_type field
            user_type_data = User.objects.filter(
                college_id=college.id,
                is_active=True
            ).exclude(
                user_type='super_admin'
            ).values('user_type').annotate(count=Count('id'))

            for row in user_type_data:
                role_counts[row['user_type']] = row['count']

            # 2. Get counts from HierarchyUserRole assignments
            hierarchy_roles = HierarchyUserRole.objects.filter(
                college_id=college.id,
                is_active=True,
                user__is_active=True
            ).select_related('role').values('role__code').annotate(count=Count('id'))

            for row in hierarchy_roles:
                role_code = (row['role__code'] or '').lower()
                if role_code:
                    role_counts[role_code] = role_counts.get(role_code, 0) + row['count']

            # 3. Get counts from AccountUserRole assignments
            account_roles = AccountUserRole.objects.filter(
                college_id=college.id,
                is_active=True,
                user__is_active=True
            ).select_related('role').values('role__code').annotate(count=Count('id'))

            for row in account_roles:
                role_code = (row['role__code'] or '').lower()
                if role_code:
                    role_counts[role_code] = role_counts.get(role_code, 0) + row['count']

            # Build role list with labels
            role_list = []
            for role_code, count in role_counts.items():
                if count > 0:
                    label, level = user_type_labels.get(role_code, (role_code.replace('_', ' ').title(), 9))
                    role_list.append({
                        'role_name': label,
                        'role_code': role_code,
                        'count': count,
                        'level': level
                    })

            college_summary['roles'] = sorted(role_list, key=lambda x: (x['level'], x['role_name']))
            college_summary['total_roles'] = len(college_summary['roles'])

            summary[college.name] = college_summary

        cache.set(cache_key, summary, timeout=300)
        return Response(summary)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def tree(self, request):
        """Return full tree structure filtered by college_id."""
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
        queryset = HierarchyUserRole.objects.filter(is_active=True)
        user = getattr(self.request, 'user', None)
        college_id = self.request.headers.get('X-College-Id')

        is_global_user = (
            getattr(user, 'is_superadmin', False) or
            getattr(user, 'is_superuser', False) or
            getattr(user, 'user_type', None) == 'central_manager'
        )

        if user and not is_global_user and getattr(user, 'college_id', None):
            college_id = user.college_id

        if college_id and str(college_id).lower() != 'all':
            try:
                return queryset.filter(college_id=int(college_id))
            except (ValueError, TypeError):
                return queryset

        if college_id == 'all' and not is_global_user:
            return queryset.none()

        if not college_id and not is_global_user:
            return queryset.none()

        return queryset

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
