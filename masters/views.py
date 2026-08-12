import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from audit.services import log_action

from .forms import CustomerForm, FurnaceForm, MachineForm, ProductForm, ShiftForm, SupplierForm
from .models import Customer, Furnace, Machine, Product, Shift, Supplier

logger = logging.getLogger("app")


def _badge(ok):
    return (
        '<span class="badge bg-success">Active</span>'
        if ok
        else '<span class="badge bg-secondary">Inactive</span>'
    )


def _actions(edit_url, del_url):
    return [
        {"label": "Edit", "url": edit_url},
        {"label": "Del", "url": del_url},
    ]


@login_required
def index(request):
    context = {
        "page_title": "Master Data",
        "counts": [
            {"label": "Suppliers", "count": Supplier.objects.count(), "url": "masters:supplier_list", "icon": "bi-truck-flatbed"},
            {"label": "Customers", "count": Customer.objects.count(), "url": "masters:customer_list", "icon": "bi-people"},
            {"label": "Products", "count": Product.objects.count(), "url": "masters:product_list", "icon": "bi-box"},
            {"label": "Machines", "count": Machine.objects.count(), "url": "masters:machine_list", "icon": "bi-cpu"},
            {"label": "Furnaces", "count": Furnace.objects.count(), "url": "masters:furnace_list", "icon": "bi-fire"},
            {"label": "Shifts", "count": Shift.objects.count(), "url": "masters:shift_list", "icon": "bi-clock-history"},
        ],
    }
    return render(request, "masters/index.html", context)


def _crud(request, model, form_cls, template, list_name, title, pk=None, extra=None):
    instance = get_object_or_404(model, pk=pk) if pk else None
    if request.method == "POST":
        form = form_cls(request.POST, instance=instance)
        if form.is_valid():
            obj = form.save()
            action = "UPDATE" if instance else "CREATE"
            log_action(
                request, action, "masters", getattr(obj, "pk", ""),
                model=model.__name__, new=form.cleaned_data,
            )
            messages.success(request, f"{title} saved successfully.")
            return redirect(list_name)
    else:
        form = form_cls(instance=instance)
    context = {
        "page_title": f"{'Edit' if instance else 'Add'} {title}",
        "form": form,
        "form_title": f"{'Edit' if instance else 'Add'} {title}",
        "back_url": f"/masters/{list_name.split(':')[-1].replace('_list', '')}/",
    }
    if extra:
        context.update(extra)
    return render(request, template, context)


@login_required
def supplier_list(request):
    rows = [
        {
            "cells": [
                s.code,
                s.name,
                s.gstin or "-",
                s.phone or "-",
                _badge(s.active),
            ],
            "actions": _actions(
                f"/masters/suppliers/{s.pk}/edit/", f"/masters/suppliers/{s.pk}/delete/"
            ),
        }
        for s in Supplier.objects.all()
    ]
    return render(
        request,
        "masters/list_page.html",
        {
            "page_title": "Suppliers",
            "columns": ["Code", "Name", "GSTIN", "Phone", "Status"],
            "rows": rows,
            "add_url": "/masters/suppliers/add/",
            "back_url": "/masters/",
        },
    )


@login_required
def supplier_add(request):
    return _crud(request, Supplier, SupplierForm, "partials/form_page.html", "masters:supplier_list", "Supplier")


@login_required
def supplier_edit(request, pk):
    return _crud(request, Supplier, SupplierForm, "partials/form_page.html", "masters:supplier_list", "Supplier", pk)


@login_required
def supplier_delete(request, pk):
    obj = get_object_or_404(Supplier, pk=pk)
    if request.method == "POST":
        name = str(obj)
        obj.delete()
        log_action(request, "DEACTIVATE", "masters", name, model="Supplier")
        messages.success(request, f"Supplier '{name}' deleted.")
        return redirect("masters:supplier_list")
    return render(
        request,
        "partials/confirm_delete.html",
        {"object": obj, "page_title": "Delete Supplier", "back_url": "/masters/suppliers/"},
    )


@login_required
def customer_list(request):
    rows = [
        {
            "cells": [c.code, c.name, c.gstin or "-", c.phone or "-", _badge(c.active)],
            "actions": _actions(f"/masters/customers/{c.pk}/edit/", f"/masters/customers/{c.pk}/delete/"),
        }
        for c in Customer.objects.all()
    ]
    return render(
        request,
        "masters/list_page.html",
        {
            "page_title": "Customers",
            "columns": ["Code", "Name", "GSTIN", "Phone", "Status"],
            "rows": rows,
            "add_url": "/masters/customers/add/",
            "back_url": "/masters/",
        },
    )


@login_required
def customer_add(request):
    return _crud(request, Customer, CustomerForm, "partials/form_page.html", "masters:customer_list", "Customer")


@login_required
def customer_edit(request, pk):
    return _crud(request, Customer, CustomerForm, "partials/form_page.html", "masters:customer_list", "Customer", pk)


@login_required
def customer_delete(request, pk):
    obj = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        name = str(obj)
        obj.delete()
        log_action(request, "DEACTIVATE", "masters", name, model="Customer")
        messages.success(request, f"Customer '{name}' deleted.")
        return redirect("masters:customer_list")
    return render(
        request,
        "partials/confirm_delete.html",
        {"object": obj, "page_title": "Delete Customer", "back_url": "/masters/customers/"},
    )


