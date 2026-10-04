# services/serializers.py
from rest_framework import serializers
from .models import Service, ServiceCategory
from marketplace.models import Shop
from marketplace.serializers import ShopSerializer


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ["id", "name", "slug"]


class ServiceSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.slug', read_only=True, allow_null=True)
    shop = ShopSerializer(read_only=True)
    shop_id = serializers.PrimaryKeyRelatedField(
        source='shop', queryset=Shop.objects.all(), write_only=True, required=False
    )

    def to_representation(self, instance):
        """Prefer a remote image URL and retain compatibility with uploaded images."""
        representation = super().to_representation(instance)
        if not representation.get('image_url') and instance.image:
            request = self.context.get('request')
            if request:
                representation['image_url'] = request.build_absolute_uri(instance.image.url)
            else:
                representation['image_url'] = instance.image.url
        return representation

    class Meta:
        model = Service
        fields = ["id", "name", "category", "shop", "shop_id", "price", "description", "image", "image_url"]
        read_only_fields = ["id"]
