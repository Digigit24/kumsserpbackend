"""
Signals for Accounting app.
Creates vouchers and account transactions on income/expense, and mirrors fee collections into income.
"""
from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from apps.accounting.models import (
    Income,
    Expense,
    Account,
    Voucher,
    AccountTransaction,
    IncomeCategory,
)


def _ensure_default_account(college):
    return Account.objects.get_or_create(
        college=college,
        account_number="DEFAULT",
        defaults={
            'account_name': 'Default Account',
            'bank_name': 'N/A',
            'balance': Decimal('0.00'),
        }
    )[0]


def _create_transaction(account, txn_type, amount, reference_type, reference_id, description, user):
    amount = Decimal(amount)
    new_balance = account.balance + amount if txn_type == 'credit' else account.balance - amount
    account.balance = new_balance
    account.save(update_fields=['balance', 'updated_at'])

    AccountTransaction.objects.create(
        account=account,
        transaction_type=txn_type,
        amount=amount,
        date=timezone.now().date(),
        reference_type=reference_type,
        reference_id=reference_id,
        description=description,
        balance_after=new_balance,
        created_by=user,
        updated_by=user,
    )


def _ensure_voucher(college, account, voucher_type, amount, ref_id, desc, user):
    voucher_number = f"VCHR-{voucher_type[:3].upper()}-{ref_id}"
    Voucher.objects.get_or_create(
        voucher_number=voucher_number,
        defaults={
            'college': college,
            'account': account,
            'voucher_type': voucher_type,
            'amount': amount,
            'date': timezone.now().date(),
            'description': desc,
            'created_by': user,
            'updated_by': user,
        }
    )


@receiver(post_save, sender=Income)
def income_post_save(sender, instance, created, **kwargs):
    if not created:
        return
    account = _ensure_default_account(instance.college)
    _create_transaction(
        account=account,
        txn_type='credit',
        amount=instance.amount,
        reference_type='income',
        reference_id=instance.id,
        description=instance.description,
        user=instance.created_by,
    )
    _ensure_voucher(
        college=instance.college,
        account=account,
        voucher_type='receipt',
        amount=instance.amount,
        ref_id=instance.id,
        desc=instance.description,
        user=instance.created_by,
    )


@receiver(post_save, sender=Expense)
def expense_post_save(sender, instance, created, **kwargs):
    if not created:
        return
    account = _ensure_default_account(instance.college)
    _create_transaction(
        account=account,
        txn_type='debit',
        amount=instance.amount,
        reference_type='expense',
        reference_id=instance.id,
        description=instance.description,
        user=instance.created_by,
    )
    _ensure_voucher(
        college=instance.college,
        account=account,
        voucher_type='payment',
        amount=instance.amount,
        ref_id=instance.id,
        desc=instance.description,
        user=instance.created_by,
    )


# Mirror FeeCollection into Income if fees app is installed
try:
    from apps.fees.models import FeeCollection  # type: ignore
except Exception:  # pragma: no cover
    FeeCollection = None


if FeeCollection:

    @receiver(post_save, sender=FeeCollection)
    def fee_collection_to_income(sender, instance, created, **kwargs):
        if not created:
            return
        college = instance.student.college if instance.student and instance.student.college_id else None
        if not college:
            return
        category, _ = IncomeCategory.objects.get_or_create(
            college=college,
            code='FEE',
            defaults={'name': 'Fees', 'created_by': instance.created_by, 'updated_by': instance.updated_by},
        )
        Income.objects.create(
            college=college,
            category=category,
            amount=instance.amount,
            date=instance.payment_date,
            description=f"Fee collection {instance.transaction_id or instance.id}",
            invoice_number=instance.transaction_id,
            payment_method=getattr(instance, 'payment_method', None),
            created_by=instance.created_by,
            updated_by=instance.updated_by,
        )
