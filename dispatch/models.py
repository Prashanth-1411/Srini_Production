from django.conf import settings
from django.db import models

from masters.models import Customer, TimeStampedModel
from production.models import ProductionLot


class Dispatch(TimeStampedModel):
    STATUS_DISPATCHED = "DISPATCHED"
    STATUS_PARTIAL = "PARTIAL"
    STATUS_CANCELLED = "CANCELLED"
    STATUS_CHOICES = [
        (STATUS_DISPATCHED, "Dispatched"),
        (STATUS_PARTIAL, "Partial"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    dispatch_no = models.CharField("Dispatch number", max_length=50, unique=True)
    customer = models.ForeignKey(
        Customer, on_delete=models.PROTECT, related_name="dispatches"
    )
    invoice_no = models.CharField("Invoice number", max_length=50, blank=True)
    dispatch_date = models.DateField()
    vehicle_no = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DISPATCHED)
    remarks = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dispatches_created",
    )

    class Meta:
        ordering = ["-dispatch_date", "-created_at"]
        indexes = [models.Index(fields=["status"]), models.Index(fields=["customer"])]

    def __str__(self):
        return f"{self.dispatch_no} ({self.customer})"


class DispatchItem(TimeStampedModel):
    dispatch = models.ForeignKey(
        Dispatch, on_delete=models.CASCADE, related_name="items"
    )
    production_lot = models.ForeignKey(
        ProductionLot, on_delete=models.PROTECT, related_name="dispatch_items"
    )
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["dispatch", "production_lot"], name="uniq_dispatch_lot"
            )
        ]

    def __str__(self):
        return f"{self.dispatch.dispatch_no} / {self.production_lot.lot_no} x{self.quantity}"
