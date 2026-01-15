from django.core.management.base import BaseCommand
from django.db.models import Sum
from django.apps import apps
from datetime import date
from decimal import Decimal
from finance.models import AppIncome, AppExpense, AppTotal, FinanceTotal, FinanceTransaction


class Command(BaseCommand):
    help = 'Sync all finance data from existing transactions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing finance data before sync',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing finance data...')
            AppIncome.objects.all().delete()
            AppExpense.objects.all().delete()
            AppTotal.objects.all().delete()
            FinanceTotal.objects.all().delete()
            FinanceTransaction.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Cleared all finance data'))

        self.stdout.write('Starting finance data sync...')

        # Sync fees app
        self.sync_fees()

        # Sync library app
        self.sync_library()

        # Sync hostel app
        self.sync_hostel()

        # Sync HR app
        self.sync_hr()

        # Sync store app
        self.sync_store()

        # Update totals
        self.update_all_totals()

        self.stdout.write(self.style.SUCCESS('Finance data sync completed!'))

    def get_month_start(self, dt):
        """Get first day of month"""
        if isinstance(dt, date):
            return date(dt.year, dt.month, 1)
        return date.today().replace(day=1)

    def sync_fees(self):
        """Sync fees app transactions"""
        self.stdout.write('Syncing fees app...')

        try:
            FeeCollection = apps.get_model('fees', 'FeeCollection')
            for collection in FeeCollection.objects.all():
                if collection.amount and collection.amount > 0:
                    month = self.get_month_start(
                        getattr(collection, 'payment_date', None) or date.today()
                    )
                    income, _ = AppIncome.objects.get_or_create(
                        app_name='fees',
                        month=month
                    )
                    income.amount += collection.amount
                    income.transaction_count += 1
                    income.save()

                    FinanceTransaction.objects.create(
                        app='fees',
                        type='income',
                        amount=collection.amount,
                        description='Fee collection',
                        reference_id=collection.id,
                        reference_model='FeeCollection',
                        date=month
                    )
            self.stdout.write(self.style.SUCCESS('  ✓ Fee collections synced'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ! Fee collections: {e}'))

        try:
            FeeFine = apps.get_model('fees', 'FeeFine')
            for fine in FeeFine.objects.all():
                if fine.amount and fine.amount > 0:
                    month = self.get_month_start(
                        getattr(fine, 'date', None) or date.today()
                    )
                    income, _ = AppIncome.objects.get_or_create(
                        app_name='fees',
                        month=month
                    )
                    income.amount += fine.amount
                    income.transaction_count += 1
                    income.save()

                    FinanceTransaction.objects.create(
                        app='fees',
                        type='income',
                        amount=fine.amount,
                        description='Fee fine',
                        reference_id=fine.id,
                        reference_model='FeeFine',
                        date=month
                    )
            self.stdout.write(self.style.SUCCESS('  ✓ Fee fines synced'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ! Fee fines: {e}'))

        try:
            FeeRefund = apps.get_model('fees', 'FeeRefund')
            for refund in FeeRefund.objects.all():
                if refund.amount and refund.amount > 0:
                    month = self.get_month_start(
                        getattr(refund, 'refund_date', None) or date.today()
                    )
                    expense, _ = AppExpense.objects.get_or_create(
                        app_name='fees',
                        month=month
                    )
                    expense.amount += refund.amount
                    expense.transaction_count += 1
                    expense.save()

                    FinanceTransaction.objects.create(
                        app='fees',
                        type='expense',
                        amount=refund.amount,
                        description='Fee refund',
                        reference_id=refund.id,
                        reference_model='FeeRefund',
                        date=month
                    )
            self.stdout.write(self.style.SUCCESS('  ✓ Fee refunds synced'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ! Fee refunds: {e}'))

    def sync_library(self):
        """Sync library app transactions"""
        self.stdout.write('Syncing library app...')

        try:
            LibraryFine = apps.get_model('library', 'LibraryFine')
            for fine in LibraryFine.objects.all():
                if fine.amount and fine.amount > 0:
                    month = self.get_month_start(
                        getattr(fine, 'date', None) or date.today()
                    )
                    income, _ = AppIncome.objects.get_or_create(
                        app_name='library',
                        month=month
                    )
                    income.amount += fine.amount
                    income.transaction_count += 1
                    income.save()

                    FinanceTransaction.objects.create(
                        app='library',
                        type='income',
                        amount=fine.amount,
                        description='Library fine',
                        reference_id=fine.id,
                        reference_model='LibraryFine',
                        date=month
                    )
            self.stdout.write(self.style.SUCCESS('  ✓ Library fines synced'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ! Library fines: {e}'))

    def sync_hostel(self):
        """Sync hostel app transactions"""
        self.stdout.write('Syncing hostel app...')

        try:
            HostelFee = apps.get_model('hostel', 'HostelFee')
            for fee in HostelFee.objects.all():
                if fee.amount and fee.amount > 0:
                    month = self.get_month_start(
                        getattr(fee, 'payment_date', None) or date.today()
                    )
                    income, _ = AppIncome.objects.get_or_create(
                        app_name='hostel',
                        month=month
                    )
                    income.amount += fee.amount
                    income.transaction_count += 1
                    income.save()

                    FinanceTransaction.objects.create(
                        app='hostel',
                        type='income',
                        amount=fee.amount,
                        description='Hostel fee',
                        reference_id=fee.id,
                        reference_model='HostelFee',
                        date=month
                    )
            self.stdout.write(self.style.SUCCESS('  ✓ Hostel fees synced'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ! Hostel fees: {e}'))

    def sync_hr(self):
        """Sync HR app transactions"""
        self.stdout.write('Syncing HR app...')

        try:
            Payroll = apps.get_model('hr', 'Payroll')
            for payroll in Payroll.objects.all():
                if payroll.net_salary and payroll.net_salary > 0:
                    month = self.get_month_start(
                        getattr(payroll, 'payment_date', None) or
                        getattr(payroll, 'month', None) or
                        date.today()
                    )
                    expense, _ = AppExpense.objects.get_or_create(
                        app_name='hr',
                        month=month
                    )
                    expense.amount += payroll.net_salary
                    expense.transaction_count += 1
                    expense.save()

                    FinanceTransaction.objects.create(
                        app='hr',
                        type='expense',
                        amount=payroll.net_salary,
                        description='Payroll payment',
                        reference_id=payroll.id,
                        reference_model='Payroll',
                        date=month
                    )
            self.stdout.write(self.style.SUCCESS('  ✓ Payrolls synced'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ! Payrolls: {e}'))

    def sync_store(self):
        """Sync store app transactions"""
        self.stdout.write('Syncing store app...')

        try:
            StoreSale = apps.get_model('store', 'StoreSale')
            for sale in StoreSale.objects.all():
                if sale.total_amount and sale.total_amount > 0:
                    month = self.get_month_start(
                        getattr(sale, 'sale_date', None) or date.today()
                    )
                    income, _ = AppIncome.objects.get_or_create(
                        app_name='store',
                        month=month
                    )
                    income.amount += sale.total_amount
                    income.transaction_count += 1
                    income.save()

                    FinanceTransaction.objects.create(
                        app='store',
                        type='income',
                        amount=sale.total_amount,
                        description='Store sale',
                        reference_id=sale.id,
                        reference_model='StoreSale',
                        date=month
                    )
            self.stdout.write(self.style.SUCCESS('  ✓ Store sales synced'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ! Store sales: {e}'))

        try:
            PurchaseOrder = apps.get_model('store', 'PurchaseOrder')
            for po in PurchaseOrder.objects.all():
                if po.grand_total and po.grand_total > 0:
                    month = self.get_month_start(
                        getattr(po, 'order_date', None) or date.today()
                    )
                    expense, _ = AppExpense.objects.get_or_create(
                        app_name='store',
                        month=month
                    )
                    expense.amount += po.grand_total
                    expense.transaction_count += 1
                    expense.save()

                    FinanceTransaction.objects.create(
                        app='store',
                        type='expense',
                        amount=po.grand_total,
                        description='Purchase order',
                        reference_id=po.id,
                        reference_model='PurchaseOrder',
                        date=month
                    )
            self.stdout.write(self.style.SUCCESS('  ✓ Purchase orders synced'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ! Purchase orders: {e}'))

    def update_all_totals(self):
        """Update all AppTotal and FinanceTotal records"""
        self.stdout.write('Updating totals...')

        # Get all unique months
        income_months = AppIncome.objects.values_list('month', flat=True).distinct()
        expense_months = AppExpense.objects.values_list('month', flat=True).distinct()
        all_months = set(list(income_months) + list(expense_months))

        for month in all_months:
            # Update app totals
            for app in ['fees', 'library', 'hostel', 'hr', 'store', 'other']:
                income = AppIncome.objects.filter(
                    app_name=app,
                    month=month
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

                expense = AppExpense.objects.filter(
                    app_name=app,
                    month=month
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

                if income > 0 or expense > 0:
                    AppTotal.objects.update_or_create(
                        app_name=app,
                        month=month,
                        defaults={
                            'income': income,
                            'expense': expense,
                            'net_total': income - expense
                        }
                    )

            # Update finance totals
            total_income = AppIncome.objects.filter(
                month=month
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

            total_expense = AppExpense.objects.filter(
                month=month
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

            FinanceTotal.objects.update_or_create(
                month=month,
                defaults={
                    'total_income': total_income,
                    'total_expense': total_expense,
                    'net_total': total_income - total_expense
                }
            )

        self.stdout.write(self.style.SUCCESS('  ✓ All totals updated'))
