from rest_framework import serializers


# ==================== Academic Statistics Serializers ====================

class GradeDistributionSerializer(serializers.Serializer):
    """Grade distribution data"""
    grade = serializers.CharField()
    count = serializers.IntegerField()
    percentage = serializers.FloatField()


class TopPerformerSerializer(serializers.Serializer):
    """Top performing student data"""
    student_id = serializers.IntegerField()
    admission_number = serializers.CharField()
    student_name = serializers.CharField()
    percentage = serializers.FloatField()
    grade = serializers.CharField()
    rank = serializers.IntegerField()


class AcademicPerformanceStatsSerializer(serializers.Serializer):
    """Academic performance statistics"""
    total_students = serializers.IntegerField()
    total_exams_conducted = serializers.IntegerField()
    average_percentage = serializers.FloatField()
    pass_percentage = serializers.FloatField()
    pass_count = serializers.IntegerField()
    fail_count = serializers.IntegerField()
    grade_distribution = GradeDistributionSerializer(many=True)
    top_performers = TopPerformerSerializer(many=True)


class DailyAttendanceTrendSerializer(serializers.Serializer):
    """Daily attendance trend data"""
    date = serializers.DateField()
    total = serializers.IntegerField()
    present = serializers.IntegerField()
    absent = serializers.IntegerField()
    late = serializers.IntegerField()
    attendance_rate = serializers.FloatField()


class AttendanceStatsSerializer(serializers.Serializer):
    """Attendance statistics"""
    total_records = serializers.IntegerField()
    present_count = serializers.IntegerField()
    absent_count = serializers.IntegerField()
    late_count = serializers.IntegerField()
    leave_count = serializers.IntegerField()
    attendance_rate = serializers.FloatField()
    chronic_absentees_count = serializers.IntegerField()
    perfect_attendance_count = serializers.IntegerField()
    daily_trend = DailyAttendanceTrendSerializer(many=True)


class AssignmentStatsSerializer(serializers.Serializer):
    """Assignment statistics"""
    total_assignments = serializers.IntegerField()
    total_submissions = serializers.IntegerField()
    submitted_count = serializers.IntegerField()
    pending_count = serializers.IntegerField()
    graded_count = serializers.IntegerField()
    late_submissions = serializers.IntegerField()
    submission_rate = serializers.FloatField()
    average_marks = serializers.FloatField()
    completion_rate = serializers.FloatField()


class SubjectWisePerformanceSerializer(serializers.Serializer):
    """Subject-wise performance data"""
    subject_id = serializers.IntegerField()
    subject_name = serializers.CharField()
    subject_code = serializers.CharField()
    average_marks = serializers.FloatField()
    pass_percentage = serializers.FloatField()
    total_students = serializers.IntegerField()


class AcademicStatsSerializer(serializers.Serializer):
    """Combined academic statistics"""
    performance = AcademicPerformanceStatsSerializer()
    attendance = AttendanceStatsSerializer()
    assignments = AssignmentStatsSerializer()
    subject_wise_performance = SubjectWisePerformanceSerializer(many=True)
    generated_at = serializers.DateTimeField()


# ==================== Financial Statistics Serializers ====================

class PaymentMethodDistributionSerializer(serializers.Serializer):
    """Payment method distribution"""
    payment_method = serializers.CharField()
    count = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    percentage = serializers.FloatField()


class MonthlyRevenueSerializer(serializers.Serializer):
    """Monthly revenue trend"""
    month = serializers.CharField()
    year = serializers.IntegerField()
    total_collected = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_due = serializers.DecimalField(max_digits=12, decimal_places=2)
    collection_rate = serializers.FloatField()


class FeeCollectionStatsSerializer(serializers.Serializer):
    """Fee collection statistics"""
    total_students = serializers.IntegerField()
    total_fee_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_collected = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_outstanding = serializers.DecimalField(max_digits=12, decimal_places=2)
    collection_rate = serializers.FloatField()
    defaulters_count = serializers.IntegerField()
    fully_paid_count = serializers.IntegerField()
    payment_method_distribution = PaymentMethodDistributionSerializer(many=True)
    monthly_trend = MonthlyRevenueSerializer(many=True)


