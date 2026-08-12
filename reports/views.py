from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from dispatch.models import Dispatch
from materials.models import MaterialLot
from production.models import ProductionLot
from quality.models import QCInspection

from .exports import export_pdf, export_xlsx


def _stock_data():
    lots = MaterialLot.objects.select_related("heat__supplier", "product").order_by("heat__heat_no")
    rows = [
        {
            "cells": [
                l.lot_no,
                l.heat.heat_no,
                l.heat.grade,
                l.product.name,
                l.heat.supplier.name,
                f"{l.quantity_received} {l.unit}",
                f"{l.quantity_remaining} {l.unit}",
                l.status,
            ]
        }
        for l in lots
    ]
    return (
        "Stock Report",
        ["Lot", "Heat", "Grade", "Material", "Supplier", "Received", "Balance", "Status"],
        rows,
    )


def _production_data():
    lots = ProductionLot.objects.select_related(
        "job__customer", "job__product", "material_lot__heat"
    ).order_by("-created_at")
    rows = [
        {
            "cells": [
                l.lot_no,
                l.job.job_no,
                l.job.product.name,
                l.job.customer.name,
                l.material_lot.heat.heat_no,
                l.qty_started,
                l.qty_ok,
                l.qty_rework,
                l.qty_scrap,
                l.get_status_display(),
            ]
        }
        for l in lots
    ]
    return (
        "Production Report",
        ["Lot", "Job", "Product", "Customer", "Heat", "Started", "OK", "Rework", "Scrap", "Status"],
        rows,
    )


def _quality_data():
    inspections = QCInspection.objects.select_related(
        "production_lot__job__product"
    ).order_by("-inspection_date")
    rows = [
        {
            "cells": [
                i.inspection_no,
                i.production_lot.lot_no,
                i.production_lot.job.product.name,
                i.inspection_date or "-",
                i.qty_checked,
                i.qty_passed,
                i.qty_rework,
                i.qty_rejected,
                i.result,
            ]
        }
        for i in inspections
    ]
    return (
        "Quality Report",
        ["Inspection No", "Prod Lot", "Product", "Date", "Checked", "Passed", "Rework", "Rejected", "Result"],
        rows,
    )


def _dispatch_data():
    dispatches = Dispatch.objects.select_related("customer").prefetch_related("items").order_by("-dispatch_date")
    rows = [
        {
            "cells": [
                d.dispatch_no,
                d.customer.name,
                d.invoice_no or "-",
                d.dispatch_date,
                sum((i.quantity for i in d.items.all()), 0),
                d.status,
            ]
        }
        for d in dispatches
    ]
    return (
        "Dispatch Report",
        ["Dispatch No", "Customer", "Invoice", "Date", "Total Qty", "Status"],
        rows,
    )


_DATA = {
    "stock": _stock_data,
    "production": _production_data,
    "quality": _quality_data,
    "dispatch": _dispatch_data,
}

REPORT_LABELS = {
    "stock": "Stock Report",
    "production": "Production Report",
    "quality": "Quality Report",
    "dispatch": "Dispatch Report",
}


@login_required
def index(request):
    context = {
        "page_title": "Reports",
        "reports": [
            {"label": "Material Stock", "desc": "Current balance of every raw-material lot by heat number.", "url": "reports:stock", "kind": "stock"},
            {"label": "Production Summary", "desc": "Production lots with OK / rework / scrap quantities.", "url": "reports:production", "kind": "production"},
            {"label": "Quality Summary", "desc": "Inspection results, rework and scrap by production lot.", "url": "reports:quality", "kind": "quality"},
            {"label": "Dispatch Summary", "desc": "Dispatches and invoiced quantities by customer.", "url": "reports:dispatch", "kind": "dispatch"},
        ],
    }
    return render(request, "reports/index.html", context)


@login_required
def stock(request):
    return _render_report(request, "stock")


@login_required
def production(request):
    return _render_report(request, "production")


@login_required
def quality(request):
    return _render_report(request, "quality")


@login_required
def dispatch(request):
    return _render_report(request, "dispatch")


def _render_report(request, kind):
    title, columns, rows = _DATA[kind]()
    return render(
        request,
        "reports/report_page.html",
        {
            "page_title": title,
            "columns": columns,
            "rows": rows,
            "back_url": "/reports/",
            "export_kind": kind,
        },
    )


@login_required
def export_xlsx_view(request, kind):
    title, columns, rows = _DATA[kind]()
    return export_xlsx(title, columns, rows)


@login_required
def export_pdf_view(request, kind):
    title, columns, rows = _DATA[kind]()
    return export_pdf(title, columns, rows)
