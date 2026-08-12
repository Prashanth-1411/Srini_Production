from django import forms
from django.forms import inlineformset_factory

from .models import Dispatch, DispatchItem


class BSFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class DispatchForm(BSFormMixin, forms.ModelForm):
    class Meta:
        model = Dispatch
        fields = ["dispatch_no", "customer", "invoice_no", "dispatch_date", "vehicle_no", "status", "remarks"]
        widgets = {"dispatch_date": forms.DateInput(attrs={"type": "date"})}


class DispatchItemForm(BSFormMixin, forms.ModelForm):
    class Meta:
        model = DispatchItem
        fields = ["production_lot", "quantity"]

    def clean_quantity(self):
        quantity = self.cleaned_data.get("quantity") or 0
        production_lot = self.cleaned_data.get("production_lot")
        if production_lot and quantity > production_lot.qty_ok:
            self.add_error(
                "quantity",
                f"Cannot dispatch {quantity} — only {production_lot.qty_ok} OK pieces available.",
            )
        return quantity


DispatchItemFormSet = inlineformset_factory(
    Dispatch,
    DispatchItem,
    form=DispatchItemForm,
    extra=1,
    can_delete=True,
)
