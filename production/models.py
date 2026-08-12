from django.conf import settings
from django.db import models

from masters.models import Customer, Machine, Product, TimeStampedModel
from materials.models import MaterialLot


class CNCJob(TimeStampedModel):
    STATUS_PLANNED = "PLANNED"
    STATUS_IN_PROGRESS = "IN_PROGRESS"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_CLOSED = "CLOSED"
    STATUS_CHOICES = [
        (STATUS_PLANNED, "Planned"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CLOSED, "Closed"),
    ]

    job_no = models.CharField("Job number", max_length=50, unique=True)
    customer = models.ForeignKey(
        Customer, on_delete=models.PROTECT, related_name="cnc_jobs"
    )
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="cnc_jobs"
    )
    order_no = models.CharField("Order number", max_length=50, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PLANNED)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["status"]), models.Index(fields=["job_no"])]

    def __str__(self):
        return f"{self.job_no} - {self.product} ({self.customer})"


class ProductionLot(TimeStampedModel):
    STATUS_IN_PROGRESS = "IN_PROGRESS"
    STATUS_QC_PENDING = "QC_PENDING"
    STATUS_QC_APPROVED = "QC_APPROVED"
    STATUS_QC_REJECTED = "QC_REJECTED"
    STATUS_DISPATCHED = "DISPATCHED"
    STATUS_CLOSED = "CLOSED"
    STATUS_CHOICES = [
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_QC_PENDING, "QC Pending"),
        (STATUS_QC_APPROVED, "QC Approved"),
        (STATUS_QC_REJECTED, "QC Rejected"),
        (STATUS_DISPATCHED, "Dispatched"),
        (STATUS_CLOSED, "Closed"),
    ]

    lot_no = models.CharField("Production lot number", max_length=50, unique=True)
    job = models.ForeignKey(CNCJob, on_delete=models.PROTECT, related_name="production_lots")
    material_lot = models.ForeignKey(
        MaterialLot, on_delete=models.PROTECT, related_name="production_lots"
    )
    machine = models.ForeignKey(
        Machine, on_delete=models.PROTECT, null=True, blank=True, related_name="production_lots"
    )
    operator = models.CharField(max_length=150, blank=True)
    material_qty = models.DecimalField(
        "Material consumed", max_digits=12, decimal_places=3, default=0,
        help_text="Weight of raw material consumed from the lot (kg).",
    )
    qty_started = models.PositiveIntegerField(default=0)
    qty_ok = models.PositiveIntegerField(default=0)
    qty_rework = models.PositiveIntegerField(default=0)
    qty_scrap = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_IN_PROGRESS)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    remarks = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="production_lots_created",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["material_lot"]),
            models.Index(fields=["job"]),
        ]

    def __str__(self):
        return f"{self.lot_no} - {self.job}"

    @property
    def qty_total(self):
        return self.qty_ok + self.qty_rework + self.qty_scrap

    @property
    def material_lot_no(self):
        return self.material_lot.lot_no

    @property
    def heat_no(self):
        return self.material_lot.heat.heat_no
