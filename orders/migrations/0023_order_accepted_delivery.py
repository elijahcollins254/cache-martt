from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0022_order_applied_offer_order_free_delivery_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending_payment', 'Pending Payment'),
                    ('requested', 'Order Requested'),
                    ('pending_assignment', 'Pending Pickup Assignment'),
                    ('assigned_pickup', 'Assigned for Pickup'),
                    ('picked', 'Picked Up'),
                    ('in_progress', 'In Progress'),
                    ('washed', 'Washed'),
                    ('folded', 'Folded'),
                    ('ready', 'Ready for Delivery'),
                    ('pending_delivery', 'Pending Delivery Assignment'),
                    ('assigned_delivery', 'Assigned for Delivery'),
                    ('accepted_delivery', 'Accepted for Delivery'),
                    ('delivered', 'Delivered'),
                    ('cancelled', 'Cancelled'),
                ],
                default='requested',
                max_length=20,
            ),
        ),
    ]