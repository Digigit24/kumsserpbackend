from rest_framework import serializers
from .models import (
    AppIncome,
    AppExpense,
    AppTotal,
    FinanceTotal,
    OtherExpense,
    FinanceTransaction
)


class AppIncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppIncome
        fields = '__all__'
        read_only_fields = ['last_synced']


class AppExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppExpense
        fields = '__all__'
        read_only_fields = ['last_synced']


class AppTotalSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppTotal
        fields = '__all__'
        read_only_fields = ['net_total', 'last_updated']


class FinanceTotalSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinanceTotal
        fields = '__all__'
        read_only_fields = ['net_total', 'last_updated']


class OtherExpenseSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = OtherExpense
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class FinanceTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinanceTransaction
        fields = '__all__'
        read_only_fields = ['created_at']


class AppSummarySerializer(serializers.Serializer):
    """Serializer for app-wise summary"""
    app_name = serializers.CharField()
    income = serializers.DecimalField(max_digits=12, decimal_places=2)
    expense = serializers.DecimalField(max_digits=12, decimal_places=2)
    total = serializers.DecimalField(max_digits=12, decimal_places=2)


class DashboardSerializer(serializers.Serializer):
    """Serializer for dashboard stats"""
    current_month = serializers.DictField()
    previous_month = serializers.DictField()
    current_year = serializers.DictField()
    top_income_sources = serializers.ListField()
    top_expense_sources = serializers.ListField()


class MonthlyReportSerializer(serializers.Serializer):
    """Serializer for monthly report"""
    month = serializers.CharField()
    apps = serializers.DictField()
    total_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_expense = serializers.DecimalField(max_digits=12, decimal_places=2)
    net = serializers.DecimalField(max_digits=12, decimal_places=2)
