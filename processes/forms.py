from django import forms

from .models import ProcessRecord


class BSFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class ProcessRecordForm(BSFormMixin, forms.ModelForm):
    class Meta:
        model = ProcessRecord
        fields = [
            "record_no",
            "process_type",
            "production_lot",
            "machine",
            "operator",
            "quantity",
            "process_date",
            "remarks",
        ]
        widgets = {"process_date": forms.DateInput(attrs={"type": "date"})}
