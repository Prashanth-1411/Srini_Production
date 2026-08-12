from django.urls import path

from . import views

app_name = "masters"

urlpatterns = [
    path("", views.index, name="index"),
    path("suppliers/", views.supplier_list, name="supplier_list"),
    path("suppliers/add/", views.supplier_add, name="supplier_add"),
    path("suppliers/<int:pk>/edit/", views.supplier_edit, name="supplier_edit"),
    path("suppliers/<int:pk>/delete/", views.supplier_delete, name="supplier_delete"),
    path("customers/", views.customer_list, name="customer_list"),
    path("customers/add/", views.customer_add, name="customer_add"),
    path("customers/<int:pk>/edit/", views.customer_edit, name="customer_edit"),
    path("customers/<int:pk>/delete/", views.customer_delete, name="customer_delete"),
    path("products/", views.product_list, name="product_list"),
    path("products/add/", views.product_add, name="product_add"),
    path("products/<int:pk>/edit/", views.product_edit, name="product_edit"),
    path("products/<int:pk>/delete/", views.product_delete, name="product_delete"),
    path("machines/", views.machine_list, name="machine_list"),
    path("machines/add/", views.machine_add, name="machine_add"),
    path("machines/<int:pk>/edit/", views.machine_edit, name="machine_edit"),
    path("machines/<int:pk>/delete/", views.machine_delete, name="machine_delete"),
    path("furnaces/", views.furnace_list, name="furnace_list"),
    path("furnaces/add/", views.furnace_add, name="furnace_add"),
    path("furnaces/<int:pk>/edit/", views.furnace_edit, name="furnace_edit"),
    path("furnaces/<int:pk>/delete/", views.furnace_delete, name="furnace_delete"),
    path("shifts/", views.shift_list, name="shift_list"),
    path("shifts/add/", views.shift_add, name="shift_add"),
    path("shifts/<int:pk>/edit/", views.shift_edit, name="shift_edit"),
    path("shifts/<int:pk>/delete/", views.shift_delete, name="shift_delete"),
]
