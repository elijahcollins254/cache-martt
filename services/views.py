from rest_framework import viewsets, permissions, filters
from .models import Service, ServiceCategory
from .serializers import ServiceCategorySerializer, ServiceSerializer


class ServiceCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Expose active service categories for catalogue filters."""
    queryset = ServiceCategory.objects.filter(is_active=True).order_by('name')
    serializer_class = ServiceCategorySerializer
    permission_classes = [permissions.AllowAny]

class ServiceViewSet(viewsets.ModelViewSet):
    """List and manage service catalogue (laundry, duvet, carpet, fumigation, etc.)"""
    queryset = Service.objects.all().order_by('category', 'name')
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'category', 'description']
    ordering_fields = ['price', 'name']

    # public read access, authenticated required to create/update/delete
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), permissions.IsAdminUser()]