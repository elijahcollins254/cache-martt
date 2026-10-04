from django.contrib import admin

from .models import MerchantProfile, Product, Shop, ShopCategory


@admin.register(MerchantProfile)
class MerchantProfileAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'merchant_username', 'user', 'status', 'is_verified')
    list_filter = ('status', 'is_verified')
    search_fields = ('business_name', 'merchant_username', 'user__email')


@admin.register(ShopCategory)
class ShopCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'owner', 'status', 'is_verified', 'created_at')
    list_filter = ('category', 'status', 'is_verified')
    search_fields = ('name', 'slug', 'owner__business_name')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'shop', 'price', 'stock_quantity', 'is_active')
    list_filter = ('shop', 'is_active')
    search_fields = ('name', 'description', 'shop__name')
    prepopulated_fields = {'slug': ('name',)}