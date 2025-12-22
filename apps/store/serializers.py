from rest_framework import serializers

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


class StoreCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreCategory
        fields = '__all__'


class StoreItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreItem
        fields = '__all__'


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = '__all__'


class StockReceiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockReceive
        fields = '__all__'


class StoreSaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreSale
        fields = '__all__'


class SaleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleItem
        fields = '__all__'


class PrintJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrintJob
        fields = '__all__'


class StoreCreditSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreCredit
        fields = '__all__'
