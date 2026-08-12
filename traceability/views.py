from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from dispatch.models import Dispatch, DispatchItem
from materials.models import HeatNumber, MaterialLot
from production.models import ProductionLot


@login_required
def index(request):
    result = None
    query = request.GET.get("q", "").strip()
    mode = request.GET.get("mode", "forward")
    if query:
        if mode == "forward":
            result = _forward_trace(query)
        else:
            result = _backward_trace(query)
    return render(
        request,
        "traceability/index.html",
        {
            "page_title": "Traceability Center",
            "query": query,
            "mode": mode,
            "result": result,
        },
    )


def _forward_trace(query):
    heats = HeatNumber.objects.filter(heat_no__icontains=query).select_related("supplier")
    payload = []
    for heat in heats:
        lots = MaterialLot.objects.filter(heat=heat).select_related("product")
        plots = ProductionLot.objects.filter(material_lot__in=lots).select_related(
            "job__customer", "job__product", "machine", "material_lot"
        )
        dispatch_items = DispatchItem.objects.filter(production_lot__in=plots).select_related(
            "dispatch__customer", "production_lot"
        )
        payload.append(
            {
                "heat": heat,
                "lots": lots,
                "production_lots": plots,
                "dispatch_items": dispatch_items,
            }
        )
    return payload


def _backward_trace(query):
    dispatch_items = DispatchItem.objects.filter(
        dispatch__dispatch_no__icontains=query
    ).select_related("dispatch__customer", "production_lot__material_lot__heat__supplier")
    lots = ProductionLot.objects.filter(lot_no__icontains=query).select_related(
        "material_lot__heat__supplier", "job__customer", "job__product"
    )
    payload = {
        "dispatch_items": dispatch_items,
        "production_lots": lots,
    }
    return payload
