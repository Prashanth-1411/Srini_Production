from datetime import date

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from dispatch.models import Dispatch
from materials.models import HeatNumber, MaterialLot
from production.models import ProductionLot
from quality.models import QCInspection

import logging

logger = logging.getLogger("app")


def get_role(request):
    """Return the single highest-priority group name for the current user."""
    user = request.user
    if not user.is_authenticated:
        return None
    if user.is_superuser:
        return "ADMIN"
    order = [
        "ADMIN",
        "MANAGEMENT",
        "STORES",
        "QC",
        "DISPATCH",
        "HEAT_TREATMENT",
        "GRINDING",
        "PRODUCTION",
    ]
    groups = set(user.groups.values_list("name", flat=True))
    for name in order:
        if name in groups:
            return name
    return None


@login_required
def dashboard(request):
    role = get_role(request)
    today = date.today()
    stats = {
        "material_received": MaterialLot.objects.filter(received_date__year=today.year, received_date__month=today.month).count(),
        "heat_numbers": HeatNumber.objects.count(),
        "stock_lots": MaterialLot.objects.filter(quantity_remaining__gt=0).count(),
        "production_today": ProductionLot.objects.filter(start_date=today).count(),
        "qc_pending": ProductionLot.objects.filter(status=ProductionLot.STATUS_QC_PENDING).count(),
        "qc_approved": ProductionLot.objects.filter(status=ProductionLot.STATUS_QC_APPROVED).count(),
        "dispatched_today": Dispatch.objects.filter(dispatch_date=today).count(),
        "dispatches_month": Dispatch.objects.filter(dispatch_date__year=today.year, dispatch_date__month=today.month).count(),
        "inspections": QCInspection.objects.count(),
    }
    context = {
        "role": role,
        "page_title": "Dashboard",
        "stats": stats,
        "cards": _role_cards(role),
    }
    logger.info("Dashboard viewed by %s (role=%s)", request.user.username, role)
    return render(request, "dashboard/index.html", context)


def _role_cards(role):
    modules = {
        "ADMIN": ["Users & Groups", "Master Data", "Material Inward", "Production", "Quality", "Dispatch", "Audit Log"],
        "MANAGEMENT": ["Production", "Quality", "Dispatch", "Reports"],
        "STORES": ["Material Inward", "Material Lots", "Bars", "Material Balance"],
        "PRODUCTION": ["CNC Jobs", "Production Lots"],
        "GRINDING": ["Grinding Jobs"],
        "HEAT_TREATMENT": ["Furnace Batches"],
        "QC": ["Inspection", "Rework", "Scrap"],
        "DISPATCH": ["Dispatch"],
    }
    return modules.get(role, ["Dashboard", "Traceability Center", "Reports"])
