from django.contrib.auth import get_user_model
from django.test import TestCase
from decimal import Decimal

from orders.models import Order
from payments.models import Payment
from payments.views import get_order_payment_progress
from services.models import Service
from users.models import Location

User = get_user_model()


class PaymentProgressTests(TestCase):
    def setUp(self):
        self.location = Location.objects.create(name='Test Location')
        self.customer = User.objects.create_user(
            username='customer_user',
            email='customer@example.com',
            password='secret123',
            role='customer',
            phone='+254712345678',
        )
        self.service = Service.objects.create(
            name='Laundry Delivery',
            description='Test service',
            price=Decimal('1000.00'),
        )

    def test_payment_progress_uses_discounted_total_when_offer_applied(self):
        order = Order.objects.create(
            user=self.customer,
            pickup_address='Main Road',
            dropoff_address='Gate B',
            status='pending_payment',
            price=Decimal('1000.00'),
            actual_price=Decimal('500.00'),
            service_location=self.location,
        )
        order.services.add(self.service)

        Payment.objects.create(
            user=self.customer,
            order_id=order.id,
            amount=Decimal('200.00'),
            phone_number='+254712345678',
            provider='mpesa',
            status='success',
        )

        total, paid, remaining = get_order_payment_progress(order)

        self.assertEqual(total, Decimal('500.00'))
        self.assertEqual(paid, Decimal('200.00'))
        self.assertEqual(remaining, Decimal('300.00'))
