from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient

from .models import MerchantProfile, Shop, Product

User = get_user_model()


class MarketplaceModelsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='merchant1',
            email='merchant1@example.com',
            password='SecurePass123',
            phone='+254712345678',
            role='merchant',
        )
        self.merchant = MerchantProfile.objects.create(
            user=self.user,
            business_name='Fresh Basket',
            merchant_username='freshbasket',
            phone='+254712345678',
            status='verified',
        )

    def test_shop_slug_and_username_are_unique(self):
        shop = Shop.objects.create(
            owner=self.merchant,
            name='Fresh Basket Shop',
            slug='fresh-basket-shop',
            description='Groceries and home goods',
            is_verified=True,
        )
        self.assertEqual(shop.owner.merchant_username, 'freshbasket')

    def test_product_requires_shop_and_price(self):
        with self.assertRaises(ValidationError):
            product = Product(
                shop=None,
                name='Tomatoes',
                slug='tomatoes',
                price='0.00',
            )
            product.full_clean()

    def test_product_slug_is_generated_from_name_when_missing(self):
        shop = Shop.objects.create(
            owner=self.merchant,
            name='Fresh Basket Shop',
            slug='fresh-basket-shop',
            description='Groceries and home goods',
            is_verified=True,
        )
        product = Product.objects.create(
            shop=shop,
            name='Fresh Avocado',
            price='120.00',
        )
        self.assertEqual(product.slug, 'fresh-avocado')


class MarketplaceAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='merchant_api_user',
            email='merchant_api@example.com',
            password='SecurePass123',
            phone='+254712345678',
            role='merchant',
        )

    def test_merchant_registration_endpoint_creates_profile(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            '/marketplace/merchants/register/',
            {
                'merchant_username': 'freshbasket',
                'business_name': 'Fresh Basket',
                'phone': '+254712345678',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(MerchantProfile.objects.filter(merchant_username='freshbasket').exists())

    def test_authenticated_user_can_create_shop(self):
        self.client.force_authenticate(user=self.user)
        MerchantProfile.objects.create(
            user=self.user,
            merchant_username='freshbasket',
            business_name='Fresh Basket',
            phone='+254712345678',
            status='verified',
        )

        response = self.client.post(
            '/marketplace/shops/',
            {
                'name': 'Fresh Basket Shop',
                'slug': 'fresh-basket-shop',
                'description': 'Groceries and home goods',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(Shop.objects.filter(slug='fresh-basket-shop').exists())

    def test_authenticated_merchant_can_create_product(self):
        self.client.force_authenticate(user=self.user)
        merchant = MerchantProfile.objects.create(
            user=self.user,
            merchant_username='freshbasket',
            business_name='Fresh Basket',
            phone='+254712345678',
            status='verified',
        )
        shop = Shop.objects.create(
            owner=merchant,
            name='Fresh Basket Shop',
            slug='fresh-basket-shop',
            description='Groceries and home goods',
            is_verified=True,
            status='active',
        )

        response = self.client.post(
            '/marketplace/products/',
            {
                'shop': shop.id,
                'name': 'Fresh Avocado',
                'price': '120.00',
                'description': 'Farm fresh avocados',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(Product.objects.filter(slug='fresh-avocado').exists())

    def test_public_products_endpoint_includes_shop_identity(self):
        merchant = MerchantProfile.objects.create(
            user=self.user,
            merchant_username='freshbasket',
            business_name='Fresh Basket',
            phone='+254712345678',
            status='verified',
        )
        shop = Shop.objects.create(
            owner=merchant,
            name='Fresh Basket Shop',
            slug='fresh-basket-shop',
            description='Groceries and home goods',
            is_verified=True,
            status='active',
        )
        Product.objects.create(
            shop=shop,
            name='Fresh Avocado',
            slug='fresh-avocado',
            price='120.00',
            description='Farm fresh avocados',
            is_active=True,
        )

        response = self.client.get('/marketplace/products/')

        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)
        self.assertIsInstance(response.data[0]['shop'], dict)
        self.assertEqual(response.data[0]['shop']['merchant_username'], 'freshbasket')
