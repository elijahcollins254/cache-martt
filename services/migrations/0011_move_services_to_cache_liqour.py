from django.db import migrations


SHOP_NAME = 'Cache-Liqour'
SHOP_SLUG = 'cache-liqour'


def move_services_to_cache_liqour(apps, schema_editor):
    Service = apps.get_model('services', 'Service')
    Shop = apps.get_model('marketplace', 'Shop')

    shop = Shop.objects.filter(slug=SHOP_SLUG).first()
    if shop is None:
        shop = Shop.objects.filter(name__iexact=SHOP_NAME).first()

    if shop is None:
        shop = Shop.objects.create(
            name=SHOP_NAME,
            slug=SHOP_SLUG,
            description='Platform shop for the existing service catalogue.',
            status='active',
            is_verified=True,
        )
    else:
        updates = []
        if shop.name != SHOP_NAME:
            shop.name = SHOP_NAME
            updates.append('name')
        if shop.status != 'active':
            shop.status = 'active'
            updates.append('status')
        if not shop.is_verified:
            shop.is_verified = True
            updates.append('is_verified')
        if updates:
            shop.save(update_fields=updates)

    Service.objects.exclude(shop_id=shop.pk).update(shop_id=shop.pk)


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0001_initial'),
        ('services', '0010_service_shop'),
    ]

    operations = [
        migrations.RunPython(
            move_services_to_cache_liqour,
            reverse_code=migrations.RunPython.noop,
        ),
    ]