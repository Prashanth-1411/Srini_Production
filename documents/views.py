import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render

from audit.services import log_action

from .forms import DocumentForm
from .models import Document
from .preview import excel_to_html


@login_required
def index(request):
    context = {
        "page_title": "Documents",
        "counts": [
            {"label": "All Documents", "count": Document.objects.count(), "url": "documents:list", "icon": "bi-folder2-open"},
            {"label": "Inward / Goods Received", "count": Document.objects.filter(category=Document.CATEGORY_INWARD).count(), "url": "documents:list", "icon": "bi-box-arrow-in-down"},
            {"label": "Outward / Goods Dispatched", "count": Document.objects.filter(category=Document.CATEGORY_OUTWARD).count(), "url": "documents:list", "icon": "bi-box-arrow-up-right"},
            {"label": "PDF Documents", "count": Document.objects.filter(file_ext=".pdf").count(), "url": "documents:list", "icon": "bi-file-earmark-pdf"},
            {"label": "Excel Documents", "count": Document.objects.filter(file_ext__in=[".xlsx", ".xls"]).count(), "url": "documents:list", "icon": "bi-file-earmark-excel"},
        ],
    }
    return render(request, "documents/index.html", context)


@login_required
def document_list(request):
    q = request.GET.get("q", "").strip()
    cat = request.GET.get("cat", "").strip()
    qs = Document.objects.select_related("uploaded_by").all()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(file__icontains=q))
    if cat:
        qs = qs.filter(category=cat)
    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get("page"))
    rows = [
        {
            "cells": [
                f'<a href="/documents/{d.pk}/">{d.title}</a>',
                d.get_category_display(),
                d.filename,
                f'<span class="badge bg-{"danger" if d.is_pdf else "success"}">{d.file_ext.upper()}</span>',
                d.human_size(),
                d.created_at.date(),
                d.uploaded_by.username if d.uploaded_by else "-",
            ],
            "actions": [
                {"label": "View", "url": f"/documents/{d.pk}/"},
                {"label": "Del", "url": f"/documents/{d.pk}/delete/"},
            ],
        }
        for d in page.object_list
    ]
    return render(
        request,
        "documents/list_page.html",
        {
            "page_title": "Documents",
            "columns": ["Title", "Category", "File", "Type", "Size", "Uploaded", "By"],
            "rows": rows,
            "add_url": "/documents/upload/",
            "back_url": "/documents/",
            "pagination": True,
            "page_obj": page,
            "q": q,
            "cat": cat,
            "cat_counts": {
                "ALL": Document.objects.count(),
                Document.CATEGORY_INWARD: Document.objects.filter(category=Document.CATEGORY_INWARD).count(),
                Document.CATEGORY_OUTWARD: Document.objects.filter(category=Document.CATEGORY_OUTWARD).count(),
                "pdf": Document.objects.filter(file_ext=".pdf").count(),
                "excel": Document.objects.filter(file_ext__in=[".xlsx", ".xls"]).count(),
            },
        },
    )


@login_required
def document_upload(request):
    return _save(request, None)


@login_required
def document_edit(request, pk):
    return _save(request, pk)


def _save(request, pk):
    instance = get_object_or_404(Document, pk=pk) if pk else None
    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            replacing = instance and "file" in form.changed_data
            old_file = instance.file if replacing else None
            obj = form.save(commit=False)
            if obj.uploaded_by_id is None:
                obj.uploaded_by = request.user
            obj.save()
            if old_file:
                try:
                    old_file.delete(save=False)
                except (OSError, ValueError):
                    pass
            log_action(
                request,
                "UPDATE" if instance else "CREATE",
                "documents",
                obj.pk,
                model="Document",
                new=form.cleaned_data,
            )
            messages.success(request, "Document saved successfully.")
            return redirect("documents:detail", pk=obj.pk)
    else:
        form = DocumentForm(instance=instance)
    return render(
        request,
        "documents/form_page.html",
        {
            "page_title": f"{'Edit' if instance else 'Upload'} Document",
            "form": form,
            "form_title": f"{'Edit' if instance else 'Upload'} Document",
            "form_subtitle": "Files are validated — only PDF (.pdf) and Excel (.xlsx, .xls) are accepted.",
            "back_url": "/documents/",
        },
    )


@login_required
def document_detail(request, pk):
    doc = get_object_or_404(Document.objects.select_related("uploaded_by"), pk=pk)
    preview_html = None
    if doc.is_excel:
        try:
            preview_html = excel_to_html(doc.file.path)
        except Exception:
            preview_html = (
                '<div class="alert alert-danger mb-0">Could not preview this file. '
                "It may be corrupt or protected — use Download to open it.</div>"
            )
    return render(
        request,
        "documents/detail.html",
        {"page_title": doc.title, "doc": doc, "preview_html": preview_html},
    )


@login_required
def document_view(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    content_type = "application/pdf" if doc.is_pdf else (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        if doc.file_ext == ".xlsx"
        else "application/vnd.ms-excel"
    )
    response = FileResponse(doc.file.open("rb"), content_type=content_type)
    response["Content-Disposition"] = f'inline; filename="{doc.filename}"'
    response["X-Frame-Options"] = "SAMEORIGIN"
    response["Content-Security-Policy"] = "frame-ancestors 'self'"
    return response


@login_required
def document_download(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    return FileResponse(doc.file.open("rb"), as_attachment=True, filename=doc.filename)


@login_required
def document_delete(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    if request.method == "POST":
        log_action(request, "DELETE", "documents", doc.pk, model="Document", new={"title": doc.title})
        doc.delete()
        messages.success(request, "Document deleted.")
        return redirect("documents:list")
    return render(
        request,
        "documents/confirm_delete.html",
        {"page_title": "Delete Document", "object": doc, "back_url": f"/documents/{doc.pk}/"},
    )
