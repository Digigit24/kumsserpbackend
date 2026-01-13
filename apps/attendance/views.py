"""
DRF ViewSets for Attendance app with comprehensive API documentation.
"""
from apps.core.cache_mixins import CachedReadOnlyMixin
from rest_framework import status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction, IntegrityError
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiResponse,
)
from drf_spectacular.types import OpenApiTypes

from .models import (
    StudentAttendance, SubjectAttendance, StaffAttendance, AttendanceNotification
)
from .serializers import (
    StudentAttendanceSerializer, StudentAttendanceListSerializer,
    SubjectAttendanceSerializer, SubjectAttendanceListSerializer,
    StaffAttendanceSerializer, StaffAttendanceListSerializer,
    AttendanceNotificationSerializer,
    BulkDeleteSerializer,
    BulkAttendanceSerializer,
    StudentWithAttendanceSerializer,
)
from apps.core.mixins import CollegeScopedModelViewSet, RelatedCollegeScopedModelViewSet


# ============================================================================
# STUDENT ATTENDANCE VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List student attendance",
        description="Retrieve student attendance records.",
        parameters=[
            OpenApiParameter(name='student', type=OpenApiTypes.INT, description='Filter by student ID'),
            OpenApiParameter(name='class_obj', type=OpenApiTypes.INT, description='Filter by class ID'),
            OpenApiParameter(name='section', type=OpenApiTypes.INT, description='Filter by section ID'),
            OpenApiParameter(name='date', type=OpenApiTypes.DATE, description='Filter by date'),
            OpenApiParameter(name='status', type=OpenApiTypes.STR, description='Filter by status'),
        ],
        responses={200: StudentAttendanceListSerializer(many=True)},
        tags=['Attendance - Students']
    ),
    retrieve=extend_schema(
        summary="Get student attendance details",
        responses={200: StudentAttendanceSerializer},
        tags=['Attendance - Students']
    ),
    create=extend_schema(
        summary="Mark student attendance",
        request=StudentAttendanceSerializer,
        responses={201: StudentAttendanceSerializer},
        tags=['Attendance - Students']
    ),
    update=extend_schema(
        summary="Update student attendance",
        request=StudentAttendanceSerializer,
        responses={200: StudentAttendanceSerializer},
        tags=['Attendance - Students']
    ),
    partial_update=extend_schema(
        summary="Partially update student attendance",
        request=StudentAttendanceSerializer,
        responses={200: StudentAttendanceSerializer},
        tags=['Attendance - Students']
    ),
    destroy=extend_schema(
        summary="Delete student attendance",
        responses={204: None},
        tags=['Attendance - Students']
    ),
)
class StudentAttendanceViewSet(CachedReadOnlyMixin, CollegeScopedModelViewSet):
    """ViewSet for managing student attendance."""
    queryset = StudentAttendance.objects.all_colleges()
    serializer_class = StudentAttendanceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student', 'class_obj', 'section', 'date', 'status', 'marked_by']
    search_fields = ['student__first_name', 'student__last_name', 'student__admission_number']
    ordering_fields = ['date', 'created_at']
    ordering = ['-date']

    def get_serializer_class(self):
        if self.action == 'list':
            return StudentAttendanceListSerializer
        return StudentAttendanceSerializer


    def get_queryset(self):
        queryset = StudentAttendance.objects.all_colleges()
        college_id = self.get_college_id(required=False)
        user = getattr(self.request, 'user', None)
        is_global_user = (
            user and (
                user.is_superuser or
                user.is_staff or
                getattr(user, 'user_type', None) == 'central_manager'
            )
        )

        if college_id == 'all' or (is_global_user and not college_id):
            return queryset

        if not college_id:
            college_id = self.get_college_id(required=True)

        return queryset.filter(class_obj__college_id=college_id)


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        defaults = {
            'class_obj': data['class_obj'],
            'section': data['section'],
            'status': data['status'],
            'remarks': data.get('remarks', ''),
            'check_in_time': data.get('check_in_time'),
            'check_out_time': data.get('check_out_time'),
            'marked_by': request.user,
        }

        try:
            with transaction.atomic():
                attendance, created = StudentAttendance.objects.all_colleges().update_or_create(
                    student=data['student'],
                    date=data['date'],
                    defaults=defaults
                )
        except IntegrityError:
            attendance = StudentAttendance.objects.all_colleges().get(
                student=data['student'],
                date=data['date']
            )
            for key, value in defaults.items():
                setattr(attendance, key, value)
            attendance.save()
            created = False

        output_serializer = self.get_serializer(attendance)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        headers = self.get_success_headers(output_serializer.data) if created else {}
        return Response(output_serializer.data, status=status_code, headers=headers)

    @extend_schema(
        summary="Bulk mark attendance",
        request=BulkAttendanceSerializer,
        responses={201: StudentAttendanceSerializer(many=True)},
        tags=['Attendance - Students']
    )
    @action(detail=False, methods=['post'])
    def bulk_mark(self, request):
        """Bulk mark attendance for multiple students."""
        serializer = BulkAttendanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        student_ids = serializer.validated_data['student_ids']
        date = serializer.validated_data['date']
        status_value = serializer.validated_data['status']
        class_obj_id = serializer.validated_data['class_obj']
        section_id = serializer.validated_data['section']
        remarks = serializer.validated_data.get('remarks', '')

        from apps.students.models import Student
        from apps.academic.models import Class, Section

        try:
            students = Student.objects.filter(id__in=student_ids)
            class_obj = Class.objects.get(id=class_obj_id)
            section = Section.objects.get(id=section_id)
        except (Class.DoesNotExist, Section.DoesNotExist) as e:
            return Response({'detail': f'Invalid class or section: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        attendance_records = []
        for student in students:
            try:
                with transaction.atomic():
                    attendance, created = StudentAttendance.objects.all_colleges().update_or_create(
                        student=student,
                        date=date,
                        defaults={
                            'class_obj': class_obj,
                            'section': section,
                            'status': status_value,
                            'remarks': remarks,
                            'marked_by': request.user,
                        }
                    )
            except IntegrityError:
                attendance = StudentAttendance.objects.all_colleges().get(
                    student=student,
                    date=date
                )
                attendance.class_obj = class_obj
                attendance.section = section
                attendance.status = status_value
                attendance.remarks = remarks
                attendance.marked_by = request.user
                attendance.save()

            attendance_records.append(attendance)

        output_serializer = StudentAttendanceSerializer(attendance_records, many=True)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Get class attendance list",
        description="Get all students in a class/section with their attendance status for a specific date",
        parameters=[
            OpenApiParameter(name='class_obj', type=OpenApiTypes.INT, description='Class ID', required=True),
            OpenApiParameter(name='section', type=OpenApiTypes.INT, description='Section ID', required=True),
            OpenApiParameter(name='date', type=OpenApiTypes.DATE, description='Attendance date', required=True),
        ],
        responses={200: StudentWithAttendanceSerializer(many=True)},
        tags=['Attendance - Students']
    )
    @action(detail=False, methods=['get'])
    def class_attendance(self, request):
        """Get all students in a class/section with their attendance status for a specific date."""
        class_obj_id = request.query_params.get('class_obj')
        section_id = request.query_params.get('section')
        date = request.query_params.get('date')

        # Validate required parameters
        if not all([class_obj_id, section_id, date]):
            return Response(
                {'detail': 'class_obj, section, and date are required parameters'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from apps.students.models import Student
        from django.db.models import OuterRef, Subquery, F, Value, CharField
        from django.db.models.functions import Concat

        # Get all students in the specified class and section
        students = Student.objects.filter(
            current_class_id=class_obj_id,
            current_section_id=section_id
        ).select_related('user')

        # Apply college scoping
        college_id = self.get_college_id(required=False)
        user = getattr(request, 'user', None)
        is_global_user = (
            user and (
                user.is_superuser or
                user.is_staff or
                getattr(user, 'user_type', None) == 'central_manager'
            )
        )

        if college_id != 'all' and not (is_global_user and not college_id):
            if not college_id:
                college_id = self.get_college_id(required=True)
            students = students.filter(college_id=college_id)

        # Subquery to get attendance records for the specified date
        attendance_subquery = StudentAttendance.objects.filter(
            student_id=OuterRef('id'),
            date=date
        ).values('id', 'status', 'check_in_time', 'check_out_time', 'remarks', 'marked_by__id', 'marked_by__first_name', 'marked_by__last_name')[:1]

        # Annotate students with attendance data
        students_with_attendance = students.annotate(
            attendance_id=Subquery(attendance_subquery.values('id')),
            attendance_status=Subquery(attendance_subquery.values('status')),
            attendance_check_in=Subquery(attendance_subquery.values('check_in_time')),
            attendance_check_out=Subquery(attendance_subquery.values('check_out_time')),
            attendance_remarks=Subquery(attendance_subquery.values('remarks')),
            attendance_marked_by_id=Subquery(attendance_subquery.values('marked_by__id')),
            attendance_marked_by_fname=Subquery(attendance_subquery.values('marked_by__first_name')),
            attendance_marked_by_lname=Subquery(attendance_subquery.values('marked_by__last_name'))
        ).order_by('roll_number', 'first_name')

        # Build response data
        result = []
        for student in students_with_attendance:
            marked_by_name = None
            if student.attendance_marked_by_fname:
                marked_by_name = f"{student.attendance_marked_by_fname} {student.attendance_marked_by_lname or ''}".strip()

            result.append({
                'student_id': student.id,
                'admission_number': student.admission_number,
                'roll_number': student.roll_number,
                'student_name': student.get_full_name(),
                'attendance_id': student.attendance_id,
                'status': student.attendance_status,
                'check_in_time': student.attendance_check_in,
                'check_out_time': student.attendance_check_out,
                'remarks': student.attendance_remarks,
                'marked_by': student.attendance_marked_by_id,
                'marked_by_name': marked_by_name,
            })

        serializer = StudentWithAttendanceSerializer(result, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ============================================================================
# SUBJECT ATTENDANCE VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List subject attendance",
        description="Retrieve subject-wise attendance records.",
        parameters=[
            OpenApiParameter(name='student', type=OpenApiTypes.INT, description='Filter by student ID'),
            OpenApiParameter(name='subject_assignment', type=OpenApiTypes.INT, description='Filter by subject assignment ID'),
            OpenApiParameter(name='date', type=OpenApiTypes.DATE, description='Filter by date'),
            OpenApiParameter(name='status', type=OpenApiTypes.STR, description='Filter by status'),
        ],
        responses={200: SubjectAttendanceListSerializer(many=True)},
        tags=['Attendance - Subjects']
    ),
    retrieve=extend_schema(
        summary="Get subject attendance details",
        responses={200: SubjectAttendanceSerializer},
        tags=['Attendance - Subjects']
    ),
    create=extend_schema(
        summary="Mark subject attendance",
        request=SubjectAttendanceSerializer,
        responses={201: SubjectAttendanceSerializer},
        tags=['Attendance - Subjects']
    ),
    update=extend_schema(
        summary="Update subject attendance",
        request=SubjectAttendanceSerializer,
        responses={200: SubjectAttendanceSerializer},
        tags=['Attendance - Subjects']
    ),
    partial_update=extend_schema(
        summary="Partially update subject attendance",
        request=SubjectAttendanceSerializer,
        responses={200: SubjectAttendanceSerializer},
        tags=['Attendance - Subjects']
    ),
    destroy=extend_schema(
        summary="Delete subject attendance",
        responses={204: None},
        tags=['Attendance - Subjects']
    ),
)
class SubjectAttendanceViewSet(RelatedCollegeScopedModelViewSet):
    """ViewSet for managing subject attendance."""
    queryset = SubjectAttendance.objects.all_colleges()
    serializer_class = SubjectAttendanceSerializer
    permission_classes = [IsAuthenticated]
    related_college_lookup = 'student__college_id'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student', 'subject_assignment', 'date', 'period', 'status', 'marked_by']
    search_fields = ['student__first_name', 'student__last_name']
    ordering_fields = ['date', 'created_at']
    ordering = ['-date']

    def get_serializer_class(self):
        if self.action == 'list':
            return SubjectAttendanceListSerializer
        return SubjectAttendanceSerializer


# ============================================================================
# STAFF ATTENDANCE VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List staff attendance",
        description="Retrieve staff attendance records.",
        parameters=[
            OpenApiParameter(name='teacher', type=OpenApiTypes.INT, description='Filter by teacher ID'),
            OpenApiParameter(name='date', type=OpenApiTypes.DATE, description='Filter by date'),
            OpenApiParameter(name='status', type=OpenApiTypes.STR, description='Filter by status'),
        ],
        responses={200: StaffAttendanceListSerializer(many=True)},
        tags=['Attendance - Staff']
    ),
    retrieve=extend_schema(
        summary="Get staff attendance details",
        responses={200: StaffAttendanceSerializer},
        tags=['Attendance - Staff']
    ),
    create=extend_schema(
        summary="Mark staff attendance",
        request=StaffAttendanceSerializer,
        responses={201: StaffAttendanceSerializer},
        tags=['Attendance - Staff']
    ),
    update=extend_schema(
        summary="Update staff attendance",
        request=StaffAttendanceSerializer,
        responses={200: StaffAttendanceSerializer},
        tags=['Attendance - Staff']
    ),
    partial_update=extend_schema(
        summary="Partially update staff attendance",
        request=StaffAttendanceSerializer,
        responses={200: StaffAttendanceSerializer},
        tags=['Attendance - Staff']
    ),
    destroy=extend_schema(
        summary="Delete staff attendance",
        responses={204: None},
        tags=['Attendance - Staff']
    ),
)
class StaffAttendanceViewSet(CachedReadOnlyMixin, CollegeScopedModelViewSet):
    """ViewSet for managing staff attendance."""
    queryset = StaffAttendance.objects.all_colleges()
    serializer_class = StaffAttendanceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['teacher', 'date', 'status', 'marked_by']
    search_fields = ['teacher__first_name', 'teacher__last_name', 'teacher__employee_id']
    ordering_fields = ['date', 'created_at']
    ordering = ['-date']

    def get_serializer_class(self):
        if self.action == 'list':
            return StaffAttendanceListSerializer
        return StaffAttendanceSerializer


