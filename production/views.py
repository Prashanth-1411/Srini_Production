from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from audit.services import log_action
from materials.models import MaterialTransaction

from .forms import CNCJobForm, ProductionLotForm
from .models import CNCJob, ProductionLot


def _status_badge(status, mapping):
    colors = {
        "PLANNED": "secondary",
        "IN_PROGRESS": "primary",
        "COMPLETED": "success",
        "CLOSED": "dark",
        "QC_PENDING": "info",
        "QC_APPROVED": "success",
        "QC_REJECTED": "danger",
        "DISPATCHED": "dark",
    }
    label = dict(mapping).get(status, status)
    return f'<span class="badge bg-{colors.get(status, "secondary")}">{label}</span>'


@login_required
def index(request):
    context = {
        "page_title": "Production",
        "counts": [
            {"label": "CNC Jobs", "count": CNCJob.objects.count(), "url": "production:job_list", "icon": "bi-clipboard-check"},
            {"label": "Production Lots", "count": ProductionLot.objects.count(), "url": "production:lot_list", "icon": "bi-gear-wide-connected"},
            {"label": "In Progress", "count": ProductionLot.objects.filter(status="IN_PROGRESS").count(), "url": "production:lot_list", "icon": "bi-play-circle"},
            {"label": "QC Approved", "count": ProductionLot.objects.filter(status="QC_APPROVED").count(), "url": "production:lot_list", "icon": "bi-check-circle"},
        ],
    }
    return render(request, "production/index.html", context)


@login_required
def job_list(request):
    rows = [
        {
            "cells": [
                j.job_no,
                j.customer.name,
                j.product.name,
                j.quantity,
                j.due_date or "-",
                _status_badge(j.status, CNCJob.STATUS_CHOICES),
            ],
            "actions": [
                {"label": "View", "url": f"/production/jobs/{j.pk}/"},
                {"label": "Edit", "url": f"/production/jobs/{j.pk}/edit/"},
            ],
        }
        for j in CNCJob.objects.select_related("customer", "product").all()
    ]
    return render(
        request,
        "production/list_page.html",
        {
            "page_title": "CNC Jobs",
            "columns": ["Job No", "Customer", "Product", "Qty", "Due Date", "Status"],
            "rows": rows,
            "add_url": "/production/jobs/add/",
            "back_url": "/production/",
        },
    )


@login_required
def job_add(request):
    return _save_form(request, CNCJobForm, "CNC Job", "production:job_list", CNCJob)


@login_required
def job_edit(request, pk):
    return _save_form(request, CNCJobForm, "CNC Job", "production:job_list", CNCJob, pk)


@login_required
def job_detail(request, pk):
    job = get_object_or_404(CNCJob.objects.select_related("customer", "product"), pk=pk)
    lots = job.production_lots.select_related("material_lot__heat").all()
    rows = [
        {
            "cells": [
                l.lot_no,
                l.material_lot.lot_no,
                l.material_lot.heat.heat_no,
                l.qty_ok,
                l.qty_scrap,
                _status_badge(l.status, ProductionLot.STATUS_CHOICES),
            ],
            "actions": [{"label": "View", "url": f"/production/lots/{l.pk}/"}],
        }
        for l in lots
    ]
    return render(
        request,
        "production/job_detail.html",
        {
            "page_title": f"Job {job.job_no}",
            "job": job,
            "columns": ["Lot No", "Material Lot", "Heat", "OK", "Scrap", "Status"],
            "rows": rows,
        },
    )


@login_required
def lot_list(request):
    rows = [
        {
            "cells": [
                l.lot_no,
                l.job.job_no,
                l.material_lot.lot_no,
                l.material_lot.heat.heat_no,
                l.qty_started,
                l.qty_ok,
                _status_badge(l.status, ProductionLot.STATUS_CHOICES),
            ],
            "actions": [
                {"label": "View", "url": f"/production/lots/{l.pk}/"},
                {"label": "Edit", "url": f"/production/lots/{l.pk}/edit/"},
            ],
        }
        for l in ProductionLot.objects.select_related("job", "material_lot__heat").all()
    ]
    return render(
        request,
        "production/list_page.html",
        {
            "page_title": "Production Lots",
            "columns": ["Lot No", "Job", "Material Lot", "Heat", "Started", "OK", "Status"],
            "rows": rows,
            "add_url": "/production/lots/add/",
            "back_url": "/production/",
        },
    )


@login_required
def lot_add(request):
    return _save_form(
        request,
        ProductionLotForm,
        "Production Lot",
        "production:lot_list",
        ProductionLot,
        form_subtitle="Creating a production lot records material consumption from the selected material lot.",
    )


@login_required
def lot_edit(request, pk):
    return _save_form(request, ProductionLotForm, "Production Lot", "production:lot_list", ProductionLot, pk)


@login_required
def lot_detail(request, pk):
    lot = get_object_or_404(
        ProductionLot.objects.select_related(
            "job__customer", "job__product", "material_lot__heat__supplier", "machine"
        ),
        pk=pk,
    )
    processes = lot.process_records.all()
    furnace = lot.furnace_batches.first()
    inspections = lot.qc_inspections.all()
    reworks = lot.rework_records.all()
    scraps = lot.scrap_records.all()
    dispatch_items = lot.dispatch_items.select_related("dispatch").all()
    return render(
        request,
        "production/lot_detail.html",
        {
            "page_title": f"Production Lot {lot.lot_no}",
            "lot": lot,
            "processes": processes,
            "furnace": furnace,
            "inspections": inspections,
            "reworks": reworks,
            "scraps": scraps,
            "dispatch_items": dispatch_items,
        },
    )


def _save_form(request, form_cls, title, redirect_name, model, pk=None, form_subtitle=None):
    instance = get_object_or_404(model, pk=pk) if pk else None
    if request.method == "POST":
        form = form_cls(request.POST, instance=instance)
        if form.is_valid():
            obj = form.save(commit=False)
            if hasattr(obj, "created_by") and obj.pk is None:
                obj.created_by = request.user
            obj.save()
            form.save_m2m()
            action = "UPDATE" if instance else "CREATE"
            log_action(
                request, action, "production", obj.pk,
                model=model.__name__, new=form.cleaned_data,
            )
            if (
                isinstance(obj, ProductionLot)
                and obj.material_qty
                and obj.pk is not None
                and not MaterialTransaction.objects.filter(
                    lot=obj.material_lot,
                    reference_type="PROD_LOT",
                    reference_id=obj.lot_no,
                ).exists()
            ):
                MaterialTransaction.objects.create(
                    lot=obj.material_lot,
                    txn_type=MaterialTransaction.TXN_OUT,
                    quantity=obj.material_qty,
                    reference_type="PROD_LOT",
                    reference_id=obj.lot_no,
                    txn_date=obj.start_date or obj.created_at.date(),
                    remarks=f"Consumed by production lot {obj.lot_no}",
                    created_by=request.user,
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
        "back_url": f"/production/{redirect_name.split(':')[-1].replace('_list', '')}/",
    }
    return render(request, "partials/form_page.html", context)
