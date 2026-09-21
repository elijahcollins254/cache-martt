from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from decimal import Decimal


def copy_existing_accounts(apps, schema_editor):
    LegacyAccount = apps.get_model('payments', 'BNPLUser')
    Account = apps.get_model('bnpl', 'BNPLAccount')
    for legacy in LegacyAccount.objects.all().iterator():
        starting_limit = legacy.credit_limit
        if starting_limit == Decimal('5000.00'):
            starting_limit = Decimal('50.00')
        Account.objects.create(
            user_id=legacy.user_id,
            is_active=legacy.is_active,
            phone_number=legacy.phone_number,
            credit_limit=starting_limit,
            current_balance=legacy.current_balance,
            created_at=legacy.created_at,
            updated_at=legacy.updated_at,
        )


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payments', '0003_tradein'),
    ]

    operations = [
        migrations.CreateModel(
            name='BNPLAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('phone_number', models.CharField(max_length=32)),
                ('credit_limit', models.DecimalField(decimal_places=2, default=Decimal('50.00'), max_digits=10)),
                ('current_balance', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='bnpl_account', to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'BNPL account', 'verbose_name_plural': 'BNPL accounts'},
        ),
        migrations.RunPython(copy_existing_accounts, migrations.RunPython.noop),
    ]