class CategoryWiseExpenseSerializer(serializers.Serializer):
    """Category-wise expense breakdown"""
    category_id = serializers.IntegerField()
    category_name = serializers.CharField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    transaction_count = serializers.IntegerField()
    percentage = serializers.FloatField()


class ExpenseStatsSerializer(serializers.Serializer):
    """Expense statistics"""
    total_expenses = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_transactions = serializers.IntegerField()
    average_expense = serializers.DecimalField(max_digits=12, decimal_places=2)
    category_breakdown = CategoryWiseExpenseSerializer(many=True)


class IncomeStatsSerializer(serializers.Serializer):
    """Income statistics"""
    total_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_transactions = serializers.IntegerField()
    average_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    category_breakdown = CategoryWiseExpenseSerializer(many=True)


class FinancialStatsSerializer(serializers.Serializer):
    """Combined financial statistics"""
    fee_collection = FeeCollectionStatsSerializer()
    expenses = ExpenseStatsSerializer()
    income = IncomeStatsSerializer()
    net_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    generated_at = serializers.DateTimeField()


# ==================== Library Statistics Serializers ====================

class PopularBookSerializer(serializers.Serializer):
    """Popular book data"""
    book_id = serializers.IntegerField()
    title = serializers.CharField()
    author = serializers.CharField()
    isbn = serializers.CharField(required=False, allow_null=True)
    issue_count = serializers.IntegerField()
    category = serializers.CharField()


class LibraryCirculationStatsSerializer(serializers.Serializer):
    """Library circulation statistics"""
    total_books = serializers.IntegerField()
    available_books = serializers.IntegerField()
    issued_books = serializers.IntegerField()
    total_issues = serializers.IntegerField()
    total_returns = serializers.IntegerField()
    overdue_books = serializers.IntegerField()
    total_fines_collected = serializers.DecimalField(max_digits=10, decimal_places=2)
    outstanding_fines = serializers.DecimalField(max_digits=10, decimal_places=2)
    popular_books = PopularBookSerializer(many=True)
    active_members = serializers.IntegerField()


# ==================== HR Statistics Serializers ====================

class LeaveTypeDistributionSerializer(serializers.Serializer):
    """Leave type distribution"""
    leave_type = serializers.CharField()
    approved_count = serializers.IntegerField()
    pending_count = serializers.IntegerField()
    rejected_count = serializers.IntegerField()
    total_days = serializers.IntegerField()


class LeaveStatsSerializer(serializers.Serializer):
    """Leave statistics"""
    total_applications = serializers.IntegerField()
    approved_count = serializers.IntegerField()
    pending_count = serializers.IntegerField()
    rejected_count = serializers.IntegerField()
    total_leave_days = serializers.IntegerField()
    approval_rate = serializers.FloatField()
    leave_type_distribution = LeaveTypeDistributionSerializer(many=True)


class PayrollStatsSerializer(serializers.Serializer):
    """Payroll statistics"""
    total_employees = serializers.IntegerField()
    total_gross_salary = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_deductions = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_net_salary = serializers.DecimalField(max_digits=12, decimal_places=2)
    average_salary = serializers.DecimalField(max_digits=12, decimal_places=2)
    paid_count = serializers.IntegerField()
    pending_count = serializers.IntegerField()


class StaffAttendanceStatsSerializer(serializers.Serializer):
    """Staff attendance statistics"""
    total_records = serializers.IntegerField()
    present_count = serializers.IntegerField()
    absent_count = serializers.IntegerField()
    late_count = serializers.IntegerField()
    leave_count = serializers.IntegerField()
    attendance_rate = serializers.FloatField()


class HRStatsSerializer(serializers.Serializer):
    """Combined HR statistics"""
    leave = LeaveStatsSerializer()
    payroll = PayrollStatsSerializer()
    attendance = StaffAttendanceStatsSerializer()
    generated_at = serializers.DateTimeField()


