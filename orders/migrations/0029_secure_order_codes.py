from django.db import migrations
import secrets


ALPHABET = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'


def secure_code():
    parts = [''.join(secrets.choice(ALPHABET) for _ in range(4)) for _ in range(3)]
    return f"CM-{'-'.join(parts)}"


def rotate_order_codes(apps, schema_editor):
    Order = apps.get_model('orders', 'Order')
    Payment = apps.get_model('payments', 'Payment')
    used_codes = set(Order.objects.values_list('code', flat=True))

    for order in Order.objects.all().iterator():
        old_code = order.code
        new_code = secure_code()
        while new_code in used_codes:
            new_code = secure_code()
        used_codes.discard(old_code)
        used_codes.add(new_code)
        order.code = new_code
        order.save(update_fields=['code'])

        payments = Payment.objects.filter(raw_payload__order_reference=old_code)
        for payment in payments:
            payload = dict(payment.raw_payload or {})
            payload['order_reference'] = new_code
            payment.raw_payload = payload
            payment.save(update_fields=['raw_payload'])


class Migration(migrations.Migration):
    dependencies = [
        ('orders', '0028_order_partially_paid'),
        ('payments', '0004_alter_bnpluser_credit_limit'),
    ]

    operations = [
        migrations.RunPython(rotate_order_codes, migrations.RunPython.noop),
    ]