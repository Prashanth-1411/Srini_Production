from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from audit.services import log_action
from production.models import ProductionLot

from .forms import QCInspectionForm, ReworkForm, ScrapForm
from .models import QCInspection, Rework, Scrap


def _result_badge(result):
    colors = {"PASS": "success", "REJECT": "danger", "HOLD": "warning"}
    return f'<span class="badge bg-{colors.get(result, "secondary")}">{result}</span>'


@login_required
def index(request):
    context = {
        "page_title": "Quality Control",
        "counts": [
            {"label": "Inspections", "count": QCInspection.objects.count(), "url": "quality:inspection_list", "icon": "bi-clipboard-check"},
            {"label": "Rework Records", "count": Rework.objects.count(), "url": "quality:rework_list", "icon": "bi-arrow-repeat"},
            {"label": "Scrap Records", "count": Scrap.objects.count(), "url": "quality:scrap_list", "icon": "bi-trash"},
            {"label": "Pending QC", "count": ProductionLot.objects.filter(status="QC_PENDING").count(), "url": "quality:inspection_list", "icon": "bi-hourglass-split"},
        ],
    }
    return render(request, "quality/index.html", context)


@login_required
def inspection_list(request):
    rows = [
        {
            "cells": [
                i.inspection_no,
                i.production_lot.lot_no,
                i.inspection_date or "-",
                i.qty_checked,
                i.qty_passed,
                i.qty_rejected,
                _result_badge(i.result),
            ],
            "actions": [{"label": "Edit", "url": f"/quality/inspections/{i.pk}/edit/"}],
        }
        for i in QCInspection.objects.select_related("production_lot").all()
    ]
    return render(
        request,
        "quality/list_page.html",
        {
            "page_title": "QC Inspections",
            "columns": ["Inspection No", "Prod Lot", "Date", "Checked", "Passed", "Rejected", "Result"],
            "rows": rows,
            "add_url": "/quality/inspections/add/",
            "back_url": "/quality/",
        },
    )


@login_required
def inspection_add(request):
    return _save_form(
        request,
        QCInspectionForm,
        "QC Inspection",
        "quality:inspection_list",
        QCInspection,
        form_subtitle="The production lot status is updated automatically based on the result.",
    )


@login_required
def inspection_edit(request, pk):
    return _save_form(request, QCInspectionForm, "QC Inspection", "quality:inspection_list", QCInspection, pk)


@login_required
def rework_list(request):
    rows = [
        {
            "cells": [
                r.production_lot.lot_no,
                r.quantity,
                r.reason or "-",
                r.rework_date or "-",
                "Yes" if r.completed else "No",
            ],
            "actions": [{"label": "Edit", "url": f"/quality/rework/{r.pk}/edit/"}],
        }
        for r in Rework.objects.select_related("production_lot").all()
    ]
    return render(
        request,
        "quality/list_page.html",
        {
            "page_title": "Rework",
            "columns": ["Prod Lot", "Qty", "Reason", "Date", "Completed"],
            "rows": rows,
            "add_url": "/quality/rework/add/",
            "back_url": "/quality/",
        },
    )


@login_required
def rework_add(request):
    return _save_form(request, ReworkForm, "Rework Record", "quality:rework_list", Rework)


@login_required
def rework_edit(request, pk):
    return _save_form(request, ReworkForm, "Rework Record", "quality:rework_list", Rework, pk)


@login_required
def scrap_list(request):
    rows = [
        {
            "cells": [
                s.production_lot.lot_no,
                s.quantity,
                s.reason or "-",
                s.scrap_date or "-",
            ],
            "actions": [{"label": "Edit", "url": f"/quality/scrap/{s.pk}/edit/"}],
        }
        for s in Scrap.objects.select_related("production_lot").all()
    ]
    return render(
        request,
        "quality/list_page.html",
        {
            "page_title": "Scrap",
            "columns": ["Prod Lot", "Qty", "Reason", "Date"],
            "rows": rows,
            "add_url": "/quality/scrap/add/",
            "back_url": "/quality/",
        },
    )


@login_required
def scrap_add(request):
    return _save_form(request, ScrapForm, "Scrap Record", "quality:scrap_list", Scrap)


@login_required
def scrap_edit(request, pk):
    return _save_form(request, ScrapForm, "Scrap Record", "quality:scrap_list", Scrap, pk)


def _save_form(request, form_cls, title, redirect_name, model, pk=None, form_subtitle=None):
    instance = get_object_or_404(model, pk=pk) if pk else None
    if request.method == "POST":
        form = form_cls(request.POST, instance=instance)
        if form.is_valid():
            obj = form.save(commit=False)
            if hasattr(obj, "created_by") and obj.pk is None:
                obj.created_by = request.user
            obj.save()
            if isinstance(obj, QCInspection):
                lot = obj.production_lot
                if obj.result == QCInspection.RESULT_PASS:
                    lot.status = ProductionLot.STATUS_QC_APPROVED
                elif obj.result == QCInspection.RESULT_REJECT:
                    lot.status = ProductionLot.STATUS_QC_REJECTED
                else:
                    lot.status = ProductionLot.STATUS_QC_PENDING
                lot.save(update_fields=["status"])
            action = "UPDATE" if instance else "CREATE"
            log_action(
                request, action, "quality", obj.pk,
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
        "back_url": "/quality/",
    }
    return render(request, "partials/form_page.html", context)
