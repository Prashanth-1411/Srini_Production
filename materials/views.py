from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from audit.services import log_action

from .forms import BarForm, HeatNumberForm, MaterialLotForm, MaterialTransactionForm
from .models import Bar, HeatNumber, MaterialLot, MaterialTransaction

from datetime import date


def _status_badge(status):
    colors = {
        MaterialLot.LOT_ACTIVE: "success",
        MaterialLot.LOT_HOLD: "warning",
        MaterialLot.LOT_CLOSED: "secondary",
    }
    label = dict(MaterialLot.STATUS_CHOICES).get(status, status)
    return f'<span class="badge bg-{colors.get(status, "secondary")}">{label}</span>'


def _actions(edit_url, del_url=None):
    acts = [{"label": "Edit", "url": edit_url}]
    if del_url:
        acts.append({"label": "Del", "url": del_url})
    return acts


@login_required
def index(request):
    today = date.today()
    month_lots = MaterialLot.objects.filter(received_date__year=today.year, received_date__month=today.month)
    context = {
        "page_title": "Materials",
        "inward_qty": month_lots.aggregate(s=Sum("quantity_received"))["s"] or 0,
        "outward_qty": (
            MaterialTransaction.objects.filter(
                txn_type=MaterialTransaction.TXN_OUT,
                txn_date__year=today.year,
                txn_date__month=today.month,
            ).aggregate(s=Sum("quantity"))["s"]
            or 0
        ),
        "stock_qty": MaterialLot.objects.aggregate(s=Sum("quantity_remaining"))["s"] or 0,
        "counts": [
            {"label": "Heat Numbers", "count": HeatNumber.objects.count(), "url": "materials:heat_list", "icon": "bi-fire"},
            {"label": "Material Lots", "count": MaterialLot.objects.count(), "url": "materials:lot_list", "icon": "bi-box-seam"},
            {"label": "Bars", "count": Bar.objects.count(), "url": "materials:bar_list", "icon": "bi-rulers"},
            {"label": "Transactions", "count": MaterialTransaction.objects.count(), "url": "materials:txn_list", "icon": "bi-arrow-left-right"},
            {"label": "Stock Balance", "count": MaterialLot.objects.filter(quantity_remaining__gt=0).count(), "url": "materials:stock", "icon": "bi-clipboard-data"},
        ],
    }
    return render(request, "materials/index.html", context)


@login_required
def heat_list(request):
    rows = [
        {
            "cells": [h.heat_no, h.supplier.name, h.grade, h.mfg_date or "-", h.mill_cert_no or "-"],
            "actions": [
                {"label": "View", "url": f"/materials/heats/{h.pk}/"},
                {"label": "Edit", "url": f"/materials/heats/{h.pk}/edit/"},
            ],
        }
        for h in HeatNumber.objects.select_related("supplier").all()
    ]
    return render(
        request,
        "materials/list_page.html",
        {
            "page_title": "Heat Numbers",
            "columns": ["Heat No", "Supplier", "Grade", "Mfg Date", "MTC No"],
            "rows": rows,
            "add_url": "/materials/heats/add/",
            "back_url": "/materials/",
        },
    )


@login_required
def heat_add(request):
    return _save_form(request, HeatNumberForm, "Heat Number", "materials:heat_list", HeatNumber)


@login_required
def heat_edit(request, pk):
    return _save_form(request, HeatNumberForm, "Heat Number", "materials:heat_list", HeatNumber, pk)


@login_required
def heat_detail(request, pk):
    heat = get_object_or_404(HeatNumber, pk=pk)
    lots = heat.lots.select_related("product").all()
    rows = [
        {
            "cells": [
                l.lot_no,
                l.product.name,
                l.bar_dia or "-",
                f"{l.quantity_received} {l.unit}",
                f"{l.quantity_remaining} {l.unit}",
                _status_badge(l.status),
            ],
            "actions": [{"label": "View", "url": f"/materials/lots/{l.pk}/"}],
        }
        for l in lots
    ]
    return render(
        request,
        "materials/heat_detail.html",
        {
            "page_title": f"Heat {heat.heat_no}",
            "heat": heat,
            "lots": lots,
            "columns": ["Lot No", "Material", "Dia (mm)", "Received", "Remaining", "Status"],
            "rows": rows,
        },
    )


@login_required
def lot_list(request):
    rows = [
        {
            "cells": [
                l.lot_no,
                f'<a href="/materials/heats/{l.heat_id}/">{l.heat.heat_no}</a>',
                l.heat.grade,
                l.product.name,
                f"{l.quantity_received} {l.unit}",
                f"{l.quantity_remaining} {l.unit}",
                _status_badge(l.status),
                l.received_date,
            ],
            "actions": [
                {"label": "View", "url": f"/materials/lots/{l.pk}/"},
                {"label": "Edit", "url": f"/materials/lots/{l.pk}/edit/"},
            ],
        }
        for l in MaterialLot.objects.select_related("heat", "product").all()
    ]
    return render(
        request,
        "materials/list_page.html",
        {
            "page_title": "Material Lots",
            "columns": ["Lot No", "Heat", "Grade", "Material", "Received", "Remaining", "Status", "Date"],
            "rows": rows,
            "add_url": "/materials/lots/add/",
            "back_url": "/materials/",
        },
    )


