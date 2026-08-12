from django.contrib import admin

from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "file_ext", "human_size", "uploaded_by", "created_at")
    list_filter = ("category", "file_ext", "created_at")
    search_fields = ("title", "description")
    readonly_fields = ("file_size", "file_ext", "uploaded_by", "created_at", "updated_at")