# ============================================================================
# ATTENDANCE NOTIFICATION VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List attendance notifications",
        description="Retrieve attendance notifications.",
        parameters=[
            OpenApiParameter(name='attendance', type=OpenApiTypes.INT, description='Filter by attendance ID'),
            OpenApiParameter(name='recipient', type=OpenApiTypes.INT, description='Filter by recipient ID'),
            OpenApiParameter(name='status', type=OpenApiTypes.STR, description='Filter by status'),
            OpenApiParameter(name='notification_type', type=OpenApiTypes.STR, description='Filter by notification type'),
        ],
        responses={200: AttendanceNotificationSerializer(many=True)},
        tags=['Attendance - Notifications']
    ),
    retrieve=extend_schema(
        summary="Get attendance notification details",
        responses={200: AttendanceNotificationSerializer},
        tags=['Attendance - Notifications']
    ),
    create=extend_schema(
        summary="Create attendance notification",
        request=AttendanceNotificationSerializer,
        responses={201: AttendanceNotificationSerializer},
        tags=['Attendance - Notifications']
    ),
    update=extend_schema(
        summary="Update attendance notification",
        request=AttendanceNotificationSerializer,
        responses={200: AttendanceNotificationSerializer},
        tags=['Attendance - Notifications']
    ),
    partial_update=extend_schema(
        summary="Partially update attendance notification",
        request=AttendanceNotificationSerializer,
        responses={200: AttendanceNotificationSerializer},
        tags=['Attendance - Notifications']
    ),
    destroy=extend_schema(
        summary="Delete attendance notification",
        responses={204: None},
        tags=['Attendance - Notifications']
    ),
)
class AttendanceNotificationViewSet(CachedReadOnlyMixin, CollegeScopedModelViewSet):
    """ViewSet for managing attendance notifications."""
    queryset = AttendanceNotification.objects.all_colleges()
    serializer_class = AttendanceNotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['attendance', 'recipient', 'status', 'notification_type', 'recipient_type']
    ordering_fields = ['sent_at', 'created_at']
    ordering = ['-created_at']
