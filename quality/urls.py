from django.urls import path

from . import views

app_name = "quality"

urlpatterns = [
    path("", views.index, name="index"),
    path("inspections/", views.inspection_list, name="inspection_list"),
    path("inspections/add/", views.inspection_add, name="inspection_add"),
    path("inspections/<int:pk>/edit/", views.inspection_edit, name="inspection_edit"),
    path("rework/", views.rework_list, name="rework_list"),
    path("rework/add/", views.rework_add, name="rework_add"),
    path("rework/<int:pk>/edit/", views.rework_edit, name="rework_edit"),
    path("scrap/", views.scrap_list, name="scrap_list"),
    path("scrap/add/", views.scrap_add, name="scrap_add"),
    path("scrap/<int:pk>/edit/", views.scrap_edit, name="scrap_edit"),
]
