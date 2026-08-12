from django import forms

from .models import QCInspection, Rework, Scrap


class BSFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class QCInspectionForm(BSFormMixin, forms.ModelForm):
    class Meta:
        model = QCInspection
        fields = [
            "inspection_no",
            "production_lot",
            "inspector",
            "inspection_date",
            "qty_checked",
            "qty_passed",
            "qty_rework",
            "qty_rejected",
            "result",
            "remarks",
        ]
        widgets = {"inspection_date": forms.DateInput(attrs={"type": "date"})}


class ReworkForm(BSFormMixin, forms.ModelForm):
    class Meta:
        model = Rework
        fields = ["production_lot", "inspection", "quantity", "reason", "rework_date", "completed"]
        widgets = {"rework_date": forms.DateInput(attrs={"type": "date"})}


class ScrapForm(BSFormMixin, forms.ModelForm):
    class Meta:
        model = Scrap
        fields = ["production_lot", "inspection", "quantity", "reason", "scrap_date"]
        widgets = {"scrap_date": forms.DateInput(attrs={"type": "date"})}
