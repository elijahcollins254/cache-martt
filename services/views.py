from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from marketplace.models import Product
from marketplace.serializers import ShopSerializer
from .models import Service, ServiceCategory
from .serializers import ServiceCategorySerializer, ServiceSerializer


class ServiceCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Expose active service categories for catalogue filters."""
    queryset = ServiceCategory.objects.filter(is_active=True).order_by('name')
    serializer_class = ServiceCategorySerializer
    permission_classes = [permissions.AllowAny]


class ServiceViewSet(viewsets.ModelViewSet):
    """List and manage service catalogue (laundry, duvet, carpet, fumigation, etc.)"""
    queryset = Service.objects.select_related(
        'category', 'shop', 'shop__category', 'shop__owner'
    ).order_by('category', 'name')
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'category', 'description']
    ordering_fields = ['price', 'name']

    def get_queryset(self):
        queryset = super().get_queryset()
        shop_slug = self.request.query_params.get('shop')
        if shop_slug:
            queryset = queryset.filter(shop__slug=shop_slug)
        if self.action in ['list', 'retrieve']:
            queryset = queryset.filter(is_active=True)
            queryset = queryset.exclude(shop__isnull=True)
            queryset = queryset.filter(shop__status='active')
            if not self.request.user.is_authenticated:
                queryset = queryset.filter(shop__is_verified=True)
        return queryset

    @action(detail=False, methods=['get'], url_path='catalog')
    def catalog(self, request):
        services = self.get_queryset().filter(is_active=True)
        products = Product.objects.filter(is_active=True).select_related(
            'shop', 'shop__category', 'shop__owner', 'shop__owner__user'
        )
        if not request.user.is_authenticated:
            products = products.filter(shop__is_verified=True, shop__status='active')

        catalog = []

        for service in services:
            catalog.append({
                'id': service.id,
                'type': 'service',
                'name': service.name,
                'category': service.category.slug if service.category else (service.category_name or 'Services'),
                'description': service.description,
                'price': float(service.price),
                'image_url': service.image_url or (request.build_absolute_uri(service.image.url) if service.image else None),
                'shop': ShopSerializer(service.shop, context={'request': request}).data if service.shop else None,
            })

        for product in products:
            catalog.append({
                'id': product.id,
                'type': 'product',
                'name': product.name,
                'category': product.category.slug if product.category else 'Products',
                'category_name': product.category.name if product.category else 'Products',
                'shop_category': product.shop.category.slug if product.shop and product.shop.category else None,
                'description': product.description,
                'price': float(product.price),
                'image_url': product.image_url or (request.build_absolute_uri(product.image.url) if product.image else None),
                'shop': ShopSerializer(product.shop, context={'request': request}).data if product.shop else None,
            })

        catalog.sort(key=lambda item: (item['name'] or '').lower())
        return Response(catalog)

    # public read access, authenticated required to create/update/delete
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'catalog']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), permissions.IsAdminUser()]