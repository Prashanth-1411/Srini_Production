from django.contrib import admin

from .models import CNCJob, ProductionLot


@admin.register(CNCJob)
class CNCJobAdmin(admin.ModelAdmin):
    list_display = ("job_no", "customer", "product", "quantity", "due_date", "status")
    list_filter = ("status", "customer")
    search_fields = ("job_no", "order_no", "product__code", "product__name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(ProductionLot)
class ProductionLotAdmin(admin.ModelAdmin):
    list_display = (
        "lot_no",
        "job",
        "material_lot",
        "qty_started",
        "qty_ok",
        "status",
    )
    list_filter = ("status", "job__customer")
    search_fields = ("lot_no", "job__job_no", "material_lot__lot_no")
    readonly_fields = ("created_at", "updated_at")
