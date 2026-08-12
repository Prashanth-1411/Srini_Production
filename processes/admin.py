from django.contrib import admin

from .models import ProcessRecord


@admin.register(ProcessRecord)
class ProcessRecordAdmin(admin.ModelAdmin):
    list_display = ("record_no", "process_type", "production_lot", "machine", "quantity", "process_date")
    list_filter = ("process_type",)
    search_fields = ("record_no", "production_lot__lot_no")
    readonly_fields = ("created_at", "updated_at")
