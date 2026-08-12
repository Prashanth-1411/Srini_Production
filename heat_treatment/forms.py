from django import forms

from .models import FurnaceBatch


class BSFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class FurnaceBatchForm(BSFormMixin, forms.ModelForm):
    class Meta:
        model = FurnaceBatch
        fields = [
            "batch_no",
            "furnace",
            "production_lot",
            "charge_date",
            "discharge_date",
            "temperature",
            "duration_hours",
            "hardness_before",
            "hardness_after",
            "status",
            "remarks",
        ]
        widgets = {
            "charge_date": forms.DateInput(attrs={"type": "date"}),
            "discharge_date": forms.DateInput(attrs={"type": "date"}),
        }
