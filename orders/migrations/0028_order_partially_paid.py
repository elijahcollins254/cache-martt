from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('orders', '0027_delivery_status_flow'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending_payment', 'Pending Payment'),
                    ('partially_paid', 'Partially Paid'),
                    ('requested', 'Order Placed'),
                    ('pending_assignment', 'Finding a Rider'),
                    ('assigned_pickup', 'Rider Assigned'),
                    ('accepted_delivery', 'Rider Confirmed'),
                    ('picked', 'Picked Up'),
                    ('at_gate', 'At the Gate'),
                    ('delivered', 'Delivered'),
                    ('cancelled', 'Cancelled'),
                ],
                default='requested',
                max_length=20,
            ),
        ),
    ]