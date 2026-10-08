from django.contrib import admin
from .models import RiderProfile, RiderLocation, RiderWallet, RiderLedgerEntry, WithdrawalRequest

@admin.register(RiderProfile)
class RiderProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "display_name", "phone", "vehicle_type", "vehicle_reg", "is_active")
    search_fields = ("display_name", "user__username", "phone", "vehicle_reg")
    list_filter = ("vehicle_type", "is_active")
    readonly_fields = ("created_at", "updated_at")

@admin.register(RiderLocation)
class RiderLocationAdmin(admin.ModelAdmin):
    list_display = ("id", "rider", "latitude", "longitude", "recorded_at")
    search_fields = ("rider__username",)
    list_filter = ("recorded_at",)
    readonly_fields = ("created_at",)
    ordering = ("-recorded_at",)


@admin.register(RiderWallet)
class RiderWalletAdmin(admin.ModelAdmin):
    list_display = ("rider", "balance", "updated_at")
    search_fields = ("rider__username", "rider__phone")
    readonly_fields = ("rider", "balance", "created_at", "updated_at")


@admin.register(RiderLedgerEntry)
class RiderLedgerEntryAdmin(admin.ModelAdmin):
    list_display = ("id", "rider", "entry_type", "amount", "order", "withdrawal", "created_at")
    list_filter = ("entry_type", "created_at")
    search_fields = ("rider__username", "order__code", "withdrawal__id", "description")
    readonly_fields = tuple(field.name for field in RiderLedgerEntry._meta.fields)


@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "rider", "amount", "phone_number", "status", "transaction_reference", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("rider__username", "phone_number", "conversation_id", "transaction_reference")
    readonly_fields = tuple(field.name for field in WithdrawalRequest._meta.fields)
