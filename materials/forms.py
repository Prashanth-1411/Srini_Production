from django import forms

from .models import Bar, HeatNumber, MaterialLot, MaterialTransaction


class BSFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class HeatNumberForm(BSFormMixin, forms.ModelForm):
    class Meta:
        model = HeatNumber
        fields = ["heat_no", "supplier", "grade", "mfg_date", "mill_cert_no", "remarks"]
        widgets = {"mfg_date": forms.DateInput(attrs={"type": "date"})}


class MaterialLotForm(BSFormMixin, forms.ModelForm):
    class Meta:
        model = MaterialLot
        fields = [
            "lot_no",
            "heat",
            "product",
            "bar_dia",
            "unit",
            "quantity_received",
            "dc_no",
            "received_date",
            "remarks",
        ]
        widgets = {"received_date": forms.DateInput(attrs={"type": "date"})}


class BarForm(BSFormMixin, forms.ModelForm):
    class Meta:
        model = Bar
        fields = ["lot", "bar_no", "weight", "status"]


class MaterialTransactionForm(BSFormMixin, forms.ModelForm):
    class Meta:
        model = MaterialTransaction
        fields = ["lot", "txn_type", "quantity", "txn_date", "remarks"]
        widgets = {"txn_date": forms.DateInput(attrs={"type": "date"})}

    def clean(self):
        cleaned = super().clean()
        lot = cleaned.get("lot")
        txn_type = cleaned.get("txn_type")
        quantity = cleaned.get("quantity")
        if lot and txn_type == MaterialTransaction.TXN_OUT and quantity is not None:
            if quantity > lot.quantity_remaining:
                self.add_error(
                    "quantity",
                    f"Cannot consume {quantity} {lot.unit} — only {lot.quantity_remaining} remaining.",
                )
        return cleaned