@login_required
def product_list(request):
    rows = [
        {
            "cells": [p.code, p.name, p.drawing_no or "-", p.material_spec or "-", _badge(p.active)],
            "actions": _actions(f"/masters/products/{p.pk}/edit/", f"/masters/products/{p.pk}/delete/"),
        }
        for p in Product.objects.all()
    ]
    return render(
        request,
        "masters/list_page.html",
        {
            "page_title": "Products",
            "columns": ["Code", "Name", "Drawing No", "Material Spec", "Status"],
            "rows": rows,
            "add_url": "/masters/products/add/",
            "back_url": "/masters/",
        },
    )


@login_required
def product_add(request):
    return _crud(request, Product, ProductForm, "partials/form_page.html", "masters:product_list", "Product")


@login_required
def product_edit(request, pk):
    return _crud(request, Product, ProductForm, "partials/form_page.html", "masters:product_list", "Product", pk)


@login_required
def product_delete(request, pk):
    obj = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        name = str(obj)
        obj.delete()
        log_action(request, "DEACTIVATE", "masters", name, model="Product")
        messages.success(request, f"Product '{name}' deleted.")
        return redirect("masters:product_list")
    return render(
        request,
        "partials/confirm_delete.html",
        {"object": obj, "page_title": "Delete Product", "back_url": "/masters/products/"},
    )


@login_required
def machine_list(request):
    rows = [
        {
            "cells": [m.code, m.name, m.get_machine_type_display(), m.location or "-", _badge(m.active)],
            "actions": _actions(f"/masters/machines/{m.pk}/edit/", f"/masters/machines/{m.pk}/delete/"),
        }
        for m in Machine.objects.all()
    ]
    return render(
        request,
        "masters/list_page.html",
        {
            "page_title": "Machines",
            "columns": ["Code", "Name", "Type", "Location", "Status"],
            "rows": rows,
            "add_url": "/masters/machines/add/",
            "back_url": "/masters/",
        },
    )


@login_required
def machine_add(request):
    return _crud(request, Machine, MachineForm, "partials/form_page.html", "masters:machine_list", "Machine")


@login_required
def machine_edit(request, pk):
    return _crud(request, Machine, MachineForm, "partials/form_page.html", "masters:machine_list", "Machine", pk)


@login_required
def machine_delete(request, pk):
    obj = get_object_or_404(Machine, pk=pk)
    if request.method == "POST":
        name = str(obj)
        obj.delete()
        log_action(request, "DEACTIVATE", "masters", name, model="Machine")
        messages.success(request, f"Machine '{name}' deleted.")
        return redirect("masters:machine_list")
    return render(
        request,
        "partials/confirm_delete.html",
        {"object": obj, "page_title": "Delete Machine", "back_url": "/masters/machines/"},
    )


@login_required
def furnace_list(request):
    rows = [
        {
            "cells": [f.code, f.name, f.furnace_type or "-", f.capacity or "-", _badge(f.active)],
            "actions": _actions(f"/masters/furnaces/{f.pk}/edit/", f"/masters/furnaces/{f.pk}/delete/"),
        }
        for f in Furnace.objects.all()
    ]
    return render(
        request,
        "masters/list_page.html",
        {
            "page_title": "Furnaces",
            "columns": ["Code", "Name", "Type", "Capacity", "Status"],
            "rows": rows,
            "add_url": "/masters/furnaces/add/",
            "back_url": "/masters/",
        },
    )


@login_required
def furnace_add(request):
    return _crud(request, Furnace, FurnaceForm, "partials/form_page.html", "masters:furnace_list", "Furnace")


@login_required
def furnace_edit(request, pk):
    return _crud(request, Furnace, FurnaceForm, "partials/form_page.html", "masters:furnace_list", "Furnace", pk)


@login_required
def furnace_delete(request, pk):
    obj = get_object_or_404(Furnace, pk=pk)
    if request.method == "POST":
        name = str(obj)
        obj.delete()
        log_action(request, "DEACTIVATE", "masters", name, model="Furnace")
        messages.success(request, f"Furnace '{name}' deleted.")
        return redirect("masters:furnace_list")
    return render(
        request,
        "partials/confirm_delete.html",
        {"object": obj, "page_title": "Delete Furnace", "back_url": "/masters/furnaces/"},
    )


@login_required
def shift_list(request):
    rows = [
        {
            "cells": [s.name, s.start_time, s.end_time, _badge(s.active)],
            "actions": _actions(f"/masters/shifts/{s.pk}/edit/", f"/masters/shifts/{s.pk}/delete/"),
        }
        for s in Shift.objects.all()
    ]
    return render(
        request,
        "masters/list_page.html",
        {
            "page_title": "Shifts",
            "columns": ["Name", "Start", "End", "Status"],
            "rows": rows,
            "add_url": "/masters/shifts/add/",
            "back_url": "/masters/",
        },
    )


@login_required
def shift_add(request):
    return _crud(request, Shift, ShiftForm, "partials/form_page.html", "masters:shift_list", "Shift")


@login_required
def shift_edit(request, pk):
    return _crud(request, Shift, ShiftForm, "partials/form_page.html", "masters:shift_list", "Shift", pk)


@login_required
def shift_delete(request, pk):
    obj = get_object_or_404(Shift, pk=pk)
    if request.method == "POST":
        name = str(obj)
        obj.delete()
        log_action(request, "DEACTIVATE", "masters", name, model="Shift")
        messages.success(request, f"Shift '{name}' deleted.")
        return redirect("masters:shift_list")
    return render(
        request,
        "partials/confirm_delete.html",
        {"object": obj, "page_title": "Delete Shift", "back_url": "/masters/shifts/"},
    )

