"""
Combined models.py content for two Django apps: `riders` and `payments`.

Save the `riders` portion to `riders/models.py` and the `payments` portion to `payments/models.py` in your project.

These models assume you have a custom user model (settings.AUTH_USER_MODEL) and an `orders.Order` model.
"""

# ---------------------------
# riders/models.py
# ---------------------------
from django.conf import settings
from django.db import models
from django.utils import timezone


class RiderProfile(models.Model):
    """Optional extended profile for users that act as riders/drivers.

    If you already store rider fields on your custom User model (is_rider flag),
    you can use this profile for extra per-rider data (vehicle, documents, rating).
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rider_profile')
    display_name = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=32, blank=True)
    vehicle_type = models.CharField(max_length=60, blank=True, help_text='e.g. Motorcycle, Car, Van')
    vehicle_reg = models.CharField(max_length=40, blank=True, help_text='Vehicle registration number')
    is_active = models.BooleanField(default=True)

    # verification / docs
    id_document = models.FileField(upload_to='riders/docs/', blank=True, null=True)
    license_document = models.FileField(upload_to='riders/docs/', blank=True, null=True)

    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    completed_jobs = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Rider profile'
        verbose_name_plural = 'Rider profiles'

    def __str__(self):
        return self.display_name or getattr(self.user, 'username', str(self.user))


class RiderLocation(models.Model):
    """Stores periodic location updates from riders for live tracking.

    A rider device (mobile app) should POST GPS updates to an endpoint that
    creates RiderLocation rows. For real-time apps you can combine this with
    Django Channels / Redis to broadcast locations.
    """
    rider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='locations')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    accuracy = models.FloatField(blank=True, null=True, help_text='GPS accuracy in meters')
    heading = models.FloatField(blank=True, null=True, help_text='Direction in degrees')
    speed = models.FloatField(blank=True, null=True, help_text='Speed in m/s')

    recorded_at = models.DateTimeField(default=timezone.now, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']
        indexes = [models.Index(fields=['rider', 'recorded_at'])]

    def __str__(self):
        return f"{self.rider} @ {self.latitude},{self.longitude} ({self.recorded_at.isoformat()})"


class RiderWallet(models.Model):
    """Available delivery earnings for a rider, maintained with ledger entries."""
    rider = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='rider_wallet',
    )
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Rider wallet: {self.rider} ({self.balance} KES)"


class WithdrawalRequest(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PROCESSING = 'processing'
    STATUS_PAID = 'paid'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PROCESSING, 'Processing'),
        (STATUS_PAID, 'Paid'),
        (STATUS_FAILED, 'Failed'),
    ]

    rider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='rider_withdrawals',
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    phone_number = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
    conversation_id = models.CharField(max_length=128, blank=True, db_index=True)
    originator_conversation_id = models.CharField(max_length=128, blank=True)
    transaction_reference = models.CharField(max_length=128, blank=True)
    failure_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Withdrawal {self.id}: {self.amount} KES ({self.status})"


class RiderLedgerEntry(models.Model):
    TYPE_EARNING = 'earning'
    TYPE_WITHDRAWAL = 'withdrawal'
    TYPE_REFUND = 'refund'
    TYPE_CHOICES = [
        (TYPE_EARNING, 'Delivery earning'),
        (TYPE_WITHDRAWAL, 'Withdrawal'),
        (TYPE_REFUND, 'Withdrawal refund'),
    ]

    rider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='rider_ledger_entries',
    )
    order = models.ForeignKey(
        'orders.Order', null=True, blank=True, on_delete=models.PROTECT, related_name='rider_earnings'
    )
    withdrawal = models.ForeignKey(
        WithdrawalRequest, null=True, blank=True, on_delete=models.PROTECT, related_name='ledger_entries'
    )
    entry_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['rider', 'order'],
                condition=models.Q(entry_type='earning'),
                name='unique_rider_order_earning',
            ),
            models.UniqueConstraint(
                fields=['rider', 'withdrawal'],
                condition=models.Q(entry_type='withdrawal'),
                name='unique_rider_withdrawal_debit',
            ),
            models.UniqueConstraint(
                fields=['rider', 'withdrawal'],
                condition=models.Q(entry_type='refund'),
                name='unique_rider_withdrawal_refund',
            ),
        ]

    def __str__(self):
        return f"{self.rider}: {self.entry_type} {self.amount} KES"

