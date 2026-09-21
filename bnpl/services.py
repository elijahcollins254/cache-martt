from decimal import Decimal

from django.db import transaction

from .models import BNPLAccount


BASE_LIMIT = Decimal('50.00')
LIMIT_STEP = Decimal('10.00')
SPEND_STEP = Decimal('500.00')
ORDER_BONUS = Decimal('5.00')
REPAYMENT_BONUS = Decimal('10.00')
MAX_LIMIT = Decimal('1000.00')


def calculate_credit_limit(user):
    """Calculate a transparent limit from completed purchases and repayments.

    Only delivered orders count as purchases. BNPL borrowing itself does not
    increase the limit; successful repayments do.
    """
    from orders.models import Order
    from payments.models import Payment

    completed_orders = Order.objects.filter(user=user, status='delivered')
    total_spend = sum(
        (order.actual_price or order.price or Decimal('0.00') for order in completed_orders),
        Decimal('0.00'),
    )
    purchase_steps = int(total_spend // SPEND_STEP)
    order_bonus = min(ORDER_BONUS * completed_orders.count(), Decimal('100.00'))
    repayment_count = Payment.objects.filter(
        user=user,
        provider='mpesa',
        status=Payment.STATUS_SUCCESS,
        raw_payload__is_bnpl_balance_payment=True,
    ).count()
    repayment_bonus = min(REPAYMENT_BONUS * repayment_count, Decimal('100.00'))

    calculated = BASE_LIMIT + (LIMIT_STEP * purchase_steps) + order_bonus + repayment_bonus
    return min(calculated, MAX_LIMIT)


@transaction.atomic
def refresh_credit_limit(account):
    """Persist an earned limit without reducing an already approved limit."""
    account = BNPLAccount.objects.select_for_update().get(pk=account.pk)
    earned_limit = calculate_credit_limit(account.user)
    if earned_limit > account.credit_limit:
        account.credit_limit = earned_limit
        account.save(update_fields=['credit_limit', 'updated_at'])
    return account
