from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0025_orderreview'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='pickup_confirmed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]