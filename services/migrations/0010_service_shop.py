from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0001_initial'),
        ('services', '0009_service_image_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='shop',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='services',
                to='marketplace.shop',
            ),
        ),
    ]
