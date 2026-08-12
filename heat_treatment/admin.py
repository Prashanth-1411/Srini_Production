from django.contrib import admin

from .models import FurnaceBatch


@admin.register(FurnaceBatch)
class FurnaceBatchAdmin(admin.ModelAdmin):
    list_display = ("batch_no", "furnace", "production_lot", "charge_date", "temperature", "status")
    list_filter = ("status", "furnace")
    search_fields = ("batch_no", "production_lot__lot_no")
    readonly_fields = ("created_at", "updated_at")
