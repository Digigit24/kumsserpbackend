"""
Serializers for Permission Management System.
Handles role-based permissions for different modules.
"""
from rest_framework import serializers
from .models import Permission, College


class PermissionSerializer(serializers.ModelSerializer):
    """Serializer for Permission model with full details."""

    college_name = serializers.CharField(source='college.name', read_only=True)
    role_display = serializers.SerializerMethodField()

    class Meta:
        model = Permission
        fields = [
            'id', 'college', 'college_name', 'role', 'role_display',
            'permissions_json', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_role_display(self, obj):
        """Get human-readable role name."""
        role_mapping = {
            'student': 'Student',
            'teacher': 'Teacher',
            'admin': 'Administrator',
            'hod': 'Head of Department',
            'accountant': 'Accountant',
            'librarian': 'Librarian',
        }
        return role_mapping.get(obj.role, obj.role.title())


class PermissionUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating permissions.
    Frontend sends only the TRUE permissions for each module.
    """

    role = serializers.CharField(
        required=True,
        help_text="User role to update permissions for"
    )

    # Module permissions - only TRUE permissions are sent
    students = serializers.DictField(
        child=serializers.BooleanField(),
        required=False,
        default=dict,
        help_text="Students module permissions (create, read, update, delete)"
    )

    classes = serializers.DictField(
        child=serializers.BooleanField(),
        required=False,
        default=dict,
        help_text="Classes module permissions"
    )

    subjects = serializers.DictField(
        child=serializers.BooleanField(),
        required=False,
        default=dict,
        help_text="Subjects module permissions"
    )

    attendance = serializers.DictField(
        child=serializers.BooleanField(),
        required=False,
        default=dict,
        help_text="Attendance module permissions"
    )

    examinations = serializers.DictField(
        child=serializers.BooleanField(),
        required=False,
        default=dict,
        help_text="Examinations module permissions"
    )

    fees = serializers.DictField(
        child=serializers.BooleanField(),
        required=False,
        default=dict,
        help_text="Fees module permissions"
    )

    library = serializers.DictField(
        child=serializers.BooleanField(),
        required=False,
        default=dict,
        help_text="Library module permissions"
    )

    hr = serializers.DictField(
        child=serializers.BooleanField(),
        required=False,
        default=dict,
        help_text="HR module permissions"
    )

    accounting = serializers.DictField(
        child=serializers.BooleanField(),
        required=False,
        default=dict,
        help_text="Accounting module permissions"
    )

    reports = serializers.DictField(
        child=serializers.BooleanField(),
        required=False,
        default=dict,
        help_text="Reports module permissions"
    )

    def validate_role(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Role is required")
        return value

    def validate(self, data):
        """Validate that at least one module permission is provided."""
        module_fields = [
            'students', 'classes', 'subjects', 'attendance',
            'examinations', 'fees', 'library', 'hr',
            'accounting', 'reports'
        ]

        has_permissions = any(data.get(field) for field in module_fields)

        if not has_permissions:
            raise serializers.ValidationError(
                "At least one module permission must be specified"
            )

        return data

    def to_permissions_json(self):
        """
        Convert the serializer data to permissions_json format.
        Only includes modules that have at least one TRUE permission.
        """
        data = self.validated_data
        role = data.pop('role')

        permissions_json = {}

        for module, perms in data.items():
            if perms:  # Only include modules with permissions
                permissions_json[module] = perms

        return role, permissions_json


class BulkPermissionSerializer(serializers.Serializer):
    """
    Serializer for bulk permission updates.
    Used when updating multiple roles at once.
    """

    permissions = serializers.ListField(
        child=PermissionUpdateSerializer(),
        min_length=1,
        help_text="List of permission updates for different roles"
    )


class PermissionCheckSerializer(serializers.Serializer):
    """
    Serializer for checking if a user has specific permissions.
    """

    module = serializers.CharField(
        required=True,
        help_text="Module name (e.g., 'students', 'attendance')"
    )

    action = serializers.ChoiceField(
        choices=['create', 'read', 'update', 'delete'],
        required=True,
        help_text="Action to check permission for"
    )

    role = serializers.CharField(
        required=False,
        help_text="Role to check (defaults to current user's role)"
    )