# ==================== Store Statistics Serializers ====================

class PopularItemSerializer(serializers.Serializer):
    """Popular store item"""
    item_id = serializers.IntegerField()
    item_name = serializers.CharField()
    category = serializers.CharField()
    quantity_sold = serializers.IntegerField()
    revenue = serializers.DecimalField(max_digits=10, decimal_places=2)


class StoreSalesStatsSerializer(serializers.Serializer):
    """Store sales statistics"""
    total_sales = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_items_sold = serializers.IntegerField()
    average_sale_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    popular_items = PopularItemSerializer(many=True)
    cash_sales = serializers.DecimalField(max_digits=10, decimal_places=2)
    online_sales = serializers.DecimalField(max_digits=10, decimal_places=2)


class InventoryStatsSerializer(serializers.Serializer):
    """Inventory statistics"""
    total_items = serializers.IntegerField()
    low_stock_items = serializers.IntegerField()
    out_of_stock_items = serializers.IntegerField()
    total_inventory_value = serializers.DecimalField(max_digits=12, decimal_places=2)


# ==================== Hostel Statistics Serializers ====================

class HostelOccupancyStatsSerializer(serializers.Serializer):
    """Hostel occupancy statistics"""
    total_hostels = serializers.IntegerField()
    total_rooms = serializers.IntegerField()
    total_beds = serializers.IntegerField()
    occupied_beds = serializers.IntegerField()
    vacant_beds = serializers.IntegerField()
    occupancy_rate = serializers.FloatField()
    total_students = serializers.IntegerField()


class HostelFeeStatsSerializer(serializers.Serializer):
    """Hostel fee statistics"""
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    collected_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    outstanding_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    collection_rate = serializers.FloatField()


# ==================== Communication Statistics Serializers ====================

class MessageDeliveryStatsSerializer(serializers.Serializer):
    """Message delivery statistics"""
    total_messages = serializers.IntegerField()
    sent_count = serializers.IntegerField()
    delivered_count = serializers.IntegerField()
    failed_count = serializers.IntegerField()
    pending_count = serializers.IntegerField()
    delivery_rate = serializers.FloatField()


class EventStatsSerializer(serializers.Serializer):
    """Event statistics"""
    total_events = serializers.IntegerField()
    upcoming_events = serializers.IntegerField()
    completed_events = serializers.IntegerField()
    total_registrations = serializers.IntegerField()
    average_attendance = serializers.FloatField()


class CommunicationStatsSerializer(serializers.Serializer):
    """Combined communication statistics"""
    messages = MessageDeliveryStatsSerializer()
    events = EventStatsSerializer()
    generated_at = serializers.DateTimeField()


# ==================== Dashboard Overview Serializer ====================

class DashboardStatsSerializer(serializers.Serializer):
    """Complete dashboard statistics overview"""
    # Quick stats
    total_students = serializers.IntegerField()
    total_teachers = serializers.IntegerField()
    total_staff = serializers.IntegerField()
    active_classes = serializers.IntegerField()

    # Today's stats
    today_student_attendance_rate = serializers.FloatField()
    today_staff_attendance_rate = serializers.FloatField()
    today_present_students = serializers.IntegerField()
    today_absent_students = serializers.IntegerField()

    # Financial summary
    total_fee_collected_this_month = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_fee_outstanding = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_expenses_this_month = serializers.DecimalField(max_digits=12, decimal_places=2)

    # Academic summary
    average_student_performance = serializers.FloatField()
    upcoming_exams = serializers.IntegerField()
    pending_assignments = serializers.IntegerField()

    # Library summary
    books_issued_today = serializers.IntegerField()
    overdue_books = serializers.IntegerField()

    # Recent activity counts
    recent_admissions = serializers.IntegerField()
    recent_fee_payments = serializers.IntegerField()

    generated_at = serializers.DateTimeField()


# ==================== Student Personal Statistics Serializers ====================