@login_required
def lot_add(request):
    return _save_form(request, MaterialLotForm, "Material Lot", "materials:lot_list", MaterialLot, form_subtitle="Lot balance starts at received quantity.")


@login_required
def lot_edit(request, pk):
    return _save_form(request, MaterialLotForm, "Material Lot", "materials:lot_list", MaterialLot, pk)


@login_required
def lot_detail(request, pk):
    lot = get_object_or_404(MaterialLot.objects.select_related("heat", "product"), pk=pk)
    bars = lot.bars.all()
    txns = lot.transactions.select_related("created_by").all()
    return render(
        request,
        "materials/lot_detail.html",
        {
            "page_title": f"Lot {lot.lot_no}",
            "lot": lot,
            "bars": bars,
            "txns": txns,
        },
    )


@login_required
def bar_list(request):
    rows = [
        {
            "cells": [
                b.lot.lot_no,
                b.bar_no,
                b.weight,
                '<span class="badge bg-secondary">' + dict(Bar.STATUS_CHOICES).get(b.status, b.status) + "</span>",
            ],
            "actions": [{"label": "Edit", "url": f"/materials/bars/{b.pk}/edit/"}],
        }
        for b in Bar.objects.select_related("lot").all()
    ]
    return render(
        request,
        "materials/list_page.html",
        {
            "page_title": "Bars",
            "columns": ["Lot", "Bar No", "Weight", "Status"],
            "rows": rows,
            "add_url": "/materials/bars/add/",
            "back_url": "/materials/",
        },
    )


@login_required
def bar_add(request):
    return _save_form(request, BarForm, "Bar", "materials:bar_list", Bar)


@login_required
def bar_edit(request, pk):
    return _save_form(request, BarForm, "Bar", "materials:bar_list", Bar, pk)


@login_required
def txn_list(request):
    rows = [
        {
            "cells": [
                t.lot.lot_no,
                f'<span class="badge bg-{"success" if t.txn_type == "IN" else "warning"}">{t.get_txn_type_display()}</span>',
                f"{t.quantity} {t.lot.unit}",
                t.txn_date,
                t.reference_type or "-",
                t.remarks or "-",
                t.created_by.username if t.created_by else "-",
            ],
            "actions": [],
        }
        for t in MaterialTransaction.objects.select_related("lot", "created_by").all()
    ]
    return render(
        request,
        "materials/list_page.html",
        {
            "page_title": "Material Transactions",
            "columns": ["Lot", "Type", "Qty", "Date", "Reference", "Remarks", "By"],
            "rows": rows,
            "add_url": "/materials/transactions/add/",
            "back_url": "/materials/",
        },
    )


@login_required
def txn_add(request):
    return _save_form(request, MaterialTransactionForm, "Material Transaction", "materials:txn_list", MaterialTransaction, form_subtitle="Outward transactions reduce the lot balance.")


@login_required
def stock(request):
    lots = (
        MaterialLot.objects.select_related("heat", "product")
        .filter(quantity_remaining__gt=0)
        .order_by("heat__heat_no", "lot_no")
    )
    total = sum((l.quantity_remaining for l in lots), 0)
    rows = [
        {
            "cells": [
                l.lot_no,
                l.heat.heat_no,
                l.heat.grade,
                l.product.name,
                l.bar_dia or "-",
                f"{l.quantity_remaining} {l.unit}",
                l.heat.supplier.name,
            ],
            "actions": [{"label": "View", "url": f"/materials/lots/{l.pk}/"}],
        }
        for l in lots
    ]
    return render(
        request,
        "materials/stock.html",
        {
            "page_title": "Stock Balance",
            "columns": ["Lot No", "Heat", "Grade", "Material", "Dia (mm)", "Balance", "Supplier"],
            "rows": rows,
            "total_lots": len(rows),
            "total_balance": total,
            "back_url": "/materials/",
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
                request, action, "materials", obj.pk,
                model=model.__name__, new=form.cleaned_data,
            )
            if hasattr(obj, "quantity_received") and hasattr(obj, "quantity_remaining"):
                if obj.quantity_remaining == 0 and obj.quantity_received:
                    obj.quantity_remaining = obj.quantity_received
                    obj.save(update_fields=["quantity_remaining"])
            messages.success(request, f"{title} saved successfully.")
            return redirect(redirect_name)
    else:
        form = form_cls(instance=instance)
    context = {
        "page_title": f"{'Edit' if instance else 'Add'} {title}",
        "form": form,
        "form_title": f"{'Edit' if instance else 'Add'} {title}",
        "form_subtitle": form_subtitle,
        "back_url": f"/materials/{redirect_name.split(':')[-1].replace('_list', '')}/",
    }
    return render(request, "partials/form_page.html", context)
