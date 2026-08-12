from django.conf import settings
from django.db import models

from masters.models import Machine, TimeStampedModel
from production.models import ProductionLot


class ProcessRecord(TimeStampedModel):
    TYPE_GRINDING = "GRINDING"
    TYPE_HARD_FACING = "HARD_FACING"
    TYPE_CHOICES = [
        (TYPE_GRINDING, "Grinding"),
        (TYPE_HARD_FACING, "Hard-facing"),
    ]

    record_no = models.CharField("Record number", max_length=50, unique=True)
    process_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    production_lot = models.ForeignKey(
        ProductionLot, on_delete=models.PROTECT, related_name="process_records"
    )
    machine = models.ForeignKey(
        Machine, on_delete=models.PROTECT, null=True, blank=True, related_name="process_records"
    )
    operator = models.CharField(max_length=150, blank=True)
    quantity = models.PositiveIntegerField(default=0)
    process_date = models.DateField(null=True, blank=True)
    remarks = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="process_records_created",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["process_type"]),
            models.Index(fields=["production_lot"]),
        ]

    def __str__(self):
        return f"{self.record_no} ({self.get_process_type_display()})"
