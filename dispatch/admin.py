from django.contrib import admin

from .models import Dispatch, DispatchItem


class DispatchItemInline(admin.TabularInline):
    model = DispatchItem
    extra = 1


@admin.register(Dispatch)
class DispatchAdmin(admin.ModelAdmin):
    list_display = ("dispatch_no", "customer", "invoice_no", "dispatch_date", "status")
    list_filter = ("status", "customer")
    search_fields = ("dispatch_no", "invoice_no", "customer__name")
    readonly_fields = ("created_at", "updated_at")
    inlines = [DispatchItemInline]


@admin.register(DispatchItem)
class DispatchItemAdmin(admin.ModelAdmin):
    list_display = ("dispatch", "production_lot", "quantity")
    search_fields = ("dispatch__dispatch_no", "production_lot__lot_no")
