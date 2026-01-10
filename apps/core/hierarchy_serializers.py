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
    user_count = serializers.SerializerMethodField()
    college_detail = serializers.SerializerMethodField()
    children_count = serializers.SerializerMethodField()
    team_members_count = serializers.SerializerMethodField()

    class Meta:
        model = OrganizationNode
        fields = '__all__'

    def get_user_count(self, obj):
        """Return count instead of user details."""
        return 1 if obj.user else 0

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
    user_count = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    class Meta:
        model = OrganizationNode
        fields = ['id', 'name', 'node_type', 'description', 'role', 'user_count', 'children', 'is_active', 'order']

    def get_user_count(self, obj):
        """Return count of users instead of user details."""
        return 1 if obj.user else 0

    def get_children(self, obj):
        children = obj.get_children().filter(is_active=True)
        return OrganizationNodeTreeSerializer(children, many=True).data


class HierarchyUserRoleSerializer(serializers.ModelSerializer):
    role_detail = DynamicRoleSerializer(source='role', read_only=True)

    class Meta:
        model = HierarchyUserRole
        fields = '__all__'


class HierarchyTeamMemberSerializer(serializers.ModelSerializer):

    class Meta:
        model = HierarchyTeamMember
        fields = '__all__'


class TeamSerializer(serializers.ModelSerializer):
    members_count = serializers.SerializerMethodField()
    node_detail = OrganizationNodeSerializer(source='node', read_only=True)

    class Meta:
        model = Team
        fields = '__all__'

    def get_members_count(self, obj):
        """Return count of team members instead of member details."""
        return obj.team_members.filter(is_active=True).count()
