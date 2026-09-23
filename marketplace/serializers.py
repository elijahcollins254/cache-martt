from django.utils.text import slugify
from rest_framework import serializers

from .models import MerchantProfile, Shop, Product


class MerchantProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MerchantProfile
        fields = [
            'id',
            'merchant_username',
            'business_name',
            'phone',
            'email',
            'description',
            'status',
            'is_verified',
            'created_at',
        ]
        read_only_fields = ['id', 'status', 'is_verified', 'created_at']


class ShopSerializer(serializers.ModelSerializer):
    owner = MerchantProfileSerializer(read_only=True)
    merchant_username = serializers.SerializerMethodField()

    class Meta:
        model = Shop
        fields = [
            'id',
            'owner',
            'merchant_username',
            'name',
            'slug',
            'description',
            'logo',
            'banner',
            'is_verified',
            'status',
            'created_at',
        ]
        read_only_fields = ['id', 'owner', 'merchant_username', 'created_at']

    def get_merchant_username(self, obj):
        return obj.owner.merchant_username


class ProductSerializer(serializers.ModelSerializer):
    shop = ShopSerializer(read_only=True)
    shop_id = serializers.PrimaryKeyRelatedField(
        source='shop',
        queryset=Shop.objects.all(),
        write_only=True,
    )
    slug = serializers.SlugField(required=False, allow_blank=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'shop',
            'shop_id',
            'name',
            'slug',
            'description',
            'price',
            'stock_quantity',
            'image',
            'image_url',
            'is_active',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at', 'shop']

    def validate(self, attrs):
        attrs = dict(attrs)
        attrs['slug'] = attrs.get('slug') or slugify(attrs.get('name', ''))
        if not attrs['slug']:
            raise serializers.ValidationError({'slug': 'A valid product slug is required.'})
        return attrs
