from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from payments.models import Payment
from payments.views import release_expired_boost_checkout


class Command(BaseCommand):
    help = 'Release BOOST credit held by expired M-Pesa checkouts.'

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(minutes=15)
        candidates = Payment.objects.filter(
            provider='mpesa',
            status__in=(Payment.STATUS_PENDING, Payment.STATUS_INITIATED),
            initiated_at__lte=cutoff,
            raw_payload__is_boost_checkout=True,
        )
        released = 0

        for payment in candidates.iterator():
            with transaction.atomic():
                locked_payment = Payment.objects.select_for_update().get(pk=payment.pk)
                if release_expired_boost_checkout(locked_payment):
                    released += 1

        self.stdout.write(self.style.SUCCESS(
            f'Reconciled {released} expired BOOST checkout(s).'
        ))
