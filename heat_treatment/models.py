from django.conf import settings
from django.db import models

from masters.models import Furnace, TimeStampedModel
from production.models import ProductionLot


class FurnaceBatch(TimeStampedModel):
    STATUS_SCHEDULED = "SCHEDULED"
    STATUS_IN_PROGRESS = "IN_PROGRESS"
    STATUS_HOLD = "HOLD"
    STATUS_RELEASED = "RELEASED"
    STATUS_CHOICES = [
        (STATUS_SCHEDULED, "Scheduled"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_HOLD, "On Hold"),
        (STATUS_RELEASED, "Released"),
    ]

    batch_no = models.CharField("Batch number", max_length=50, unique=True)
    furnace = models.ForeignKey(
        Furnace, on_delete=models.PROTECT, related_name="furnace_batches"
    )
    production_lot = models.ForeignKey(
        ProductionLot, on_delete=models.PROTECT, related_name="furnace_batches"
    )
    charge_date = models.DateField(null=True, blank=True)
    discharge_date = models.DateField(null=True, blank=True)
    temperature = models.CharField("Temperature", max_length=100, blank=True)
    duration_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    hardness_before = models.CharField(max_length=100, blank=True)
    hardness_after = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SCHEDULED)
    remarks = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="furnace_batches_created",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["production_lot"]),
        ]

    def __str__(self):
        return f"{self.batch_no} ({self.furnace})"
