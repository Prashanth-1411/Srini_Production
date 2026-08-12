from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from audit.services import log_action
from production.models import ProductionLot

from .forms import DispatchForm, DispatchItemFormSet
from .models import Dispatch


@login_required
def index(request):
    today = date.today()
    context = {
        "page_title": "Dispatch",
        "counts": [
            {"label": "Total Dispatches", "count": Dispatch.objects.count(), "url": "dispatch:list", "icon": "bi-truck"},
            {"label": "This Month", "count": Dispatch.objects.filter(dispatch_date__year=today.year, dispatch_date__month=today.month).count(), "url": "dispatch:list", "icon": "bi-calendar-month"},
            {"label": "QC Approved (ready)", "count": ProductionLot.objects.filter(status="QC_APPROVED").count(), "url": "dispatch:list", "icon": "bi-check2-circle"},
        ],
    }
    return render(request, "dispatch/index.html", context)


@login_required
def list_view(request):
    rows = [
        {
            "cells": [
                d.dispatch_no,
                d.customer.name,
                d.invoice_no or "-",
                d.dispatch_date,
                d.vehicle_no or "-",
                d.status,
                d.items.count(),
            ],
            "actions": [
                {"label": "View", "url": f"/dispatch/{d.pk}/"},
                {"label": "Edit", "url": f"/dispatch/{d.pk}/edit/"},
            ],
        }
        for d in Dispatch.objects.select_related("customer").prefetch_related("items").all()
    ]
    return render(
        request,
        "dispatch/list_page.html",
        {
            "page_title": "Dispatches",
            "columns": ["Dispatch No", "Customer", "Invoice", "Date", "Vehicle", "Status", "Items"],
            "rows": rows,
            "add_url": "/dispatch/add/",
            "back_url": "/dispatch/",
        },
    )


@login_required
def add_view(request):
    return _save_form(request, DispatchForm, DispatchItemFormSet, "Dispatch", "dispatch:list", Dispatch)


@login_required
def edit_view(request, pk):
    return _save_form(request, DispatchForm, DispatchItemFormSet, "Dispatch", "dispatch:list", Dispatch, pk)


@login_required
def detail_view(request, pk):
    dispatch = get_object_or_404(Dispatch.objects.select_related("customer"), pk=pk)
    items = dispatch.items.select_related("production_lot__job__product", "production_lot__material_lot__heat").all()
    return render(
        request,
        "dispatch/detail.html",
        {"page_title": f"Dispatch {dispatch.dispatch_no}", "dispatch": dispatch, "items": items},
    )


def _save_form(request, form_cls, formset_cls, title, redirect_name, model, pk=None):
    instance = get_object_or_404(model, pk=pk) if pk else None
    if request.method == "POST":
        form = form_cls(request.POST, instance=instance)
        formset = formset_cls(request.POST, instance=instance)
        if form.is_valid() and formset.is_valid():
            obj = form.save(commit=False)
            if hasattr(obj, "created_by") and obj.pk is None:
                obj.created_by = request.user
            obj.save()
            formset.instance = obj
            formset.save()
            for item in obj.items.all():
                lot = item.production_lot
                if lot.status == ProductionLot.STATUS_QC_APPROVED:
                    lot.status = ProductionLot.STATUS_DISPATCHED
                    lot.save(update_fields=["status"])
            action = "UPDATE" if instance else "CREATE"
            log_action(
                request, action, "dispatch", obj.pk,
                model=model.__name__, new=form.cleaned_data,
            )
            messages.success(request, f"{title} saved successfully.")
            return redirect("dispatch:list")
    else:
        form = form_cls(instance=instance)
        formset = formset_cls(instance=instance)
    context = {
        "page_title": f"{'Edit' if instance else 'Add'} {title}",
        "form": form,
        "formset": formset,
        "form_title": f"{'Edit' if instance else 'Add'} {title}",
        "form_subtitle": "Dispatch items mark the selected production lots as dispatched.",
        "back_url": "/dispatch/",
    }
    return render(request, "dispatch/form_page.html", context)
