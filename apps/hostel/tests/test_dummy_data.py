from datetime import date

from django.test import TestCase

from apps.core.models import College
from apps.core.utils import set_current_college_id, clear_current_college_id
from apps.accounts.models import User, UserType
from apps.academic.models import Faculty, Program, AcademicSession, Class, Section
from apps.core.models import AcademicYear
from apps.teachers.models import Teacher
from apps.students.models import Student
from apps.hostel.models import (
    Hostel,
    RoomType,
    Room,
    Bed,
    HostelAllocation,
    HostelFee,
)


class HostelDummyDataTest(TestCase):
    """Build a dummy hostel graph and verify relationships."""

    def setUp(self):
        self.college = College.objects.create(
            code="HOS",
            name="Hostel College",
            short_name="HOS",
            email="info@hos.test",
            phone="9999999997",
            address_line1="123 Street",
            city="City",
            state="State",
            pincode="000000",
            country="Testland",
        )
        set_current_college_id(self.college.id)

        self.year = AcademicYear.objects.create(
            college=self.college,
            year="2025-2026",
            start_date=date(2025, 6, 1),
            end_date=date(2026, 5, 31),
            is_current=True,
        )
        self.session = AcademicSession.objects.create(
            college=self.college,
            academic_year=self.year,
            name="Semester 1",
            semester=1,
            start_date=date(2025, 6, 1),
            end_date=date(2025, 11, 30),
            is_current=True,
        )
        self.faculty = Faculty.objects.create(
            college=self.college,
            code="ENG",
            name="Engineering",
            short_name="ENG",
            display_order=1,
        )
        self.program = Program.objects.create(
            college=self.college,
            faculty=self.faculty,
            code="BTECH",
            name="B.Tech",
            short_name="BTECH",
            program_type="ug",
            duration=4,
            duration_type="year",
            total_credits=160,
            display_order=1,
        )
        self.class_obj = Class.objects.create(
            college=self.college,
            program=self.program,
            academic_session=self.session,
            name="BTECH-CS Sem 1",
            semester=1,
            year=1,
            max_students=60,
        )
        self.section = Section.objects.create(
            class_obj=self.class_obj,
            name="A",
            max_students=60,
        )
        self.teacher_user = User.objects.create_user(
            username="warden_hos",
            email="warden@hos.test",
            password="dummy-pass",
            first_name="War",
            last_name="Den",
            college=self.college,
            user_type=UserType.TEACHER,
            is_active=True,
        )
        self.warden = Teacher.objects.create(
            user=self.teacher_user,
            college=self.college,
            employee_id="EMP-HOS-001",
            joining_date=date(2025, 6, 1),
            faculty=self.faculty,
            first_name="War",
            last_name="Den",
            date_of_birth=date(1990, 1, 1),
            gender="male",
            email="warden@hos.test",
            phone="7777777780",
        )
        self.student_user = User.objects.create_user(
            username="student_hos",
            email="student@hos.test",
            password="dummy-pass",
            first_name="Stu",
            last_name="Dent",
            college=self.college,
            user_type=UserType.STUDENT,
            is_active=True,
        )
        self.student = Student.objects.create(
            user=self.student_user,
            college=self.college,
            admission_number="ADM-HOS-001",
            admission_date=date(2025, 6, 1),
            admission_type="regular",
            registration_number="REG-HOS-001",
            program=self.program,
            current_class=self.class_obj,
            current_section=self.section,
            academic_year=self.year,
            first_name="Stu",
            last_name="Dent",
            date_of_birth=date(2007, 1, 1),
            gender="male",
            email="student@hos.test",
        )

        self.hostel = Hostel.objects.create(
            college=self.college,
            name="Boys Hostel",
            hostel_type="boys",
            capacity=100,
            warden=self.warden,
        )
        self.room_type = RoomType.objects.create(
            hostel=self.hostel,
            name="Double Sharing",
            capacity=2,
            monthly_fee=5000,
        )
        self.room = Room.objects.create(
            hostel=self.hostel,
            room_type=self.room_type,
            room_number="101",
            floor="1",
            capacity=2,
            occupied_beds=0,
        )
        self.bed = Bed.objects.create(
            room=self.room,
            bed_number="A",
            status="vacant",
        )
        self.allocation = HostelAllocation.objects.create(
            student=self.student,
            hostel=self.hostel,
            room=self.room,
            bed=self.bed,
            from_date=date(2025, 6, 15),
            is_current=True,
        )
        # Fee created by signal; ensure one exists
        self.fee = HostelFee.objects.first() or HostelFee.objects.create(
            allocation=self.allocation,
            month=6,
            year=2025,
            amount=self.room_type.monthly_fee,
            due_date=date(2025, 7, 1),
        )

    def tearDown(self):
        clear_current_college_id()

    def test_dummy_graph_created(self):
        self.assertEqual(College.objects.count(), 1)
        self.assertEqual(Hostel.objects.count(), 1)
        self.assertEqual(RoomType.objects.count(), 1)
        self.assertEqual(Room.objects.count(), 1)
        self.assertEqual(Bed.objects.count(), 1)
        self.assertEqual(HostelAllocation.objects.count(), 1)
        self.assertGreaterEqual(HostelFee.objects.count(), 1)

        # Relationships
        self.assertEqual(self.hostel.warden, self.warden)
        self.assertEqual(self.room.hostel, self.hostel)
        self.assertEqual(self.bed.room, self.room)
        self.assertEqual(self.allocation.bed, self.bed)
        self.assertEqual(self.allocation.student, self.student)

        # __str__ calls
        str(self.hostel)
        str(self.room_type)
        str(self.room)
        str(self.bed)
        str(self.allocation)
        str(self.fee)
