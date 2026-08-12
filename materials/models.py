from django.conf import settings
from django.db import models
from django.db.models import Sum

from masters.models import Product, Supplier, TimeStampedModel


class HeatNumber(TimeStampedModel):
    heat_no = models.CharField("Heat number", max_length=50, unique=True)
    supplier = models.ForeignKey(
        Supplier, on_delete=models.PROTECT, related_name="heat_numbers"
    )
    grade = models.CharField("Material grade", max_length=100)
    mfg_date = models.DateField("Manufacturing date", null=True, blank=True)
    mill_cert_no = models.CharField("Mill certificate / MTC no", max_length=50, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.heat_no} ({self.grade})"


class MaterialLot(TimeStampedModel):
    LOT_ACTIVE = "ACTIVE"
    LOT_CLOSED = "CLOSED"
    LOT_HOLD = "HOLD"
    STATUS_CHOICES = [
        (LOT_ACTIVE, "Active"),
        (LOT_HOLD, "Hold"),
        (LOT_CLOSED, "Closed"),
    ]

    lot_no = models.CharField("Lot number", max_length=50, unique=True)
    heat = models.ForeignKey(
        HeatNumber, on_delete=models.PROTECT, related_name="lots"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="material_lots",
        verbose_name="Raw material",
    )
    bar_dia = models.DecimalField(
        "Bar diameter (mm)", max_digits=8, decimal_places=2, null=True, blank=True
    )
    unit = models.CharField(max_length=10, default="kg")
    quantity_received = models.DecimalField(max_digits=12, decimal_places=3)
    quantity_remaining = models.DecimalField(max_digits=12, decimal_places=3)
    dc_no = models.CharField("DC / Challan no", max_length=50, blank=True)
    received_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=LOT_ACTIVE)
    remarks = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="material_lots_created",
    )

    class Meta:
        ordering = ["-received_date", "lot_no"]
        indexes = [models.Index(fields=["status"]), models.Index(fields=["heat"])]

    def __str__(self):
        return f"{self.lot_no} ({self.heat})"

    def save(self, *args, **kwargs):
        if not self.quantity_remaining and self.quantity_received:
            self.quantity_remaining = self.quantity_received
        super().save(*args, **kwargs)

    def is_closed(self):
        return self.quantity_remaining <= 0


class Bar(TimeStampedModel):
    BAR_STOCK = "STOCK"
    BAR_USED = "USED"
    BAR_SCRAP = "SCRAP"
    STATUS_CHOICES = [
        (BAR_STOCK, "Stock"),
        (BAR_USED, "Used"),
        (BAR_SCRAP, "Scrap"),
    ]

    lot = models.ForeignKey(MaterialLot, on_delete=models.CASCADE, related_name="bars")
    bar_no = models.CharField(max_length=50)
    weight = models.DecimalField(max_digits=10, decimal_places=3)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=BAR_STOCK)

    class Meta:
        ordering = ["bar_no"]
        constraints = [
            models.UniqueConstraint(fields=["lot", "bar_no"], name="uniq_lot_bar_no")
        ]

    def __str__(self):
        return f"{self.lot.lot_no} / {self.bar_no}"


class MaterialTransaction(TimeStampedModel):
    TXN_IN = "IN"
    TXN_OUT = "OUT"
    TXN_TYPES = [
        (TXN_IN, "Inward"),
        (TXN_OUT, "Outward / Consumed"),
    ]

    lot = models.ForeignKey(
        MaterialLot, on_delete=models.CASCADE, related_name="transactions"
    )
    txn_type = models.CharField(max_length=3, choices=TXN_TYPES)
    quantity = models.DecimalField(max_digits=12, decimal_places=3)
    reference_type = models.CharField(max_length=50, blank=True)
    reference_id = models.CharField(max_length=100, blank=True)
    txn_date = models.DateField()
    remarks = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="material_transactions_created",
    )

    class Meta:
        ordering = ["-txn_date", "-created_at"]
        indexes = [models.Index(fields=["txn_type"]), models.Index(fields=["lot"])]

    def __str__(self):
        return f"{self.lot.lot_no} {self.txn_type} {self.quantity}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        _recompute_lot_balance(self.lot)

    def delete(self, *args, **kwargs):
        lot = self.lot
        super().delete(*args, **kwargs)
        _recompute_lot_balance(lot)


def _recompute_lot_balance(lot):
    inward = (
        lot.transactions.filter(txn_type=MaterialTransaction.TXN_IN).aggregate(s=Sum("quantity"))["s"]
        or 0
    )
    outward = (
        lot.transactions.filter(txn_type=MaterialTransaction.TXN_OUT).aggregate(s=Sum("quantity"))["s"]
        or 0
    )
    lot.quantity_remaining = lot.quantity_received + inward - outward
    lot.status = (
        MaterialLot.LOT_CLOSED
        if lot.quantity_remaining <= 0
        else MaterialLot.LOT_ACTIVE
    )
    lot.save(update_fields=["quantity_remaining", "status"])
