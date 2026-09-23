from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0023_order_accepted_delivery'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivery_code_hash',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_code_sent_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='gate_notified_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]