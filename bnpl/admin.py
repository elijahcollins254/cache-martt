from django.contrib import admin

from .models import BNPLAccount


@admin.register(BNPLAccount)
class BNPLAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_active', 'phone_number', 'credit_limit', 'current_balance', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('user__username', 'phone_number')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
