from django.contrib import admin

from .models import Bar, HeatNumber, MaterialLot, MaterialTransaction


class MaterialLotInline(admin.TabularInline):
    model = MaterialLot
    extra = 0
    fields = ("lot_no", "product", "quantity_received", "quantity_remaining", "status")


class BarInline(admin.TabularInline):
    model = Bar
    extra = 0


@admin.register(HeatNumber)
class HeatNumberAdmin(admin.ModelAdmin):
    list_display = ("heat_no", "supplier", "grade", "mfg_date", "mill_cert_no")
    list_filter = ("supplier",)
    search_fields = ("heat_no", "grade", "mill_cert_no")
    inlines = [MaterialLotInline]


@admin.register(MaterialLot)
class MaterialLotAdmin(admin.ModelAdmin):
    list_display = (
        "lot_no",
        "heat",
        "product",
        "quantity_received",
        "quantity_remaining",
        "received_date",
        "status",
    )
    list_filter = ("status", "product")
    search_fields = ("lot_no", "heat__heat_no", "dc_no")
    inlines = [BarInline]
    readonly_fields = ("created_at", "updated_at")


@admin.register(MaterialTransaction)
class MaterialTransactionAdmin(admin.ModelAdmin):
    list_display = ("lot", "txn_type", "quantity", "txn_date", "reference_type", "remarks")
    list_filter = ("txn_type",)
    search_fields = ("lot__lot_no", "reference_id", "remarks")


@admin.register(Bar)
class BarAdmin(admin.ModelAdmin):
    list_display = ("lot", "bar_no", "weight", "status")
    list_filter = ("status",)
    search_fields = ("lot__lot_no", "bar_no")
