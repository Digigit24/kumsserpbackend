from django.db import models
from django.conf import settings
from apps.core.models import CollegeScopedModel, AuditModel, College
from apps.teachers.models import Teacher
from apps.students.models import Student
from apps.academic.models import Class as AcademicClass, Section


class Hostel(CollegeScopedModel):
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='hostels')
    name = models.CharField(max_length=100)
    hostel_type = models.CharField(max_length=10)
    address = models.TextField(null=True, blank=True)
    capacity = models.IntegerField()
    warden = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='wardened_hostels')
    contact_number = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        db_table = 'hostel'
        indexes = [
            models.Index(fields=['college']),
        ]

    def __str__(self):
        return self.name


class RoomType(AuditModel):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='room_types')
    name = models.CharField(max_length=50)
    capacity = models.IntegerField()
    features = models.TextField(null=True, blank=True)
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'room_type'
        indexes = [
            models.Index(fields=['hostel']),
        ]

    def __str__(self):
        return f"{self.name} - {self.hostel}"


class Room(AuditModel):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='rooms')
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=20)
    floor = models.CharField(max_length=20, null=True, blank=True)
    capacity = models.IntegerField()
    occupied_beds = models.IntegerField(default=0)

    class Meta:
        db_table = 'room'
        unique_together = ['hostel', 'room_number']
        indexes = [
            models.Index(fields=['hostel', 'room_number']),
        ]

    def __str__(self):
        return f"{self.hostel} - {self.room_number}"


class Bed(AuditModel):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='beds')
    bed_number = models.CharField(max_length=10)
    status = models.CharField(max_length=20, default='vacant')

    class Meta:
        db_table = 'bed'
        unique_together = ['room', 'bed_number']
        indexes = [
            models.Index(fields=['room', 'status']),
        ]

    def __str__(self):
        return f"{self.room} - Bed {self.bed_number}"


class HostelAllocation(AuditModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='hostel_allocations')
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='allocations')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='allocations')
    bed = models.ForeignKey(Bed, on_delete=models.CASCADE, related_name='allocations')
    from_date = models.DateField()
    to_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=True)
    remarks = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'hostel_allocation'
        indexes = [
            models.Index(fields=['student', 'hostel', 'room', 'bed', 'is_current']),
        ]

    def __str__(self):
        return f"{self.student} -> {self.hostel} ({self.room}/{self.bed})"


class HostelFee(AuditModel):
    allocation = models.ForeignKey(HostelAllocation, on_delete=models.CASCADE, related_name='fees')
    month = models.IntegerField()
    year = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    is_paid = models.BooleanField(default=False)
    paid_date = models.DateField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'hostel_fee'
        unique_together = ['allocation', 'month', 'year']
        indexes = [
            models.Index(fields=['allocation', 'month', 'year', 'is_paid']),
        ]

    def __str__(self):
        return f"{self.allocation} - {self.month}/{self.year}"
