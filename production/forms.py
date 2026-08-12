from django import forms

from .models import CNCJob, ProductionLot


class BSFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class CNCJobForm(BSFormMixin, forms.ModelForm):
    class Meta:
        model = CNCJob
        fields = [
            "job_no",
            "customer",
            "product",
            "order_no",
            "quantity",
            "due_date",
            "status",
            "remarks",
        ]
        widgets = {"due_date": forms.DateInput(attrs={"type": "date"})}


class ProductionLotForm(BSFormMixin, forms.ModelForm):
    class Meta:
        model = ProductionLot
        fields = [
            "lot_no",
            "job",
            "material_lot",
            "machine",
            "operator",
            "material_qty",
            "qty_started",
            "qty_ok",
            "qty_rework",
            "qty_scrap",
            "status",
            "start_date",
            "end_date",
            "remarks",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean_material_qty(self):
        material_qty = self.cleaned_data.get("material_qty") or 0
        material_lot = self.cleaned_data.get("material_lot")
        if material_lot and material_qty > material_lot.quantity_remaining:
            self.add_error(
                "material_qty",
                f"Cannot consume {material_qty} {material_lot.unit} — only "
                f"{material_lot.quantity_remaining} remaining in lot {material_lot.lot_no}.",
            )
        return material_qty
