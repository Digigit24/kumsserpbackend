from rest_framework import serializers

from .models import Hostel, RoomType, Room, Bed, HostelAllocation, HostelFee


class HostelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hostel
        fields = '__all__'


class RoomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomType
        fields = '__all__'


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'


class BedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bed
        fields = '__all__'


class HostelAllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelAllocation
        fields = '__all__'


class HostelFeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelFee
        fields = '__all__'
