from django import forms

from .models import Customer, Furnace, Machine, Product, Shift, Supplier


class BSFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class SupplierForm(BSFormMixin, forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ["code", "name", "gstin", "address", "phone", "email", "active"]


class CustomerForm(BSFormMixin, forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["code", "name", "gstin", "address", "phone", "email", "active"]


class ProductForm(BSFormMixin, forms.ModelForm):
    class Meta:
        model = Product
        fields = ["code", "name", "drawing_no", "material_spec", "description", "active"]


class MachineForm(BSFormMixin, forms.ModelForm):
    class Meta:
        model = Machine
        fields = ["code", "name", "machine_type", "location", "active"]


class FurnaceForm(BSFormMixin, forms.ModelForm):
    class Meta:
        model = Furnace
        fields = ["code", "name", "furnace_type", "capacity", "active"]


class ShiftForm(BSFormMixin, forms.ModelForm):
    class Meta:
        model = Shift
        fields = ["name", "start_time", "end_time", "active"]
        widgets = {
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
        }
