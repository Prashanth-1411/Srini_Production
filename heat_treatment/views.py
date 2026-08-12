from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from audit.services import log_action

from .forms import FurnaceBatchForm
from .models import FurnaceBatch


def _status_badge(status):
    colors = {
        "SCHEDULED": "secondary",
        "IN_PROGRESS": "primary",
        "HOLD": "warning",
        "RELEASED": "success",
    }
    label = dict(FurnaceBatch.STATUS_CHOICES).get(status, status)
    return f'<span class="badge bg-{colors.get(status, "secondary")}">{label}</span>'


@login_required
def index(request):
    context = {
        "page_title": "Heat Treatment",
        "counts": [
            {"label": "Total Batches", "count": FurnaceBatch.objects.count(), "url": "heat_treatment:list", "icon": "bi-fire"},
            {"label": "In Progress", "count": FurnaceBatch.objects.filter(status="IN_PROGRESS").count(), "url": "heat_treatment:list", "icon": "bi-hourglass-split"},
            {"label": "On Hold", "count": FurnaceBatch.objects.filter(status="HOLD").count(), "url": "heat_treatment:list", "icon": "bi-pause-circle"},
            {"label": "Released", "count": FurnaceBatch.objects.filter(status="RELEASED").count(), "url": "heat_treatment:list", "icon": "bi-check-circle"},
        ],
    }
    return render(request, "heat_treatment/index.html", context)


@login_required
def list_view(request):
    rows = [
        {
            "cells": [
                b.batch_no,
                b.furnace.name,
                b.production_lot.lot_no,
                b.production_lot.job.product.name,
                b.charge_date or "-",
                b.temperature or "-",
                b.hardness_after or "-",
                _status_badge(b.status),
            ],
            "actions": [{"label": "Edit", "url": f"/heat-treatment/batches/{b.pk}/edit/"}],
        }
        for b in FurnaceBatch.objects.select_related("furnace", "production_lot__job__product").all()
    ]
    return render(
        request,
        "heat_treatment/list_page.html",
        {
            "page_title": "Furnace Batches",
            "columns": ["Batch No", "Furnace", "Prod Lot", "Product", "Charge Date", "Temp", "Hardness After", "Status"],
            "rows": rows,
            "add_url": "/heat-treatment/batches/add/",
            "back_url": "/heat-treatment/",
        },
    )


@login_required
def add_view(request):
    return _save_form(request, FurnaceBatchForm, "Furnace Batch", "heat_treatment:list", FurnaceBatch)


@login_required
def edit_view(request, pk):
    return _save_form(request, FurnaceBatchForm, "Furnace Batch", "heat_treatment:list", FurnaceBatch, pk)


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
                request, action, "heat_treatment", obj.pk,
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
        "back_url": "/heat-treatment/",
    }
    return render(request, "partials/form_page.html", context)