class StudentInfoSerializer(serializers.Serializer):
    """Student basic information"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    admission_number = serializers.CharField()
    class_name = serializers.CharField(source='class')
    roll_number = serializers.CharField()


class StudentAttendanceStatsSerializer(serializers.Serializer):
    """Student personal attendance stats"""
    total_days = serializers.IntegerField()
    present_days = serializers.IntegerField()
    absent_days = serializers.IntegerField()
    late_days = serializers.IntegerField()
    attendance_percentage = serializers.FloatField()


class StudentAcademicStatsSerializer(serializers.Serializer):
    """Student academic performance stats"""
    total_exams = serializers.IntegerField()
    average_percentage = serializers.FloatField()
    latest_grade = serializers.CharField()
    latest_percentage = serializers.FloatField()


class StudentAssignmentStatsSerializer(serializers.Serializer):
    """Student assignment stats"""
    total_assignments = serializers.IntegerField()
    submitted = serializers.IntegerField()
    pending = serializers.IntegerField()
    average_marks = serializers.FloatField()


class StudentFeeStatsSerializer(serializers.Serializer):
    """Student fee stats"""
    total_fee = serializers.DecimalField(max_digits=10, decimal_places=2)
    paid = serializers.DecimalField(max_digits=10, decimal_places=2)
    balance = serializers.DecimalField(max_digits=10, decimal_places=2)
    payment_status = serializers.CharField()


class StudentLibraryStatsSerializer(serializers.Serializer):
    """Student library stats"""
    books_issued = serializers.IntegerField()
    overdue_books = serializers.IntegerField()


class StudentOverviewStatsSerializer(serializers.Serializer):
    """Complete student statistics"""
    student_info = StudentInfoSerializer()
    attendance = StudentAttendanceStatsSerializer()
    academic = StudentAcademicStatsSerializer()
    assignments = StudentAssignmentStatsSerializer()
    fees = StudentFeeStatsSerializer()
    library = StudentLibraryStatsSerializer()
    generated_at = serializers.DateTimeField()


# ==================== Teacher Personal Statistics Serializers ====================

class TeacherInfoSerializer(serializers.Serializer):
    """Teacher basic information"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    employee_id = serializers.CharField()
    department = serializers.CharField()


class TeacherTeachingStatsSerializer(serializers.Serializer):
    """Teacher teaching stats"""
    total_subjects = serializers.IntegerField()
    total_classes = serializers.IntegerField()
    is_class_teacher = serializers.BooleanField()
    class_teacher_of = serializers.CharField()


class TeacherAssignmentStatsSerializer(serializers.Serializer):
    """Teacher assignment stats"""
    total_created = serializers.IntegerField()
    active_assignments = serializers.IntegerField()
    total_submissions = serializers.IntegerField()
    pending_grading = serializers.IntegerField()
    graded = serializers.IntegerField()


class TeacherStudyMaterialStatsSerializer(serializers.Serializer):
    """Teacher study material stats"""
    total_uploaded = serializers.IntegerField()
    total_views = serializers.IntegerField()


class TeacherAttendanceStatsSerializer(serializers.Serializer):
    """Teacher attendance stats"""
    total_days = serializers.IntegerField()
    present_days = serializers.IntegerField()
    attendance_percentage = serializers.FloatField()


class TeacherLeaveStatsSerializer(serializers.Serializer):
    """Teacher leave stats"""
    total_applications = serializers.IntegerField()
    approved = serializers.IntegerField()
    pending = serializers.IntegerField()


class TeacherOverviewStatsSerializer(serializers.Serializer):
    """Complete teacher statistics"""
    teacher_info = TeacherInfoSerializer()
    teaching = TeacherTeachingStatsSerializer()
    assignments = TeacherAssignmentStatsSerializer()
    study_materials = TeacherStudyMaterialStatsSerializer()
    attendance = TeacherAttendanceStatsSerializer()
    leave = TeacherLeaveStatsSerializer()
    generated_at = serializers.DateTimeField()
