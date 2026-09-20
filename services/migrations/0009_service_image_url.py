from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0008_alter_service_options_service_category_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='image_url',
            field=models.URLField(blank=True, help_text='Remote image URL (preferred over uploaded image)', null=True),
        ),
    ]