import os

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

ALLOWED_EXTENSIONS = {".pdf", ".xlsx", ".xls"}
MAX_FILE_SIZE = 25 * 1024 * 1024

_PDF_MAGIC = b"%PDF-"
_XLSX_MAGIC = b"PK\x03\x04"
_XLS_MAGIC = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"

_MAGIC_BY_EXT = {".pdf": _PDF_MAGIC, ".xlsx": _XLSX_MAGIC, ".xls": _XLS_MAGIC}


def validate_document_file(value):
    ext = os.path.splitext(getattr(value, "name", ""))[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            _("Unsupported file type '{}'. Only PDF (.pdf) and Excel (.xlsx, .xls) files are allowed.").format(
                ext or "unknown"
            )
        )
    if value.size and value.size > MAX_FILE_SIZE:
        raise ValidationError(
            _("File is too large (maximum {} MB).").format(MAX_FILE_SIZE // (1024 * 1024))
        )
    value.seek(0)
    head = value.read(8)
    value.seek(0)
    if not head.startswith(_MAGIC_BY_EXT[ext]):
        raise ValidationError(
            _("The file content does not match its extension. Please upload a valid {} file.").format(
                ext.upper()
            )
        )
