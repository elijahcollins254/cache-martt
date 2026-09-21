from decimal import Decimal

from django.conf import settings
from django.db import models


class BNPLAccount(models.Model):
    """A user's BNPL enrollment, balance, and approved credit limit."""

    INITIAL_CREDIT_LIMIT = Decimal('50.00')

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bnpl_account',
    )
    is_active = models.BooleanField(default=True)
    phone_number = models.CharField(max_length=32)
    credit_limit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=INITIAL_CREDIT_LIMIT,
    )
    current_balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'BNPL account'
        verbose_name_plural = 'BNPL accounts'

    def __str__(self):
        return f'BNPL - {self.user.username}'
