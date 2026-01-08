"""
API views for approval and notification management.
"""
from datetime import timedelta
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from rest_framework import status, generics, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter

from apps.fees.models import FeeCollection
from .models import ApprovalRequest, ApprovalAction, Notification
from .serializers import (
    ApprovalRequestSerializer,
    ApprovalRequestCreateSerializer,
    FeePaymentApprovalRequestSerializer,
    ApprovalActionSerializer,
    ApprovalActionCreateSerializer,
    ApproveRejectSerializer,
    NotificationSerializer,
    NotificationCreateSerializer,
    BulkNotificationSerializer,
    NotificationMarkReadSerializer,
)


class ApprovalRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing approval requests.
    Provides CRUD operations and custom actions for approval workflow.
    """
    queryset = ApprovalRequest.objects.all()
    serializer_class = ApprovalRequestSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'request_type', 'priority', 'requester']
    search_fields = ['title', 'description']
    ordering_fields = ['submitted_at', 'deadline', 'priority']
    ordering = ['-submitted_at']

    def get_queryset(self):
        """Filter based on user role."""
        user = self.request.user
        queryset = super().get_queryset()

        # Filter by college if available
        college = None
        if hasattr(user, 'college') and user.college:
            college = user.college
        elif hasattr(user, 'student_profile') and user.student_profile:
            college = user.student_profile.college
        elif hasattr(user, 'teacher_profile') and user.teacher_profile:
            college = user.teacher_profile.college

        if college:
            queryset = queryset.filter(college=college)

        # Filter based on user role
        if self.action in ['my_requests']:
            # Requests made by the current user
            queryset = queryset.filter(requester=user)
        elif self.action in ['pending_approvals']:
            # Requests that need approval from current user
            queryset = queryset.filter(approvers=user, status='pending')

        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return ApprovalRequestCreateSerializer
        return ApprovalRequestSerializer

    @extend_schema(
        description="Get approval requests made by the current user",
        responses={200: ApprovalRequestSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def my_requests(self, request):
        """Get all approval requests made by the current user."""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        description="Get pending approval requests that need current user's approval",
        responses={200: ApprovalRequestSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def pending_approvals(self, request):
        """Get pending approvals for the current user."""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        description="Get all store-related approval requests (indents, procurement, inspections) for college admin",
        responses={200: ApprovalRequestSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def store_requests(self, request):
        """Get all store-related approval requests for college admin."""
        store_types = ['store_indent', 'procurement_requirement', 'goods_inspection']
        queryset = self.filter_queryset(
            self.get_queryset().filter(request_type__in=store_types)
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        description="Get pending store-related approval requests for college admin",
        responses={200: ApprovalRequestSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def pending_store_requests(self, request):
        """Get pending store-related approval requests for college admin."""
        store_types = ['store_indent', 'procurement_requirement', 'goods_inspection']
        queryset = self.filter_queryset(
            self.get_queryset().filter(
                request_type__in=store_types,
                status='pending'
            )
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=ApproveRejectSerializer,
        description="Approve or reject an approval request",
        responses={200: ApprovalRequestSerializer}
    )
    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        """Approve or reject an approval request."""
        approval_request = ApprovalRequest.objects.filter(pk=pk).first()
        if not approval_request:
            approval_request = ApprovalRequest.objects.filter(
                request_type='procurement_requirement',
                object_id=pk
            ).first()
        if not approval_request:
            return Response(
                {'error': 'No approval request match'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ApproveRejectSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Check if user is an approver
        if request.user not in approval_request.approvers.all():
            return Response(
                {'error': 'You are not authorized to review this request'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if already reviewed
        if approval_request.status != 'pending':
            return Response(
                {'error': f'Request is already {approval_request.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        action_type = serializer.validated_data['action']
        comment = serializer.validated_data.get('comment', '')

        # Get IP address
        ip_address = self.request.META.get('REMOTE_ADDR')

        # Create approval action
        approval_action = ApprovalAction.objects.create(
            approval_request=approval_request,
            actor=request.user,
            action=action_type,
            comment=comment,
            ip_address=ip_address
        )

        # Update approval request status
        if action_type == 'approve':
            approval_request.approve(request.user)
        else:  # reject
            approval_request.reject(request.user, comment)

        # Create notification for requester
        Notification.objects.create(
            recipient=approval_request.requester,
            notification_type=f'approval_{action_type}d',
            title=f'Your {approval_request.get_request_type_display()} request has been {action_type}d',
            message=f'Your request "{approval_request.title}" has been {action_type}d by {request.user.get_full_name() or request.user.username}.' + (f'\n\nComment: {comment}' if comment else ''),
            priority='high',
            content_type=ContentType.objects.get_for_model(approval_request),
            object_id=approval_request.id,
            action_url=f'/approvals/{approval_request.id}'
        )

        response_serializer = self.get_serializer(approval_request)
        return Response(response_serializer.data)


class FeePaymentApprovalView(APIView):
    """
    API endpoint for creating fee payment approval requests.
    Students submit fee payments which create approval requests for teachers/admins.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=FeePaymentApprovalRequestSerializer,
        description="Submit a fee payment for approval",
        responses={201: ApprovalRequestSerializer}
    )
    def post(self, request):
        """Create a fee payment approval request."""
        serializer = FeePaymentApprovalRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        fee_collection_id = serializer.validated_data['fee_collection_id']
        approver_ids = serializer.validated_data['approver_ids']
        deadline_hours = serializer.validated_data.get('deadline_hours')
        priority = serializer.validated_data.get('priority', 'medium')
        attachment = serializer.validated_data.get('attachment')

        # Validate fee collection exists
        try:
            fee_collection = FeeCollection.objects.get(id=fee_collection_id)
        except FeeCollection.DoesNotExist:
            return Response(
                {'error': 'Fee collection not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Validate approvers exist
        from django.contrib.auth import get_user_model
        User = get_user_model()
        approvers = User.objects.filter(id__in=approver_ids)
        if approvers.count() != len(approver_ids):
            return Response(
                {'error': 'One or more approvers not found'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if approval request already exists for this fee collection
        content_type = ContentType.objects.get_for_model(FeeCollection)
        existing_request = ApprovalRequest.objects.filter(
            content_type=content_type,
            object_id=fee_collection_id,
            status='pending'
        ).first()

        if existing_request:
            return Response(
                {'error': 'An approval request already exists for this fee payment'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Calculate deadline
        deadline = None
        if deadline_hours:
            deadline = timezone.now() + timedelta(hours=deadline_hours)

        # Create approval request
        title = serializer.validated_data.get(
            'title',

            f'Fee Payment Approval - Rs.{fee_collection.amount}'
        )
        description = serializer.validated_data.get(
            'description',
            f'Fee payment of Rs.{fee_collection.amount} on {fee_collection.payment_date}'
        )

        # Determine college - prioritize from fee_collection, fallback to user's profile
        college = None
        if hasattr(fee_collection, 'student') and fee_collection.student:
            college = fee_collection.student.college
        elif hasattr(request.user, 'student_profile') and request.user.student_profile:
            college = request.user.student_profile.college
        elif hasattr(request.user, 'teacher_profile') and request.user.teacher_profile:
            college = request.user.teacher_profile.college
        elif hasattr(request.user, 'college'):
            college = request.user.college

        if not college:
            return Response(
                {'error': 'Unable to determine college for this approval request'},
                status=status.HTTP_400_BAD_REQUEST
            )

        approval_request = ApprovalRequest.objects.create(
            college=college,
            requester=request.user,
            request_type='fee_payment',
            title=title,
            description=description,
            priority=priority,
            content_type=content_type,
            object_id=fee_collection_id,
            requires_approval_count=1,
            deadline=deadline,
            attachment=attachment,
            metadata={
                'fee_collection_id': fee_collection_id,
                'amount': str(fee_collection.amount),
                'payment_date': str(fee_collection.payment_date),
            }
        )
        approval_request.approvers.set(approvers)

        # Create notifications for approvers
        for approver in approvers:
            Notification.objects.create(
                recipient=approver,
                notification_type='approval_request',
                title='New Fee Payment Approval Request',


                priority='high',
                content_type=ContentType.objects.get_for_model(approval_request),
                object_id=approval_request.id,
                action_url=f'/approvals/{approval_request.id}'
            )

        response_serializer = ApprovalRequestSerializer(approval_request)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing notifications.
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['notification_type', 'is_read', 'priority']
    search_fields = ['title', 'message']
    ordering_fields = ['sent_at', 'priority']
    ordering = ['-sent_at']

    def get_queryset(self):
        """Filter notifications for current user."""
        return super().get_queryset().filter(recipient=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return NotificationCreateSerializer
        return NotificationSerializer

    @extend_schema(
        description="Get unread notifications for the current user",
        responses={200: NotificationSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get unread notifications."""
        queryset = self.filter_queryset(self.get_queryset().filter(is_read=False))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        description="Get count of unread notifications",
        responses={200: {'type': 'object', 'properties': {'unread_count': {'type': 'integer'}}}}
    )
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications."""
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread_count': count})

    @extend_schema(
        request=NotificationMarkReadSerializer,
        description="Mark notifications as read",
        responses={200: {'type': 'object', 'properties': {'marked_count': {'type': 'integer'}}}}
    )
    @action(detail=False, methods=['post'])
    def mark_read(self, request):
        """Mark one or more notifications as read."""
        serializer = NotificationMarkReadSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        notification_ids = serializer.validated_data.get('notification_ids')

        if notification_ids:
            # Mark specific notifications as read
            notifications = self.get_queryset().filter(id__in=notification_ids, is_read=False)
        else:
            # Mark all unread notifications as read
            notifications = self.get_queryset().filter(is_read=False)

        count = 0
        for notification in notifications:
            notification.mark_as_read()
            count += 1

        return Response({'marked_count': count})

    @extend_schema(
        description="Mark a single notification as read",
        responses={200: NotificationSerializer}
    )
    @action(detail=True, methods=['post'])
    def read(self, request, pk=None):
        """Mark a single notification as read."""
        notification = self.get_object()
        notification.mark_as_read()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)


class BulkNotificationView(APIView):
    """
    API endpoint for sending bulk notifications to multiple users.
    Only accessible to admins/teachers.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=BulkNotificationSerializer,
        description="Send bulk notifications to multiple users",
        responses={201: {'type': 'object', 'properties': {'created_count': {'type': 'integer'}}}}
    )
    def post(self, request):
        """Send bulk notifications."""
        # TODO: Add permission check for admin/teacher role

        serializer = BulkNotificationSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        recipient_ids = serializer.validated_data['recipient_ids']
        notification_type = serializer.validated_data['notification_type']
        title = serializer.validated_data['title']
        message = serializer.validated_data['message']
        priority = serializer.validated_data.get('priority', 'medium')
        action_url = serializer.validated_data.get('action_url', '')
        expires_at = serializer.validated_data.get('expires_at')

        # Validate recipients exist
        from django.contrib.auth import get_user_model
        User = get_user_model()
        recipients = User.objects.filter(id__in=recipient_ids)

        if recipients.count() != len(recipient_ids):
            return Response(
                {'error': 'One or more recipients not found'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create notifications
        notifications = []
        for recipient in recipients:
            notification = Notification.objects.create(
                recipient=recipient,
                notification_type=notification_type,
                title=title,
                message=message,
                priority=priority,
                action_url=action_url,
                expires_at=expires_at
            )
            notifications.append(notification)

        return Response(
            {'created_count': len(notifications)},
            status=status.HTTP_201_CREATED
        )
