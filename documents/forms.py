from django import forms

from .models import Document
from .validators import ALLOWED_EXTENSIONS


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["title", "category", "description", "file"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
        self.fields["description"].widget.attrs["rows"] = 3
        self.fields["file"].widget.attrs["accept"] = ",".join(sorted(ALLOWED_EXTENSIONS))
        if self.instance and self.instance.pk:
            self.fields["file"].required = False
            self.fields["file"].help_text = (
                f"Only PDF (.pdf) and Excel (.xlsx, .xls) files are allowed. "
                f"Current file: {self.instance.filename} — leave empty to keep it."
            )
