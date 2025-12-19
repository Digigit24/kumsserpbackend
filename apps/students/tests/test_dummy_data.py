from datetime import date

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from apps.core.models import (
    College,
    AcademicYear,
    AcademicSession,
)
from apps.core.utils import set_current_college_id, clear_current_college_id
from apps.accounts.models import User, UserType
from apps.academic.models import Faculty, Program, Class, Section, Subject
from apps.students.models import (
    StudentCategory,
    StudentGroup,
    Student,
    Guardian,
    StudentGuardian,
    StudentAddress,
    StudentDocument,
    StudentMedicalRecord,
    PreviousAcademicRecord,
    StudentPromotion,
    Certificate,
    StudentIDCard,
)


class StudentDummyDataTest(TestCase):
    """Build a dummy student graph and ensure creation succeeds."""

    def setUp(self):
        self.college = College.objects.create(
            code="STD",
            name="Student College",
            short_name="STD",
            email="info@student.test",
            phone="9999999990",
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
        self.class_from = Class.objects.create(
            college=self.college,
            program=self.program,
            academic_session=self.session,
            name="BTECH-CS Sem 1",
            semester=1,
            year=1,
            max_students=60,
        )
        self.class_to = Class.objects.create(
            college=self.college,
            program=self.program,
            academic_session=self.session,
            name="BTECH-CS Sem 2",
            semester=2,
            year=1,
            max_students=60,
        )
        self.section_a = Section.objects.create(
            class_obj=self.class_from,
            name="A",
            max_students=60,
        )
        self.section_b = Section.objects.create(
            class_obj=self.class_to,
            name="B",
            max_students=60,
        )
        self.subject = Subject.objects.create(
            college=self.college,
            code="MATH101",
            name="Maths",
            short_name="MATH",
            subject_type="theory",
            credits="4.00",
            theory_hours=4,
            practical_hours=0,
            max_marks=100,
            pass_marks=40,
        )
        self.category = StudentCategory.objects.create(
            college=self.college,
            name="General",
            code="GEN",
        )
        self.group = StudentGroup.objects.create(
            college=self.college,
            name="Morning Batch",
        )
        self.student_user = User.objects.create_user(
            username="student_dummy",
            email="student@std.test",
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
            admission_number="ADM001",
            admission_date=date(2025, 6, 1),
            admission_type="regular",
            registration_number="REG001",
            program=self.program,
            current_class=self.class_from,
            current_section=self.section_a,
            academic_year=self.year,
            category=self.category,
            group=self.group,
            first_name="Stu",
            last_name="Dent",
            date_of_birth=date(2007, 1, 1),
            gender="male",
            email="student@std.test",
        )
        self.guardian = Guardian.objects.create(
            first_name="Parent",
            last_name="One",
            relation="father",
            phone="8888888888",
        )
        self.student_guardian = StudentGuardian.objects.create(
            student=self.student,
            guardian=self.guardian,
            is_primary=True,
            is_emergency_contact=True,
        )
        self.address = StudentAddress.objects.create(
            student=self.student,
            address_type="permanent",
            address_line1="Home 1",
            city="City",
            state="State",
            pincode="000000",
        )
        self.document = StudentDocument.objects.create(
            student=self.student,
            document_type="aadhar",
            document_name="Aadhar Card",
            document_file=SimpleUploadedFile("aadhar.pdf", b"dummy"),
        )
        self.medical = StudentMedicalRecord.objects.get(student=self.student)
        self.prev_record = PreviousAcademicRecord.objects.create(
            student=self.student,
            level="10th",
            institution_name="Test School",
            board_university="Board",
            year_of_passing=2023,
            percentage=88.5,
        )
        self.promotion = StudentPromotion.objects.create(
            student=self.student,
            from_class=self.class_from,
            to_class=self.class_to,
            from_section=self.section_a,
            to_section=self.section_b,
            promotion_date=date(2025, 12, 1),
            academic_year=self.year,
            remarks="Promoted",
        )
        self.certificate = Certificate.objects.create(
            student=self.student,
            certificate_type="bonafide",
            certificate_number="CERT001",
            issue_date=date(2025, 7, 1),
        )
        self.id_card = StudentIDCard.objects.create(
            student=self.student,
            card_number="ID001",
            issue_date=date(2025, 7, 1),
            valid_until=date(2026, 6, 30),
        )

    def tearDown(self):
        clear_current_college_id()

    def test_dummy_graph_created(self):
        def count(model):
            manager = model.objects
            return manager.all_colleges().count() if hasattr(manager, "all_colleges") else manager.count()

        self.assertEqual(College.objects.count(), 1)
        self.assertEqual(count(AcademicYear), 1)
        self.assertEqual(count(AcademicSession), 1)
        self.assertEqual(count(Faculty), 1)
        self.assertEqual(count(Program), 1)
        self.assertEqual(count(Class), 2)
        self.assertEqual(Section.objects.count(), 2)
        self.assertEqual(count(Subject), 1)
        self.assertEqual(count(StudentCategory), 1)
        self.assertEqual(count(StudentGroup), 1)
        self.assertEqual(count(Student), 1)
        self.assertEqual(Guardian.objects.count(), 1)
        self.assertEqual(StudentGuardian.objects.count(), 1)
        self.assertEqual(StudentAddress.objects.count(), 1)
        self.assertEqual(StudentDocument.objects.count(), 1)
        self.assertEqual(StudentMedicalRecord.objects.count(), 1)
        self.assertEqual(PreviousAcademicRecord.objects.count(), 1)
        self.assertEqual(StudentPromotion.objects.count(), 1)
        self.assertEqual(Certificate.objects.count(), 1)
        self.assertEqual(StudentIDCard.objects.count(), 1)

        # Relationship sanity
        self.assertEqual(self.student.current_class, self.class_from)
        self.assertEqual(self.student.category, self.category)
        self.assertEqual(self.student.group, self.group)
        self.assertEqual(self.student_guardian.guardian, self.guardian)
        self.assertEqual(self.address.student, self.student)
        self.assertEqual(self.document.student, self.student)
        self.assertEqual(self.medical.student, self.student)
        self.assertEqual(self.prev_record.student, self.student)
        self.assertEqual(self.promotion.to_class, self.class_to)
        self.assertEqual(self.certificate.student, self.student)
        self.assertEqual(self.id_card.student, self.student)

        # __str__ should not raise
        str(self.student)
        str(self.guardian)
        str(self.student_guardian)
        str(self.address)
        str(self.document)
        str(self.medical)
        str(self.prev_record)
        str(self.promotion)
        str(self.certificate)
        str(self.id_card)
