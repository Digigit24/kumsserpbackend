from django.contrib import admin

from .models import Hostel, RoomType, Room, Bed, HostelAllocation, HostelFee


@admin.register(Hostel)
class HostelAdmin(admin.ModelAdmin):
    list_display = ('name', 'college', 'hostel_type', 'capacity', 'is_active')
    search_fields = ('name',)
    list_filter = ('hostel_type', 'college', 'is_active')


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'hostel', 'capacity', 'monthly_fee', 'is_active')
    list_filter = ('hostel', 'is_active')


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('hostel', 'room_number', 'room_type', 'capacity', 'occupied_beds', 'is_active')
    list_filter = ('hostel', 'room_type', 'is_active')
    search_fields = ('room_number',)


@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):
    list_display = ('room', 'bed_number', 'status', 'is_active')
    list_filter = ('status', 'is_active')


@admin.register(HostelAllocation)
class HostelAllocationAdmin(admin.ModelAdmin):
    list_display = ('student', 'hostel', 'room', 'bed', 'from_date', 'to_date', 'is_current', 'is_active')
    list_filter = ('hostel', 'is_current', 'is_active')


@admin.register(HostelFee)
class HostelFeeAdmin(admin.ModelAdmin):
    list_display = ('allocation', 'month', 'year', 'amount', 'due_date', 'is_paid', 'is_active')
    list_filter = ('month', 'year', 'is_paid', 'is_active')
