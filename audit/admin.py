from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "timestamp",
        "username",
        "action",
        "module",
        "model",
        "record_id",
        "ip_address",
    )
    list_filter = ("action", "module", "timestamp")
    search_fields = ("username", "record_id", "model", "module")
    readonly_fields = (
        "user",
        "username",
        "timestamp",
        "ip_address",
        "module",
        "action",
        "model",
        "record_id",
        "old_value",
        "new_value",
    )
    date_hierarchy = "timestamp"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
