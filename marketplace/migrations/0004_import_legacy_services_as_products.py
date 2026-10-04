from django.db import migrations
from django.utils.text import slugify


def import_legacy_services_as_products(apps, schema_editor):
    Service = apps.get_model('services', 'Service')
    Shop = apps.get_model('marketplace', 'Shop')
    Product = apps.get_model('marketplace', 'Product')
    ProductCategory = apps.get_model('marketplace', 'ProductCategory')

    shop = Shop.objects.filter(slug='cache-liqour').first()
    if shop is None:
        shop = Shop.objects.filter(name__iexact='Cache-Liqour').first()
    if shop is None:
        raise RuntimeError('The Cache Liqour shop must exist before importing services as products.')

    for service in Service.objects.select_related('category').order_by('pk').iterator():
        shop_id = service.shop_id or shop.pk
        category_name = (
            service.category.name if service.category_id
            else (service.category_name or 'Services')
        )
        category = ProductCategory.objects.filter(name__iexact=category_name).first()
        if category is None:
            category_slug = slugify(category_name) or 'services'
            base_category_slug = category_slug
            suffix = 2
            while ProductCategory.objects.filter(slug=category_slug).exists():
                category_slug = f'{base_category_slug}-{suffix}'
                suffix += 1
            category = ProductCategory.objects.create(
                name=category_name,
                slug=category_slug,
            )

        product = Product.objects.filter(shop_id=shop_id, name=service.name).order_by('pk').first()
        product_slug = slugify(service.name) or f'service-{service.pk}'
        base_product_slug = product_slug
        if Product.objects.filter(shop_id=shop_id, slug=product_slug).exclude(pk=getattr(product, 'pk', None)).exists():
            product_slug = f'{base_product_slug}-{service.pk}'
            suffix = 2
            while Product.objects.filter(shop_id=shop_id, slug=product_slug).exclude(pk=getattr(product, 'pk', None)).exists():
                product_slug = f'{base_product_slug}-{service.pk}-{suffix}'
                suffix += 1

        values = {
            'shop_id': shop_id,
            'category_id': category.pk,
            'name': service.name,
            'slug': product_slug,
            'description': service.description or (product.description if product else ''),
            'price': service.price,
            'stock_quantity': 20,
            'image': service.image or (product.image if product else ''),
            'image_url': service.image_url or (product.image_url if product else ''),
            'is_active': service.is_active,
        }

        if product is None:
            Product.objects.create(**values)
        else:
            for field, value in values.items():
                setattr(product, field, value)
            product.save()


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0003_productcategory_and_product_category'),
        ('services', '0011_move_services_to_cache_liqour'),
    ]

    operations = [
        migrations.RunPython(
            import_legacy_services_as_products,
            reverse_code=migrations.RunPython.noop,
        ),
    ]