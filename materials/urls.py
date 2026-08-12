from django.urls import path

from . import views

app_name = "materials"

urlpatterns = [
    path("", views.index, name="index"),
    path("heats/", views.heat_list, name="heat_list"),
    path("heats/add/", views.heat_add, name="heat_add"),
    path("heats/<int:pk>/", views.heat_detail, name="heat_detail"),
    path("heats/<int:pk>/edit/", views.heat_edit, name="heat_edit"),
    path("lots/", views.lot_list, name="lot_list"),
    path("lots/add/", views.lot_add, name="lot_add"),
    path("lots/<int:pk>/", views.lot_detail, name="lot_detail"),
    path("lots/<int:pk>/edit/", views.lot_edit, name="lot_edit"),
    path("bars/", views.bar_list, name="bar_list"),
    path("bars/add/", views.bar_add, name="bar_add"),
    path("bars/<int:pk>/edit/", views.bar_edit, name="bar_edit"),
    path("transactions/", views.txn_list, name="txn_list"),
    path("transactions/add/", views.txn_add, name="txn_add"),
    path("stock/", views.stock, name="stock"),
]
