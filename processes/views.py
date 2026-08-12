from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from audit.services import log_action

from .forms import ProcessRecordForm
from .models import ProcessRecord


@login_required
def index(request):
    context = {
        "page_title": "Grinding / Hard-facing",
        "counts": [
            {"label": "Grinding Records", "count": ProcessRecord.objects.filter(process_type="GRINDING").count(), "url": "processes:list", "icon": "bi-brush"},
            {"label": "Hard-facing Records", "count": ProcessRecord.objects.filter(process_type="HARD_FACING").count(), "url": "processes:list", "icon": "bi-fire"},
            {"label": "Total Records", "count": ProcessRecord.objects.count(), "url": "processes:list", "icon": "bi-list-check"},
        ],
    }
    return render(request, "processes/index.html", context)


@login_required
def list_view(request):
    rows = [
        {
            "cells": [
                r.record_no,
                '<span class="badge bg-info">' + r.get_process_type_display() + "</span>",
                r.production_lot.lot_no,
                r.production_lot.job.product.name,
                r.machine.name if r.machine else "-",
                r.quantity,
                r.process_date or "-",
            ],
            "actions": [{"label": "Edit", "url": f"/processes/{r.pk}/edit/"}],
        }
        for r in ProcessRecord.objects.select_related("production_lot__job__product", "machine").all()
    ]
    return render(
        request,
        "processes/list_page.html",
        {
            "page_title": "Process Records",
            "columns": ["Record No", "Type", "Prod Lot", "Product", "Machine", "Qty", "Date"],
            "rows": rows,
            "add_url": "/processes/add/",
            "back_url": "/processes/",
        },
    )


@login_required
def add_view(request):
    return _save_form(request, ProcessRecordForm, "Process Record", "processes:list", ProcessRecord)


@login_required
def edit_view(request, pk):
    return _save_form(request, ProcessRecordForm, "Process Record", "processes:list", ProcessRecord, pk)


def _save_form(request, form_cls, title, redirect_name, model, pk=None, form_subtitle=None):
    instance = get_object_or_404(model, pk=pk) if pk else None
    if request.method == "POST":
        form = form_cls(request.POST, instance=instance)
        if form.is_valid():
            obj = form.save(commit=False)
            if hasattr(obj, "created_by") and obj.pk is None:
                obj.created_by = request.user
            obj.save()
            action = "UPDATE" if instance else "CREATE"
            log_action(
                request, action, "processes", obj.pk,
                model=model.__name__, new=form.cleaned_data,
            )
            messages.success(request, f"{title} saved successfully.")
            return redirect(redirect_name)
    else:
        form = form_cls(instance=instance)
    context = {
        "page_title": f"{'Edit' if instance else 'Add'} {title}",
        "form": form,
        "form_title": f"{'Edit' if instance else 'Add'} {title}",
        "form_subtitle": form_subtitle,
        "back_url": "/processes/",
    }
    return render(request, "partials/form_page.html", context)
