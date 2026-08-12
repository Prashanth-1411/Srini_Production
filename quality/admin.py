from django.contrib import admin

from .models import QCInspection, Rework, Scrap


@admin.register(QCInspection)
class QCInspectionAdmin(admin.ModelAdmin):
    list_display = (
        "inspection_no",
        "production_lot",
        "inspection_date",
        "qty_checked",
        "qty_passed",
        "result",
    )
    list_filter = ("result",)
    search_fields = ("inspection_no", "production_lot__lot_no")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Rework)
class ReworkAdmin(admin.ModelAdmin):
    list_display = ("production_lot", "quantity", "reason", "rework_date", "completed")
    list_filter = ("completed",)
    search_fields = ("production_lot__lot_no", "reason")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Scrap)
class ScrapAdmin(admin.ModelAdmin):
    list_display = ("production_lot", "quantity", "reason", "scrap_date")
    search_fields = ("production_lot__lot_no", "reason")
    readonly_fields = ("created_at", "updated_at")
