from rest_framework import serializers

from apps.teachers.models import Teacher
from apps.teachers.serializers import FlexibleTeacherField

from .models import Hostel, RoomType, Room, Bed, HostelAllocation, HostelFee


class HostelSerializer(serializers.ModelSerializer):
    warden = FlexibleTeacherField(queryset=Teacher.objects.all_colleges(), required=False, allow_null=True)
    warden_user_id = serializers.CharField(source='warden.user_id', read_only=True)
    warden_name = serializers.CharField(source='warden.get_full_name', read_only=True)
    college_name = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    updated_by_name = serializers.CharField(source='updated_by.get_full_name', read_only=True)
    def get_college_name(self, obj):
        if not obj.college:
            return ''
        return obj.college.short_name or obj.college.name or ''

    class Meta:
        model = Hostel
        fields = '__all__'


class RoomTypeSerializer(serializers.ModelSerializer):

    hostel_name = serializers.CharField(source='hostel.name', read_only=True)
    class Meta:
        model = RoomType
        fields = '__all__'


class RoomSerializer(serializers.ModelSerializer):

    hostel_name = serializers.CharField(source='hostel.name', read_only=True)
    room_type_name = serializers.CharField(source='room_type.name', read_only=True)
    class Meta:
        model = Room
        fields = '__all__'


class BedSerializer(serializers.ModelSerializer):

    room_number = serializers.CharField(source='room.room_number', read_only=True)
    hostel_name = serializers.CharField(source='room.hostel.name', read_only=True)
    class Meta:
        model = Bed
        fields = '__all__'


class HostelAllocationSerializer(serializers.ModelSerializer):

    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    hostel_name = serializers.CharField(source='hostel.name', read_only=True)
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    bed_number = serializers.CharField(source='bed.bed_number', read_only=True)
    class Meta:
        model = HostelAllocation
        fields = '__all__'


class HostelFeeSerializer(serializers.ModelSerializer):

    allocation_label = serializers.SerializerMethodField()

    student_name = serializers.CharField(source='allocation.student.get_full_name', read_only=True)
    hostel_name = serializers.CharField(source='allocation.hostel.name', read_only=True)
    room_number = serializers.CharField(source='allocation.room.room_number', read_only=True)
    bed_number = serializers.CharField(source='allocation.bed.bed_number', read_only=True)

    def get_allocation_label(self, obj):
        return str(obj.allocation) if obj.allocation else ''

    class Meta:
        model = HostelFee
        fields = '__all__'