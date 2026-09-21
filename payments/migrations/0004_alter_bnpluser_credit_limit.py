from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('payments', '0003_tradein'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bnpluser',
            name='credit_limit',
            field=models.DecimalField(decimal_places=2, default=50.0, max_digits=10),
        ),
    ]
