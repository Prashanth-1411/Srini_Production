from django.urls import path

from . import views

app_name = "heat_treatment"

urlpatterns = [
    path("", views.index, name="index"),
    path("batches/", views.list_view, name="list"),
    path("batches/add/", views.add_view, name="add"),
    path("batches/<int:pk>/edit/", views.edit_view, name="edit"),
]
