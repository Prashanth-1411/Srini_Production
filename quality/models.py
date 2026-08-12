from django.conf import settings
from django.db import models

from masters.models import TimeStampedModel
from production.models import ProductionLot


class QCInspection(TimeStampedModel):
    RESULT_PASS = "PASS"
    RESULT_REJECT = "REJECT"
    RESULT_HOLD = "HOLD"
    RESULT_CHOICES = [
        (RESULT_PASS, "Pass"),
        (RESULT_REJECT, "Reject"),
        (RESULT_HOLD, "Hold"),
    ]

    inspection_no = models.CharField("Inspection number", max_length=50, unique=True)
    production_lot = models.ForeignKey(
        ProductionLot, on_delete=models.PROTECT, related_name="qc_inspections"
    )
    inspector = models.CharField(max_length=150, blank=True)
    inspection_date = models.DateField(null=True, blank=True)
    qty_checked = models.PositiveIntegerField(default=0)
    qty_passed = models.PositiveIntegerField(default=0)
    qty_rework = models.PositiveIntegerField(default=0)
    qty_rejected = models.PositiveIntegerField(default=0)
    result = models.CharField(max_length=10, choices=RESULT_CHOICES, default=RESULT_PASS)
    remarks = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="qc_inspections_created",
    )

    class Meta:
        ordering = ["-inspection_date", "-created_at"]
        indexes = [
            models.Index(fields=["result"]),
            models.Index(fields=["production_lot"]),
        ]

    def __str__(self):
        return f"{self.inspection_no} ({self.get_result_display()})"


class Rework(TimeStampedModel):
    production_lot = models.ForeignKey(
        ProductionLot, on_delete=models.PROTECT, related_name="rework_records"
    )
    inspection = models.ForeignKey(
        QCInspection, on_delete=models.SET_NULL, null=True, blank=True, related_name="rework_records"
    )
    quantity = models.PositiveIntegerField(default=0)
    reason = models.CharField(max_length=255, blank=True)
    rework_date = models.DateField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rework_records_created",
    )

    class Meta:
        ordering = ["-rework_date", "-created_at"]

    def __str__(self):
        return f"Rework {self.production_lot} x{self.quantity}"


class Scrap(TimeStampedModel):
    production_lot = models.ForeignKey(
        ProductionLot, on_delete=models.PROTECT, related_name="scrap_records"
    )
    inspection = models.ForeignKey(
        QCInspection, on_delete=models.SET_NULL, null=True, blank=True, related_name="scrap_records"
    )
    quantity = models.PositiveIntegerField(default=0)
    reason = models.CharField(max_length=255, blank=True)
    scrap_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="scrap_records_created",
    )

    class Meta:
        ordering = ["-scrap_date", "-created_at"]

    def __str__(self):
        return f"Scrap {self.production_lot} x{self.quantity}"
