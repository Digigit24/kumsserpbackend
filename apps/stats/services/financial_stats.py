from django.db.models import Sum, Count, Avg, Q, F, DecimalField
from django.db.models.functions import Coalesce, TruncMonth
from django.utils import timezone
from datetime import datetime
from decimal import Decimal

from apps.fees.models import FeeCollection, FeeStructure, FeeInstallment
from apps.accounting.models import Income, Expense, IncomeCategory, ExpenseCategory
from apps.students.models import Student


class FinancialStatsService:
    """Service class for financial statistics calculations"""

    def __init__(self, college_id, filters=None):
        self.college_id = college_id
        self.filters = filters or {}

    def get_fee_collection_stats(self):
        """Calculate fee collection statistics"""
        # Base querysets
        students_qs = Student.objects.all_colleges().filter(college_id=self.college_id, is_active=True)

        # Apply filters
        if self.filters.get('program'):
            students_qs = students_qs.filter(program=self.filters['program'])
        if self.filters.get('class'):
            students_qs = students_qs.filter(current_class=self.filters['class'])

        total_students = students_qs.count()

        # Fee structure stats
        fee_structures = FeeStructure.objects.all_colleges().filter(
            student__college_id=self.college_id,
            student__is_active=True
        )

        if self.filters.get('program'):
            fee_structures = fee_structures.filter(student__program=self.filters['program'])
        if self.filters.get('class'):
            fee_structures = fee_structures.filter(student__current_class=self.filters['class'])
        if self.filters.get('academic_year'):
            fee_structures = fee_structures.filter(fee_master__academic_year=self.filters['academic_year'])

        total_fee_amount = fee_structures.aggregate(
            total=Coalesce(Sum('amount'), Decimal('0'))
        )['total']

        total_balance = fee_structures.aggregate(
            total=Coalesce(Sum('balance'), Decimal('0'))
        )['total']

        # Fee collection stats
        collections = FeeCollection.objects.all_colleges().filter(
            student__college_id=self.college_id,
            status='COMPLETED'
        )

        if self.filters.get('from_date'):
            collections = collections.filter(payment_date__gte=self.filters['from_date'])
        if self.filters.get('to_date'):
            collections = collections.filter(payment_date__lte=self.filters['to_date'])
        if self.filters.get('program'):
            collections = collections.filter(student__program=self.filters['program'])
        if self.filters.get('class'):
            collections = collections.filter(student__current_class=self.filters['class'])

        total_collected = collections.aggregate(
            total=Coalesce(Sum('amount'), Decimal('0'))
        )['total']

        total_outstanding = total_fee_amount - total_collected
        collection_rate = (total_collected / total_fee_amount * 100) if total_fee_amount > 0 else 0

        # Defaulters (students with balance > 0)
        defaulters_count = fee_structures.filter(balance__gt=0).values('student').distinct().count()

        # Fully paid students
        fully_paid_count = fee_structures.filter(is_paid=True).values('student').distinct().count()

        # Payment method distribution
        payment_methods = collections.values('payment_method').annotate(
            count=Count('id'),
            total_amount=Coalesce(Sum('amount'), Decimal('0'))
        )

        payment_method_distribution = []
        total_collections_count = collections.count()
        for method in payment_methods:
            payment_method_distribution.append({
                'payment_method': method['payment_method'] or 'N/A',
                'count': method['count'],
                'total_amount': method['total_amount'],
                'percentage': round((method['count'] / total_collections_count * 100), 2) if total_collections_count > 0 else 0
            })

        # Monthly revenue trend
        monthly_data = collections.annotate(
            month=TruncMonth('payment_date')
        ).values('month').annotate(
            total_collected=Coalesce(Sum('amount'), Decimal('0'))
        ).order_by('month')

        monthly_trend = []
        for month_data in monthly_data:
            month_fee_structures = fee_structures.filter(
                due_date__year=month_data['month'].year,
                due_date__month=month_data['month'].month
            )
            total_due = month_fee_structures.aggregate(
                total=Coalesce(Sum('amount'), Decimal('0'))
            )['total']

            collection_rate_month = (month_data['total_collected'] / total_due * 100) if total_due > 0 else 0

            monthly_trend.append({
                'month': month_data['month'].strftime('%B'),
                'year': month_data['month'].year,
                'total_collected': month_data['total_collected'],
                'total_due': total_due,
                'collection_rate': round(collection_rate_month, 2)
            })

        return {
            'total_students': total_students,
            'total_fee_amount': total_fee_amount,
            'total_collected': total_collected,
            'total_outstanding': total_outstanding,
            'collection_rate': round(collection_rate, 2),
            'defaulters_count': defaulters_count,
            'fully_paid_count': fully_paid_count,
            'payment_method_distribution': payment_method_distribution,
            'monthly_trend': monthly_trend,
        }

    def get_expense_stats(self):
        """Calculate expense statistics"""
        expenses = Expense.objects.all_colleges().filter(
            college_id=self.college_id,
            is_active=True
        )

        if self.filters.get('from_date'):
            expenses = expenses.filter(date__gte=self.filters['from_date'])
        if self.filters.get('to_date'):
            expenses = expenses.filter(date__lte=self.filters['to_date'])

        total_expenses = expenses.aggregate(
            total=Coalesce(Sum('amount'), Decimal('0'))
        )['total']

        total_transactions = expenses.count()

        average_expense = (total_expenses / total_transactions) if total_transactions > 0 else Decimal('0')

        # Category-wise breakdown
        category_breakdown_qs = expenses.values(
            'category__id',
            'category__name'
        ).annotate(
            total_amount=Coalesce(Sum('amount'), Decimal('0')),
            transaction_count=Count('id')
        )

        category_breakdown = []
        for category in category_breakdown_qs:
            percentage = (category['total_amount'] / total_expenses * 100) if total_expenses > 0 else 0
            category_breakdown.append({
                'category_id': category['category__id'],
                'category_name': category['category__name'] or 'Uncategorized',
                'total_amount': category['total_amount'],
                'transaction_count': category['transaction_count'],
                'percentage': round(percentage, 2)
            })

        return {
            'total_expenses': total_expenses,
            'total_transactions': total_transactions,
            'average_expense': average_expense,
            'category_breakdown': category_breakdown,
        }

    def get_income_stats(self):
        """Calculate income statistics"""
        income = Income.objects.all_colleges().filter(
            college_id=self.college_id,
            is_active=True
        )

        if self.filters.get('from_date'):
            income = income.filter(date__gte=self.filters['from_date'])
        if self.filters.get('to_date'):
            income = income.filter(date__lte=self.filters['to_date'])

        total_income = income.aggregate(
            total=Coalesce(Sum('amount'), Decimal('0'))
        )['total']

        total_transactions = income.count()

        average_income = (total_income / total_transactions) if total_transactions > 0 else Decimal('0')

        # Category-wise breakdown
        category_breakdown_qs = income.values(
            'category__id',
            'category__name'
        ).annotate(
            total_amount=Coalesce(Sum('amount'), Decimal('0')),
            transaction_count=Count('id')
        )

        category_breakdown = []
        for category in category_breakdown_qs:
            percentage = (category['total_amount'] / total_income * 100) if total_income > 0 else 0
            category_breakdown.append({
                'category_id': category['category__id'],
                'category_name': category['category__name'] or 'Uncategorized',
                'total_amount': category['total_amount'],
                'transaction_count': category['transaction_count'],
                'percentage': round(percentage, 2)
            })

        return {
            'total_income': total_income,
            'total_transactions': total_transactions,
            'average_income': average_income,
            'category_breakdown': category_breakdown,
        }

    def get_all_stats(self):
        """Get all financial statistics combined"""
        fee_collection = self.get_fee_collection_stats()
        expenses = self.get_expense_stats()
        income = self.get_income_stats()

        # Calculate net balance
        net_balance = (
            fee_collection['total_collected'] +
            income['total_income'] -
            expenses['total_expenses']
        )

        return {
            'fee_collection': fee_collection,
            'expenses': expenses,
            'income': income,
            'net_balance': net_balance,
            'generated_at': timezone.now(),
        }
