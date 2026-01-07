"""
DRF ViewSets for Accounts app with comprehensive API documentation.
"""
from rest_framework import status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from dj_rest_auth.views import LoginView as DRALoginView
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiExample,
    OpenApiResponse,
)
from drf_spectacular.types import OpenApiTypes
from django.utils import timezone

from .models import (
    User,
    Role,
    UserRole,
    Department,
    UserProfile,
    UserType
)
from .serializers import (
    UserSerializer,
    UserListSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    CustomPasswordChangeSerializer,
    TokenWithUserSerializer,
    RoleSerializer,
    RoleListSerializer,
    RoleTreeSerializer,
    UserRoleSerializer,
    DepartmentSerializer,
    DepartmentListSerializer,
    UserProfileSerializer,
    UserBulkDeleteSerializer,
    UserBulkActivateSerializer,
    BulkUserTypeUpdateSerializer,
)
from apps.core.mixins import CollegeScopedModelViewSet, CollegeScopedReadOnlyModelViewSet


# ============================================================================
# AUTH: LOGIN VIEW
# ============================================================================


class LoginViewNoAuth(DRALoginView):
    """
    Override login to ignore incoming Authorization headers so stale tokens
    don't trigger TokenAuthentication before credentials are checked.
    Enhanced to return comprehensive user details including college info, roles,
    permissions, and profile data on successful login.
    """
    authentication_classes = []

    def get_response_serializer(self):
        """Override to use our custom TokenWithUserSerializer."""
        return TokenWithUserSerializer

    def post(self, request, *args, **kwargs):
        """Override post to log user details to console after successful login."""
        import logging
        import json

        logger = logging.getLogger(__name__)

        # Call the parent login method
        response = super().post(request, *args, **kwargs)

        # Log user details to console if login was successful
        if response.status_code == 200 and response.data:
            user_data = response.data

            logger.info("=" * 80)
            logger.info("LOGIN SUCCESSFUL")
            logger.info("=" * 80)

            # Log the complete response data
            logger.info("Complete Response Data:")
            logger.info(json.dumps(user_data, indent=2, default=str))

            # Log user object details if present
            if 'user' in user_data:
                logger.info("-" * 80)
                logger.info("USER DETAILS:")
                logger.info("-" * 80)
                user = user_data['user']
                for key, value in user.items():
                    logger.info(f"  {key}: {value}")

            # Log authentication token
            if 'key' in user_data:
                logger.info("-" * 80)
                logger.info(f"Authentication Token: {user_data['key']}")

            # Log college information
            if 'college_id' in user_data:
                logger.info("-" * 80)
                logger.info(f"Primary College ID: {user_data['college_id']}")

            if 'accessible_colleges' in user_data:
                logger.info("Accessible Colleges:")
                for college in user_data['accessible_colleges']:
                    logger.info(f"  - {college}")

            logger.info("=" * 80)

        return response


