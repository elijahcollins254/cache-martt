# services/serializers.py
from rest_framework import serializers
from .models import Service


class ServiceSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.slug', read_only=True, allow_null=True)

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
        fields = ["id", "name", "category", "price", "description", "image", "image_url"]
        read_only_fields = ["id"]
