"""Serializers for Organization Hierarchy System."""
from rest_framework import serializers
from .models import (
    OrganizationNode,
    DynamicRole,
    HierarchyPermission,
    RolePermission,
    HierarchyUserRole,
    Team,
    HierarchyTeamMember
)


class HierarchyPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HierarchyPermission
        fields = '__all__'


class RolePermissionSerializer(serializers.ModelSerializer):
    permission_detail = HierarchyPermissionSerializer(source='permission', read_only=True)

    class Meta:
        model = RolePermission
        fields = '__all__'


class DynamicRoleSerializer(serializers.ModelSerializer):
    permissions = RolePermissionSerializer(source='role_permissions', many=True, read_only=True)
    permissions_count = serializers.SerializerMethodField()

    class Meta:
        model = DynamicRole
        fields = '__all__'

    def get_permissions_count(self, obj):
        return obj.role_permissions.count()


class OrganizationNodeSerializer(serializers.ModelSerializer):
    role_detail = DynamicRoleSerializer(source='role', read_only=True)
    user_detail = serializers.SerializerMethodField()
    college_detail = serializers.SerializerMethodField()
    children_count = serializers.SerializerMethodField()
    team_members_count = serializers.SerializerMethodField()

    class Meta:
        model = OrganizationNode
        fields = '__all__'

    def get_user_detail(self, obj):
        if obj.user:
            return {
                'id': obj.user.id,
                'name': obj.user.get_full_name(),
                'email': obj.user.email
            }
        return None

    def get_college_detail(self, obj):
        if obj.college:
            return {
                'id': obj.college.id,
                'name': obj.college.name,
                'short_name': obj.college.short_name
            }
        return None

    def get_children_count(self, obj):
        return obj.get_children().count()

    def get_team_members_count(self, obj):
        if hasattr(obj, 'team') and obj.team:
            return obj.team.team_members.count()
        return 0


class OrganizationNodeTreeSerializer(serializers.ModelSerializer):
    """Recursive serializer for tree structure."""
    role = DynamicRoleSerializer(read_only=True)
    user = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    class Meta:
        model = OrganizationNode
        fields = ['id', 'name', 'node_type', 'description', 'role', 'user', 'children', 'is_active', 'order']

    def get_user(self, obj):
        if obj.user:
            return {
                'id': obj.user.id,
                'name': obj.user.get_full_name(),
                'email': obj.user.email
            }
        return None

    def get_children(self, obj):
        children = obj.get_children().filter(is_active=True)
        return OrganizationNodeTreeSerializer(children, many=True).data


class HierarchyUserRoleSerializer(serializers.ModelSerializer):
    role_detail = DynamicRoleSerializer(source='role', read_only=True)
    user_detail = serializers.SerializerMethodField()

    class Meta:
        model = HierarchyUserRole
        fields = '__all__'

    def get_user_detail(self, obj):
        return {
            'id': obj.user.id,
            'name': obj.user.get_full_name(),
            'email': obj.user.email
        }


class HierarchyTeamMemberSerializer(serializers.ModelSerializer):
    user_detail = serializers.SerializerMethodField()

    class Meta:
        model = HierarchyTeamMember
        fields = '__all__'

    def get_user_detail(self, obj):
        return {
            'id': obj.user.id,
            'name': obj.user.get_full_name(),
            'email': obj.user.email
        }


class TeamSerializer(serializers.ModelSerializer):
    members = HierarchyTeamMemberSerializer(source='team_members', many=True, read_only=True)
    node_detail = OrganizationNodeSerializer(source='node', read_only=True)
    lead_detail = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = '__all__'

    def get_lead_detail(self, obj):
        if obj.lead_user:
            return {
                'id': obj.lead_user.id,
                'name': obj.lead_user.get_full_name(),
                'email': obj.lead_user.email
            }
        return None