# ============================================================================
# USER VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List all users",
        description="Retrieve a paginated list of all users in the current college context.",
        parameters=[
            OpenApiParameter(
                name='X-College-ID',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.HEADER,
                description='College identifier',
                required=True
            ),
            OpenApiParameter(
                name='user_type',
                type=OpenApiTypes.STR,
                description='Filter by user type (teacher, student, etc.)'
            ),
            OpenApiParameter(
                name='is_active',
                type=OpenApiTypes.BOOL,
                description='Filter by active status'
            ),
            OpenApiParameter(
                name='is_verified',
                type=OpenApiTypes.BOOL,
                description='Filter by verification status'
            ),
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                description='Search by username, email, name'
            ),
        ],
        responses={200: UserListSerializer(many=True)},
        tags=['Users']
    ),
    retrieve=extend_schema(
        summary="Get user details",
        description="Retrieve detailed information about a specific user.",
        responses={200: UserSerializer},
        tags=['Users']
    ),
    create=extend_schema(
        summary="Create new user",
        description="Create a new user account. Password will be hashed automatically.",
        request=UserCreateSerializer,
        responses={201: UserSerializer},
        tags=['Users']
    ),
    update=extend_schema(
        summary="Update user",
        description="Update all fields of a user.",
        request=UserSerializer,
        responses={200: UserSerializer},
        tags=['Users']
    ),
    partial_update=extend_schema(
        summary="Partially update user",
        description="Update specific fields of a user.",
        request=UserUpdateSerializer,
        responses={200: UserSerializer},
        tags=['Users']
    ),
    destroy=extend_schema(
        summary="Delete user",
        description="Soft delete a user (sets is_active=False).",
        responses={204: None},
        tags=['Users']
    ),
)
class UserViewSet(CollegeScopedModelViewSet):
    """
    ViewSet for managing users in the college-scoped system.

    Provides CRUD operations and custom actions for user management.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user_type', 'is_active', 'is_verified', 'is_staff', 'college', 'gender']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone']
    ordering_fields = ['username', 'email', 'date_joined', 'last_login']
    ordering = ['-date_joined']

    def get_queryset(self):
        """Add select_related for teacher_profile and student_profile."""
        queryset = super().get_queryset()
        return queryset.select_related('teacher_profile', 'student_profile', 'college')

    def get_serializer_class(self):
        """Use different serializers for different actions."""
        if self.action == 'list':
            return UserListSerializer
        if self.action == 'create':
            return UserCreateSerializer
        if self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        if self.action == 'change_password':
            return CustomPasswordChangeSerializer
        return UserSerializer

    def perform_destroy(self, instance):
        """Soft delete instead of hard delete."""
        instance.is_active = False
        instance.save(update_fields=['is_active', 'updated_at'])

    @extend_schema(
        summary="Get current user profile",
        description="Retrieve the profile of the currently authenticated user.",
        responses={200: UserSerializer},
        tags=['Users']
    )
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's profile."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @extend_schema(
        summary="Change password",
        description="Change the password for the current user.",
        request=CustomPasswordChangeSerializer,
        tags=['Users']
    )
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change password for current user."""
        serializer = CustomPasswordChangeSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.last_password_change = timezone.now()
        user.save(update_fields=['password', 'last_password_change'])

        return Response({'message': 'Password changed successfully'})

    @extend_schema(
        summary="Bulk delete users",
        description="Soft delete multiple users at once.",
        request=UserBulkDeleteSerializer,
        tags=['Users']
    )
    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        """Soft delete multiple users."""
        serializer = UserBulkDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ids = serializer.validated_data['ids']
        users = self.get_queryset().filter(id__in=ids)
        count = users.count()

        users.update(is_active=False, updated_at=timezone.now())

        return Response({
            'message': f'{count} users deleted successfully',
            'deleted_ids': ids
        })

    @extend_schema(
        summary="Bulk activate/deactivate users",
        description="Activate or deactivate multiple users at once.",
        request=UserBulkActivateSerializer,
        tags=['Users']
    )
    @action(detail=False, methods=['post'])
    def bulk_activate(self, request):
        """Bulk activate or deactivate users."""
        serializer = UserBulkActivateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ids = serializer.validated_data['ids']
        is_active = serializer.validated_data['is_active']

        users = self.get_queryset().filter(id__in=ids)
        count = users.count()

        users.update(is_active=is_active, updated_at=timezone.now())

        action_word = 'activated' if is_active else 'deactivated'
        return Response({
            'message': f'{count} users {action_word} successfully',
            'updated_ids': ids
        })

    @extend_schema(
        summary="Bulk update user types",
        description="Update user type for multiple users at once.",
        request=BulkUserTypeUpdateSerializer,
        tags=['Users']
    )
    @action(detail=False, methods=['post'])
    def bulk_update_type(self, request):
        """Bulk update user types."""
        serializer = BulkUserTypeUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ids = serializer.validated_data['ids']
        user_type = serializer.validated_data['user_type']

        users = self.get_queryset().filter(id__in=ids)
        count = users.count()

        users.update(user_type=user_type, updated_at=timezone.now())

        return Response({
            'message': f'{count} users updated to {user_type}',
            'updated_ids': ids
        })

    @extend_schema(
        summary="Get users by type",
        description="Filter users by user type (teachers, students, etc.).",
        parameters=[
            OpenApiParameter(
                name='type',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description='User type filter',
                required=True
            )
        ],
        responses={200: UserListSerializer(many=True)},
        tags=['Users']
    )
    @action(detail=False, methods=['get'], url_path='by-type/(?P<type>[^/.]+)')
    def by_type(self, request, type=None):
        """Get users filtered by type."""
        users = self.get_queryset().filter(user_type=type, is_active=True)
        serializer = UserListSerializer(users, many=True)
        return Response(serializer.data)


