from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum
from datetime import date
from decimal import Decimal


def get_month_start(dt):
    """Get first day of month"""
    return date(dt.year, dt.month, 1)


def update_app_totals(app_name, month):
    """Update AppTotal for given app and month"""
    from .models import AppIncome, AppExpense, AppTotal

    month_start = get_month_start(month)

    # Get income
    income = AppIncome.objects.filter(
        app_name=app_name,
        month=month_start
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    # Get expense
    expense = AppExpense.objects.filter(
        app_name=app_name,
        month=month_start
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    # Update or create AppTotal
    app_total, _ = AppTotal.objects.update_or_create(
        app_name=app_name,
        month=month_start,
        defaults={
            'income': income,
            'expense': expense,
            'net_total': income - expense
        }
    )


def update_finance_totals(month):
    """Update FinanceTotal for given month"""
    from .models import AppIncome, AppExpense, FinanceTotal

    month_start = get_month_start(month)

    # Get total income
    total_income = AppIncome.objects.filter(
        month=month_start
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    # Get total expense
    total_expense = AppExpense.objects.filter(
        month=month_start
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    # Update or create FinanceTotal
    finance_total, _ = FinanceTotal.objects.update_or_create(
        month=month_start,
        defaults={
            'total_income': total_income,
            'total_expense': total_expense,
            'net_total': total_income - total_expense
        }
    )


def log_transaction(app, trans_type, amount, description, reference_id, reference_model, trans_date, payment_method='cash'):
    """Log transaction in FinanceTransaction"""
    from .models import FinanceTransaction

    FinanceTransaction.objects.create(
        app=app,
        type=trans_type,
        amount=amount,
        description=description,
        payment_method=payment_method,
        reference_id=reference_id,
        reference_model=reference_model,
        date=trans_date
    )


# ============ FEES APP SIGNALS ============

@receiver(post_save, sender='fees.FeeCollection')
def sync_fee_collection(sender, instance, created, **kwargs):
    """Sync fee collection to finance (INCOME)"""
    from .models import AppIncome

    if instance.amount and instance.amount > 0:
        month_start = get_month_start(instance.payment_date if hasattr(instance, 'payment_date') else date.today())

        # Update AppIncome
        income, _ = AppIncome.objects.get_or_create(
            app_name='fees',
            month=month_start
        )

        if created:
            income.amount += instance.amount
            income.transaction_count += 1
            income.save()

            # Log transaction
            log_transaction(
                app='fees',
                trans_type='income',
                amount=instance.amount,
                description='Fee collection',
                reference_id=instance.id,
                reference_model='FeeCollection',
                trans_date=month_start
            )

        # Update totals
        update_app_totals('fees', month_start)
        update_finance_totals(month_start)


@receiver(post_save, sender='fees.FeeFine')
def sync_fee_fine(sender, instance, created, **kwargs):
    """Sync fee fine to finance (INCOME)"""
    from .models import AppIncome

    if instance.amount and instance.amount > 0:
        month_start = get_month_start(instance.date if hasattr(instance, 'date') else date.today())

        # Update AppIncome
        income, _ = AppIncome.objects.get_or_create(
            app_name='fees',
            month=month_start
        )

        if created:
            income.amount += instance.amount
            income.transaction_count += 1
            income.save()

            # Log transaction
            log_transaction(
                app='fees',
                trans_type='income',
                amount=instance.amount,
                description='Fee fine',
                reference_id=instance.id,
                reference_model='FeeFine',
                trans_date=month_start
            )

        # Update totals
        update_app_totals('fees', month_start)
        update_finance_totals(month_start)


@receiver(post_save, sender='fees.FeeRefund')
def sync_fee_refund(sender, instance, created, **kwargs):
    """Sync fee refund to finance (EXPENSE)"""
    from .models import AppExpense

    if instance.amount and instance.amount > 0:
        month_start = get_month_start(instance.refund_date if hasattr(instance, 'refund_date') else date.today())

        # Update AppExpense
        expense, _ = AppExpense.objects.get_or_create(
            app_name='fees',
            month=month_start
        )

        if created:
            expense.amount += instance.amount
            expense.transaction_count += 1
            expense.save()

            # Log transaction
            log_transaction(
                app='fees',
                trans_type='expense',
                amount=instance.amount,
                description='Fee refund',
                reference_id=instance.id,
                reference_model='FeeRefund',
                trans_date=month_start
            )

        # Update totals
        update_app_totals('fees', month_start)
        update_finance_totals(month_start)


# ============ LIBRARY APP SIGNALS ============

@receiver(post_save, sender='library.LibraryFine')
def sync_library_fine(sender, instance, created, **kwargs):
    """Sync library fine to finance (INCOME)"""
    from .models import AppIncome

    if instance.amount and instance.amount > 0:
        month_start = get_month_start(instance.date if hasattr(instance, 'date') else date.today())

        # Update AppIncome
        income, _ = AppIncome.objects.get_or_create(
            app_name='library',
            month=month_start
        )

        if created:
            income.amount += instance.amount
            income.transaction_count += 1
            income.save()

            # Log transaction
            log_transaction(
                app='library',
                trans_type='income',
                amount=instance.amount,
                description='Library fine',
                reference_id=instance.id,
                reference_model='LibraryFine',
                trans_date=month_start
            )

        # Update totals
        update_app_totals('library', month_start)
        update_finance_totals(month_start)


# ============ HOSTEL APP SIGNALS ============

@receiver(post_save, sender='hostel.HostelFee')
def sync_hostel_fee(sender, instance, created, **kwargs):
    """Sync hostel fee to finance (INCOME)"""
    from .models import AppIncome

    if instance.amount and instance.amount > 0:
        month_start = get_month_start(instance.payment_date if hasattr(instance, 'payment_date') else date.today())

        # Update AppIncome
        income, _ = AppIncome.objects.get_or_create(
            app_name='hostel',
            month=month_start
        )

        if created:
            income.amount += instance.amount
            income.transaction_count += 1
            income.save()

            # Log transaction
            log_transaction(
                app='hostel',
                trans_type='income',
                amount=instance.amount,
                description='Hostel fee',
                reference_id=instance.id,
                reference_model='HostelFee',
                trans_date=month_start
            )

        # Update totals
        update_app_totals('hostel', month_start)
        update_finance_totals(month_start)


# ============ HR APP SIGNALS ============

@receiver(post_save, sender='hr.Payroll')
def sync_payroll(sender, instance, created, **kwargs):
    """Sync payroll to finance (EXPENSE)"""
    from .models import AppExpense

    if instance.net_salary and instance.net_salary > 0:
        month_start = get_month_start(instance.payment_date if hasattr(instance, 'payment_date') else date.today())

        # Update AppExpense
        expense, _ = AppExpense.objects.get_or_create(
            app_name='hr',
            month=month_start
        )

        if created:
            expense.amount += instance.net_salary
            expense.transaction_count += 1
            expense.save()

            # Log transaction
            log_transaction(
                app='hr',
                trans_type='expense',
                amount=instance.net_salary,
                description='Payroll payment',
                reference_id=instance.id,
                reference_model='Payroll',
                trans_date=month_start
            )

        # Update totals
        update_app_totals('hr', month_start)
        update_finance_totals(month_start)


# ============ STORE APP SIGNALS ============

@receiver(post_save, sender='store.StoreSale')
def sync_store_sale(sender, instance, created, **kwargs):
    """Sync store sale to finance (INCOME)"""
    from .models import AppIncome

    if instance.total_amount and instance.total_amount > 0:
        month_start = get_month_start(instance.sale_date if hasattr(instance, 'sale_date') else date.today())

        # Update AppIncome
        income, _ = AppIncome.objects.get_or_create(
            app_name='store',
            month=month_start
        )

        if created:
            income.amount += instance.total_amount
            income.transaction_count += 1
            income.save()

            # Log transaction
            log_transaction(
                app='store',
                trans_type='income',
                amount=instance.total_amount,
                description='Store sale',
                reference_id=instance.id,
                reference_model='StoreSale',
                trans_date=month_start
            )

        # Update totals
        update_app_totals('store', month_start)
        update_finance_totals(month_start)


@receiver(post_save, sender='store.PurchaseOrder')
def sync_purchase_order(sender, instance, created, **kwargs):
    """Sync purchase order to finance (EXPENSE)"""
    from .models import AppExpense

    if instance.grand_total and instance.grand_total > 0:
        month_start = get_month_start(instance.order_date if hasattr(instance, 'order_date') else date.today())

        # Update AppExpense
        expense, _ = AppExpense.objects.get_or_create(
            app_name='store',
            month=month_start
        )

        if created:
            expense.amount += instance.grand_total
            expense.transaction_count += 1
            expense.save()

            # Log transaction
            log_transaction(
                app='store',
                trans_type='expense',
                amount=instance.grand_total,
                description='Purchase order',
                reference_id=instance.id,
                reference_model='PurchaseOrder',
                trans_date=month_start
            )

        # Update totals
        update_app_totals('store', month_start)
        update_finance_totals(month_start)


# ============ OTHER EXPENSE SIGNALS ============

@receiver(post_save, sender='finance.OtherExpense')
def sync_other_expense(sender, instance, created, **kwargs):
    """Sync other expense to finance (EXPENSE)"""
    from .models import AppExpense

    if instance.amount and instance.amount > 0:
        month_start = get_month_start(instance.date)

        # Update AppExpense
        expense, _ = AppExpense.objects.get_or_create(
            app_name='other',
            month=month_start
        )

        if created:
            expense.amount += instance.amount
            expense.transaction_count += 1
            expense.save()

            # Log transaction
            log_transaction(
                app='other',
                trans_type='expense',
                amount=instance.amount,
                description=instance.title,
                reference_id=instance.id,
                reference_model='OtherExpense',
                trans_date=instance.date,
                payment_method=instance.payment_method
            )

        # Update totals
        update_app_totals('other', month_start)
        update_finance_totals(month_start)
