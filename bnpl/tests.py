from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from orders.models import Order
from payments.models import Payment

from .models import BNPLAccount
from .services import calculate_credit_limit


class CreditLimitTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='bnpl-test-user',
            password='test-password',
        )

    def test_new_account_starts_at_fifty(self):
        account = BNPLAccount.objects.create(user=self.user, phone_number='0712345678')
        self.assertEqual(account.credit_limit, Decimal('50.00'))

    def test_delivered_spend_and_repayment_increase_limit(self):
        Order.objects.create(
            user=self.user,
            pickup_address='Pickup',
            dropoff_address='Dropoff',
            status='delivered',
            price=Decimal('500.00'),
        )
        Payment.objects.create(
            user=self.user,
            amount=Decimal('20.00'),
            phone_number='254712345678',
            provider='mpesa',
            status=Payment.STATUS_SUCCESS,
            raw_payload={'is_bnpl_balance_payment': True},
        )

        self.assertEqual(calculate_credit_limit(self.user), Decimal('75.00'))