# ============================================================================
# ROLE VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List all roles",
        description="Retrieve all roles for the current college.",
        parameters=[
            OpenApiParameter(name='is_active', type=OpenApiTypes.BOOL, description='Filter by active status'),
            OpenApiParameter(name='search', type=OpenApiTypes.STR, description='Search by name or code'),
        ],
        responses={200: RoleListSerializer(many=True)},
        tags=['Roles']
    ),
    retrieve=extend_schema(
        summary="Get role details",
        responses={200: RoleSerializer},
        tags=['Roles']
    ),
    create=extend_schema(
        summary="Create role",
        request=RoleSerializer,
        responses={201: RoleSerializer},
        tags=['Roles']
    ),
    update=extend_schema(
        summary="Update role",
        request=RoleSerializer,
        responses={200: RoleSerializer},
        tags=['Roles']
    ),
    partial_update=extend_schema(
        summary="Partially update role",
        request=RoleSerializer,
        responses={200: RoleSerializer},
        tags=['Roles']
    ),
    destroy=extend_schema(
        summary="Delete role",
        responses={204: None},
        tags=['Roles']
    ),
)
class RoleViewSet(CollegeScopedModelViewSet):
    """ViewSet for managing roles."""
    queryset = Role.objects.all_colleges()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'college']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'display_order']
    ordering = ['display_order', 'name']

    def get_serializer_class(self):
        """Use different serializers for different actions."""
        if self.action == 'list':
            return RoleListSerializer
        return RoleSerializer

    def perform_destroy(self, instance):
        """Soft delete instead of hard delete."""
        instance.soft_delete()


    @extend_schema(
        summary="Get hierarchical role tree",
        description="Return full role hierarchy as a nested tree.",
        responses={200: OpenApiTypes.OBJECT},
        tags=['Roles']
    )
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Get hierarchical role tree."""
        roots = self.get_queryset().filter(parent__isnull=True).order_by('display_order', 'name')
        serializer = RoleTreeSerializer(roots, many=True)
        return Response({'tree': serializer.data})

    @extend_schema(
        summary="Add child role",
        description="Create a new role as a child of the given role.",
        request=RoleSerializer,
        responses={201: RoleSerializer},
        tags=['Roles']
    )
    @action(detail=True, methods=['post'])
    def add_child(self, request, pk=None):
        """Add child role to this role."""
        parent_role = self.get_object()
        serializer = RoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(parent=parent_role, **self._college_save_kwargs(serializer, include_created=True))
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Get team members for role",
        description="Get users under this role based on hierarchy.",
        responses={200: OpenApiTypes.OBJECT},
        tags=['Roles']
    )
    @action(detail=True, methods=['get'])
    def team_members(self, request, pk=None):
        """Get all team members under this role."""
        role = self.get_object()
        assignments = role.get_team_members()
        members = []
        for assignment in assignments:
            members.append({
                'user_id': assignment.user_id,
                'name': assignment.user.get_full_name(),
                'role': assignment.role.name,
                'level': assignment.role.level,
            })
        return Response({
            'role': role.name,
            'team_members': members,
            'total': len(members)
        })

    @extend_schema(
        summary="Get role hierarchy path",
        description="Get the ancestor chain from root to this role.",
        responses={200: OpenApiTypes.OBJECT},
        tags=['Roles']
    )
    @action(detail=True, methods=['get'])
    def hierarchy_path(self, request, pk=None):
        """Get ancestors path from root to this role."""
        role = self.get_object()
        ancestors = role.get_ancestors(include_self=True)
        path_data = [{
            'id': item.id,
            'name': item.name,
            'level': item.level
        } for item in sorted(ancestors, key=lambda r: r.level)]
        return Response({'path': path_data})

    @extend_schema(
        summary="Get role descendants",
        description="Get all descendant roles under this role.",
        responses={200: OpenApiTypes.OBJECT},
        tags=['Roles']
    )
    @action(detail=True, methods=['get'])
    def descendants(self, request, pk=None):
        """Get all descendants for this role."""
        role = self.get_object()
        descendants = role.get_descendants(include_self=False)
        data = [{
            'id': item.id,
            'name': item.name,
            'code': item.code,
            'level': item.level,
            'parent': item.parent_id
        } for item in descendants]
        return Response({
            'role': role.name,
            'descendants': data,
            'total': len(data)
        })


# ============================================================================
# USER ROLE VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List user role assignments",
        description="Retrieve all user-role assignments.",
        parameters=[
            OpenApiParameter(name='user', type=OpenApiTypes.UUID, description='Filter by user ID'),
            OpenApiParameter(name='role', type=OpenApiTypes.INT, description='Filter by role ID'),
            OpenApiParameter(name='college', type=OpenApiTypes.INT, description='Filter by college ID'),
        ],
        responses={200: UserRoleSerializer(many=True)},
        tags=['User Roles']
    ),
    retrieve=extend_schema(
        summary="Get user role assignment details",
        responses={200: UserRoleSerializer},
        tags=['User Roles']
    ),
    create=extend_schema(
        summary="Create user role assignment",
        request=UserRoleSerializer,
        responses={201: UserRoleSerializer},
        tags=['User Roles']
    ),
    update=extend_schema(
        summary="Update user role assignment",
        request=UserRoleSerializer,
        responses={200: UserRoleSerializer},
        tags=['User Roles']
    ),
    partial_update=extend_schema(
        summary="Partially update user role assignment",
        request=UserRoleSerializer,
        responses={200: UserRoleSerializer},
        tags=['User Roles']
    ),
    destroy=extend_schema(
        summary="Delete user role assignment",
        responses={204: None},
        tags=['User Roles']
    ),
)
class UserRoleViewSet(CollegeScopedModelViewSet):
    """ViewSet for managing user role assignments."""
    queryset = UserRole.objects.all_colleges()
    serializer_class = UserRoleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['user', 'role', 'college', 'is_active']
    ordering_fields = ['assigned_at']
    ordering = ['-assigned_at']

    def perform_destroy(self, instance):
        """Soft delete instead of hard delete."""
        instance.soft_delete()


# ============================================================================
# DEPARTMENT VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List all departments",
        description="Retrieve all departments for the current college.",
        parameters=[
            OpenApiParameter(name='is_active', type=OpenApiTypes.BOOL, description='Filter by active status'),
            OpenApiParameter(name='search', type=OpenApiTypes.STR, description='Search by name or code'),
        ],
        responses={200: DepartmentListSerializer(many=True)},
        tags=['Departments']
    ),
    retrieve=extend_schema(
        summary="Get department details",
        responses={200: DepartmentSerializer},
        tags=['Departments']
    ),
    create=extend_schema(
        summary="Create department",
        request=DepartmentSerializer,
        responses={201: DepartmentSerializer},
        tags=['Departments']
    ),
    update=extend_schema(
        summary="Update department",
        request=DepartmentSerializer,
        responses={200: DepartmentSerializer},
        tags=['Departments']
    ),
    partial_update=extend_schema(
        summary="Partially update department",
        request=DepartmentSerializer,
        responses={200: DepartmentSerializer},
        tags=['Departments']
    ),
    destroy=extend_schema(
        summary="Delete department",
        responses={204: None},
        tags=['Departments']
    ),
)
class DepartmentViewSet(CollegeScopedModelViewSet):
    """ViewSet for managing departments."""
    queryset = Department.objects.all_colleges()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'college', 'hod']
    search_fields = ['name', 'code', 'short_name', 'description']
    ordering_fields = ['name', 'display_order']
    ordering = ['display_order', 'name']

    def get_serializer_class(self):
        """Use different serializers for different actions."""
        if self.action == 'list':
            return DepartmentListSerializer
        return DepartmentSerializer

    def perform_destroy(self, instance):
        """Soft delete instead of hard delete."""
        instance.soft_delete()


# ============================================================================
# USER PROFILE VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List user profiles",
        description="Retrieve all user profiles.",
        parameters=[
            OpenApiParameter(name='user', type=OpenApiTypes.UUID, description='Filter by user ID'),
            OpenApiParameter(name='department', type=OpenApiTypes.INT, description='Filter by department ID'),
        ],
        responses={200: UserProfileSerializer(many=True)},
        tags=['User Profiles']
    ),
    retrieve=extend_schema(
        summary="Get user profile details",
        responses={200: UserProfileSerializer},
        tags=['User Profiles']
    ),
    create=extend_schema(
        summary="Create user profile",
        request=UserProfileSerializer,
        responses={201: UserProfileSerializer},
        tags=['User Profiles']
    ),
    update=extend_schema(
        summary="Update user profile",
        request=UserProfileSerializer,
        responses={200: UserProfileSerializer},
        tags=['User Profiles']
    ),
    partial_update=extend_schema(
        summary="Partially update user profile",
        request=UserProfileSerializer,
        responses={200: UserProfileSerializer},
        tags=['User Profiles']
    ),
    destroy=extend_schema(
        summary="Delete user profile",
        responses={204: None},
        tags=['User Profiles']
    ),
)
class UserProfileViewSet(CollegeScopedModelViewSet):
    """ViewSet for managing user profiles."""
    queryset = UserProfile.objects.all_colleges()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'department', 'college', 'is_active']
    search_fields = ['user__username', 'user__email', 'city', 'state']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Return all profiles for superuser, college-scoped for others"""
        if self.request.user.is_superuser:
            return UserProfile.objects.all()
        return super().get_queryset()

    def perform_destroy(self, instance):
        """Soft delete instead of hard delete."""
        instance.soft_delete()

    @extend_schema(
        summary="Get current user's profile",
        description="Retrieve the profile of the currently authenticated user.",
        responses={200: UserProfileSerializer},
        tags=['User Profiles']
    )
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get or create current user's profile."""
        if not request.user.college_id:
            return Response(
                {'error': 'User has no college assigned'},
                status=status.HTTP_400_BAD_REQUEST
            )

        profile, created = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={'college_id': request.user.college_id}
        )

        if profile.college_id != request.user.college_id:
            profile.college_id = request.user.college_id
            profile.save(update_fields=['college', 'updated_at'])

        serializer = self.get_serializer(profile)
        return Response(serializer.data)
