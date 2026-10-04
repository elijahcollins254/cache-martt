from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MerchantProfileViewSet, ProductViewSet, ShopCategoryViewSet, ShopViewSet


router = DefaultRouter()
router.register('merchants', MerchantProfileViewSet, basename='merchant')
router.register('categories', ShopCategoryViewSet, basename='shop-category')
router.register('shops', ShopViewSet, basename='shop')
router.register('products', ProductViewSet, basename='product')

urlpatterns = [path('', include(router.urls))]