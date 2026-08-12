import os
import shutil
import tempfile

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from .models import Document
from .preview import excel_to_html
from .validators import validate_document_file

TEMP_MEDIA = tempfile.mkdtemp(prefix="documents_test_media_")


def tearDownModule():
    shutil.rmtree(TEMP_MEDIA, ignore_errors=True)


class ValidatorTests(TestCase):
    def test_rejects_non_pdf_excel_extension(self):
        file = SimpleUploadedFile("notes.txt", b"hello")
        with self.assertRaises(ValidationError):
            validate_document_file(file)

    def test_rejects_mismatched_content(self):
        file = SimpleUploadedFile("fake.pdf", b"definitely not a pdf")
        with self.assertRaises(ValidationError):
            validate_document_file(file)

    def test_accepts_pdf(self):
        file = SimpleUploadedFile("mtc.pdf", b"%PDF-1.4 fake content")
        validate_document_file(file)

    def test_accepts_xlsx(self):
        file = SimpleUploadedFile("sheet.xlsx", b"PK\x03\x04 fake zip")
        validate_document_file(file)

    def test_accepts_xls(self):
        file = SimpleUploadedFile("old.xls", b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1 fake ole")
        validate_document_file(file)


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class DocumentModelTests(TestCase):
    def test_save_records_size_and_ext(self):
        doc = Document.objects.create(
            title="MTC EN8",
            category=Document.CATEGORY_MATERIAL_CERT,
            file=SimpleUploadedFile("mtc.pdf", b"%PDF-1.4 test"),
        )
        self.assertEqual(doc.file_ext, ".pdf")
        self.assertEqual(doc.file_size, len(b"%PDF-1.4 test"))
        self.assertTrue(doc.is_pdf)
        self.assertFalse(doc.is_excel)
        self.assertTrue(doc.filename.endswith(".pdf"))

    def test_excel_extension_flagged(self):
        doc = Document.objects.create(
            title="Stock",
            file=SimpleUploadedFile("stock.xlsx", b"PK\x03\x04 fake"),
        )
        self.assertTrue(doc.is_excel)


class PreviewTests(TestCase):
    def test_xlsx_preview_renders_sheet(self):
        import io

        from openpyxl import Workbook

        wb = Workbook()
        ws = wb.active
        ws.title = "Sheet1"
        ws.append(["Part", "Qty"])
        ws.append(["Gear Shaft", 12])

        buffer = io.BytesIO()
        wb.save(buffer)
        path = os.path.join(tempfile.gettempdir(), "documents_preview_test.xlsx")
        with open(path, "wb") as fh:
            fh.write(buffer.getvalue())
        try:
            out = excel_to_html(path)
            self.assertIn("Sheet1", out)
            self.assertIn("Part", out)
            self.assertIn("Gear Shaft", out)
        finally:
            os.remove(path)
