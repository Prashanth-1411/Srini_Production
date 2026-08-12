import os

from django.conf import settings
from django.db import models

from .validators import validate_document_file


class Document(models.Model):
    CATEGORY_INWARD = "INWARD"
    CATEGORY_OUTWARD = "OUTWARD"
    CATEGORY_MATERIAL_CERT = "MATERIAL_CERT"
    CATEGORY_TEST_REPORT = "TEST_REPORT"
    CATEGORY_HEAT_TREATMENT = "HEAT_TREATMENT"
    CATEGORY_INSPECTION = "INSPECTION"
    CATEGORY_DISPATCH = "DISPATCH"
    CATEGORY_OTHER = "OTHER"

    CATEGORY_CHOICES = [
        (CATEGORY_INWARD, "Inward / Goods Received"),
        (CATEGORY_OUTWARD, "Outward / Goods Dispatched"),
        (CATEGORY_MATERIAL_CERT, "Material Certificate (MTC)"),
        (CATEGORY_TEST_REPORT, "Test Report"),
        (CATEGORY_HEAT_TREATMENT, "Heat Treatment Chart"),
        (CATEGORY_INSPECTION, "Inspection Report"),
        (CATEGORY_DISPATCH, "Dispatch Document"),
        (CATEGORY_OTHER, "Other"),
    ]

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default=CATEGORY_OTHER)
    description = models.TextField(blank=True)
    file = models.FileField(
        upload_to="documents/%Y/%m/",
        validators=[validate_document_file],
        help_text="Only PDF (.pdf) and Excel (.xlsx, .xls) files are allowed.",
    )
    file_size = models.PositiveBigIntegerField(default=0, editable=False)
    file_ext = models.CharField(max_length=10, editable=False, default="")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="uploaded_documents",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.file:
            self.file_ext = os.path.splitext(self.file.name)[1].lower()
            try:
                self.file_size = self.file.size
            except (OSError, ValueError):
                pass
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        stored = self.file
        super().delete(*args, **kwargs)
        if stored:
            try:
                stored.delete(save=False)
            except (OSError, ValueError):
                pass

    @property
    def is_pdf(self):
        return self.file_ext == ".pdf"

    @property
    def is_excel(self):
        return self.file_ext in (".xlsx", ".xls")

    @property
    def filename(self):
        return os.path.basename(self.file.name)

    def human_size(self):
        size = self.file_size
        if size >= 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        if size >= 1024:
            return f"{size / 1024:.1f} KB"
        return f"{size} B"
