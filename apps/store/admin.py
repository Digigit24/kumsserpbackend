from django.contrib import admin

from .models import (
    StoreCategory,
    StoreItem,
    Vendor,
    StockReceive,
    StoreSale,
    SaleItem,
    PrintJob,
    StoreCredit,
)


@admin.register(StoreCategory)
class StoreCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'college', 'is_active')
    search_fields = ('name', 'code')
    list_filter = ('college', 'is_active')


@admin.register(StoreItem)
class StoreItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'college', 'category', 'price', 'stock_quantity', 'is_active')
    search_fields = ('name', 'code', 'barcode')
    list_filter = ('college', 'category', 'is_active')


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'college', 'phone', 'email', 'is_active')
    search_fields = ('name', 'phone', 'email', 'gstin')
    list_filter = ('college', 'is_active')


@admin.register(StockReceive)
class StockReceiveAdmin(admin.ModelAdmin):
    list_display = ('item', 'vendor', 'quantity', 'unit_price', 'receive_date', 'is_active')
    list_filter = ('receive_date', 'is_active')


@admin.register(StoreSale)
class StoreSaleAdmin(admin.ModelAdmin):
    list_display = ('sale_date', 'college', 'student', 'teacher', 'total_amount', 'payment_status', 'is_active')
    list_filter = ('payment_status', 'sale_date', 'is_active')


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ('sale', 'item', 'quantity', 'unit_price', 'total_price', 'is_active')
    list_filter = ('is_active',)


@admin.register(PrintJob)
class PrintJobAdmin(admin.ModelAdmin):
    list_display = ('job_name', 'teacher', 'pages', 'copies', 'total_amount', 'status', 'submission_date', 'is_active')
    list_filter = ('status', 'submission_date', 'completion_date', 'is_active')


@admin.register(StoreCredit)
class StoreCreditAdmin(admin.ModelAdmin):
    list_display = ('student', 'transaction_type', 'amount', 'date', 'balance_after', 'is_active')
    list_filter = ('transaction_type', 'date', 'is_active')
