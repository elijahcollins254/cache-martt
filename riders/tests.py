from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from orders.models import Order
from .models import RiderLedgerEntry, RiderWallet, WithdrawalRequest
from .payouts import credit_delivery_earning, fail_withdrawal_and_refund


class RiderEarningsTests(TestCase):
	def setUp(self):
		User = get_user_model()
		self.rider = User.objects.create_user(username='payout-rider', password='test', role='rider')
		self.order = Order.objects.create(
			pickup_address='Pickup',
			dropoff_address='Dropoff',
			delivery_rider=self.rider,
			status='at_gate',
		)

	@override_settings(RIDER_DELIVERY_EARNING_AMOUNT='50.00')
	def test_delivery_earning_is_credited_once(self):
		first = credit_delivery_earning(self.order, self.rider)
		second = credit_delivery_earning(self.order, self.rider)

		wallet = RiderWallet.objects.get(rider=self.rider)
		self.assertEqual(first.pk, second.pk)
		self.assertEqual(wallet.balance, Decimal('50.00'))
		self.assertEqual(
			RiderLedgerEntry.objects.filter(
				rider=self.rider, order=self.order, entry_type=RiderLedgerEntry.TYPE_EARNING
			).count(),
			1,
		)

	def test_failed_withdrawal_refunds_once(self):
		wallet = RiderWallet.objects.create(rider=self.rider, balance=Decimal('100.00'))
		withdrawal = WithdrawalRequest.objects.create(
			rider=self.rider,
			amount=Decimal('50.00'),
			phone_number='+254712345678',
			status=WithdrawalRequest.STATUS_PROCESSING,
		)
		wallet.balance -= withdrawal.amount
		wallet.save(update_fields=['balance'])

		fail_withdrawal_and_refund(withdrawal, 'Provider rejected payout')
		fail_withdrawal_and_refund(withdrawal, 'Duplicate callback')

		wallet.refresh_from_db()
		self.assertEqual(wallet.balance, Decimal('100.00'))
		self.assertEqual(
			RiderLedgerEntry.objects.filter(
				rider=self.rider, withdrawal=withdrawal, entry_type=RiderLedgerEntry.TYPE_REFUND
			).count(),
			1,
		)
