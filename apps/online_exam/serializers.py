from rest_framework import serializers

from .models import (
    QuestionBank,
    Question,
    QuestionOption,
    OnlineExam,
    ExamQuestion,
    StudentExamAttempt,
    StudentAnswer,
)


class QuestionBankSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionBank
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'


class QuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = '__all__'


class OnlineExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnlineExam
        fields = '__all__'


class ExamQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamQuestion
        fields = '__all__'


class StudentExamAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentExamAttempt
        fields = '__all__'


class StudentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAnswer
        fields = '__all__'
