from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Q
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from decimal import Decimal

from .models import (
    AppIncome,
    AppExpense,
    AppTotal,
    FinanceTotal,
    OtherExpense,
    FinanceTransaction
)
from .serializers import (
    AppIncomeSerializer,
    AppExpenseSerializer,
    AppTotalSerializer,
    FinanceTotalSerializer,
    OtherExpenseSerializer,
    FinanceTransactionSerializer,
    AppSummarySerializer,
    DashboardSerializer,
    MonthlyReportSerializer
)


class AppIncomeViewSet(viewsets.ModelViewSet):
    queryset = AppIncome.objects.all()
    serializer_class = AppIncomeSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['app_name', 'month']
    ordering_fields = ['month', 'amount']


class AppExpenseViewSet(viewsets.ModelViewSet):
    queryset = AppExpense.objects.all()
    serializer_class = AppExpenseSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['app_name', 'month']
    ordering_fields = ['month', 'amount']


class AppTotalViewSet(viewsets.ModelViewSet):
    queryset = AppTotal.objects.all()
    serializer_class = AppTotalSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['app_name', 'month']
    ordering_fields = ['month', 'net_total']


class FinanceTotalViewSet(viewsets.ModelViewSet):
    queryset = FinanceTotal.objects.all()
    serializer_class = FinanceTotalSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['month']
    ordering_fields = ['month', 'net_total']


class OtherExpenseViewSet(viewsets.ModelViewSet):
    queryset = OtherExpense.objects.all()
    serializer_class = OtherExpenseSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['category', 'date']
    ordering_fields = ['date', 'amount']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class FinanceTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FinanceTransaction.objects.all()
    serializer_class = FinanceTransactionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['app', 'type', 'date']
    ordering_fields = ['date', 'amount']

    def get_queryset(self):
        queryset = super().get_queryset()
        from_date = self.request.query_params.get('from_date')
        to_date = self.request.query_params.get('to_date')

        if from_date:
            queryset = queryset.filter(date__gte=from_date)
        if to_date:
            queryset = queryset.filter(date__lte=to_date)

        return queryset


class FinanceReportViewSet(viewsets.ViewSet):
    """Custom viewset for finance reports and analytics"""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def app_summary(self, request):
        """Get app-wise income/expense summary"""
        apps = ['fees', 'library', 'hostel', 'hr', 'store', 'other']
        summary = {}

        for app in apps:
            # Get income
            income = AppIncome.objects.filter(app_name=app).aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0.00')

            # Get expense
            expense = AppExpense.objects.filter(app_name=app).aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0.00')

            summary[app] = {
                'income': float(income),
                'expense': float(expense),
                'total': float(income - expense)
            }

        return Response(summary)

    @action(detail=False, methods=['get'])
    def totals(self, request):
        """Get overall finance totals"""
        total_income = AppIncome.objects.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')

        total_expense = AppExpense.objects.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')

        latest = FinanceTotal.objects.first()

        return Response({
            'total_income': float(total_income),
            'total_expense': float(total_expense),
            'net_total': float(total_income - total_expense),
            'last_updated': latest.last_updated if latest else None
        })

    @action(detail=False, methods=['get'])
    def monthly(self, request):
        """Get monthly report"""
        year = request.query_params.get('year', datetime.now().year)
        month = request.query_params.get('month', datetime.now().month)

        try:
            year = int(year)
            month = int(month)
            target_date = date(year, month, 1)
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid year or month'},
                status=status.HTTP_400_BAD_REQUEST
            )

        apps = ['fees', 'library', 'hostel', 'hr', 'store', 'other']
        apps_data = {}
        total_income = Decimal('0.00')
        total_expense = Decimal('0.00')

        for app in apps:
            income = AppIncome.objects.filter(
                app_name=app,
                month=target_date
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

            expense = AppExpense.objects.filter(
                app_name=app,
                month=target_date
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

            apps_data[app] = {
                'income': float(income),
                'expense': float(expense)
            }

            total_income += income
            total_expense += expense

        return Response({
            'month': target_date.strftime('%Y-%m'),
            'apps': apps_data,
            'total_income': float(total_income),
            'total_expense': float(total_expense),
            'net': float(total_income - total_expense)
        })

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get dashboard statistics"""
        today = date.today()
        current_month = date(today.year, today.month, 1)
        previous_month = current_month - relativedelta(months=1)
        year_start = date(today.year, 1, 1)

        # Current month stats
        current_income = AppIncome.objects.filter(
            month=current_month
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        current_expense = AppExpense.objects.filter(
            month=current_month
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        # Previous month stats
        prev_income = AppIncome.objects.filter(
            month=previous_month
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        prev_expense = AppExpense.objects.filter(
            month=previous_month
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        # Current year stats
        year_income = AppIncome.objects.filter(
            month__gte=year_start
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        year_expense = AppExpense.objects.filter(
            month__gte=year_start
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        # Top income sources
        top_income = []
        for app in ['fees', 'library', 'hostel', 'store']:
            amount = AppIncome.objects.filter(
                app_name=app
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            if amount > 0:
                top_income.append({'app': app, 'amount': float(amount)})
        top_income = sorted(top_income, key=lambda x: x['amount'], reverse=True)[:5]

        # Top expense sources
        top_expense = []
        for app in ['fees', 'hr', 'store', 'other']:
            amount = AppExpense.objects.filter(
                app_name=app
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            if amount > 0:
                top_expense.append({'app': app, 'amount': float(amount)})
        top_expense = sorted(top_expense, key=lambda x: x['amount'], reverse=True)[:5]

        return Response({
            'current_month': {
                'income': float(current_income),
                'expense': float(current_expense),
                'net': float(current_income - current_expense)
            },
            'previous_month': {
                'income': float(prev_income),
                'expense': float(prev_expense),
                'net': float(prev_income - prev_expense)
            },
            'current_year': {
                'income': float(year_income),
                'expense': float(year_expense),
                'net': float(year_income - year_expense)
            },
            'top_income_sources': top_income,
            'top_expense_sources': top_expense
        })
