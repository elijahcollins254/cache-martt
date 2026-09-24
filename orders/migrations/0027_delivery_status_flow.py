from django.db import migrations
from django.db import models


def move_legacy_workflow_statuses(apps, schema_editor):
    Order = apps.get_model('orders', 'Order')
    legacy_statuses = {
        'in_progress': 'picked',
        'washed': 'picked',
        'folded': 'picked',
        'ready': 'picked',
        'pending_delivery': 'picked',
        'assigned_delivery': 'picked',
    }
    for old_status, new_status in legacy_statuses.items():
        Order.objects.filter(status=old_status).update(status=new_status)


class Migration(migrations.Migration):
    dependencies = [
        ('orders', '0026_order_pickup_confirmed_at'),
    ]

    operations = [
        migrations.RunPython(move_legacy_workflow_statuses, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending_payment', 'Pending Payment'),
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