from rest_framework import serializers

from .models import (
    MarksGrade,
    ExamType,
    Exam,
    ExamSchedule,
    ExamAttendance,
    AdmitCard,
    MarksRegister,
    StudentMarks,
    ExamResult,
    ProgressCard,
    MarkSheet,
    TabulationSheet,
)


class MarksGradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarksGrade
        fields = '__all__'


class ExamTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamType
        fields = '__all__'


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = '__all__'


class ExamScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamSchedule
        fields = '__all__'


class ExamAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamAttendance
        fields = '__all__'


class AdmitCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmitCard
        fields = '__all__'


class MarksRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarksRegister
        fields = '__all__'


class StudentMarksSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentMarks
        fields = '__all__'


class ExamResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamResult
        fields = '__all__'


class ProgressCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgressCard
        fields = '__all__'


class MarkSheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarkSheet
        fields = '__all__'


class TabulationSheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = TabulationSheet
        fields = '__all__'
