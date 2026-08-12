from django.urls import path

from . import views

app_name = "processes"

urlpatterns = [
    path("", views.index, name="index"),
    path("records/", views.list_view, name="list"),
    path("records/add/", views.add_view, name="add"),
    path("records/<int:pk>/edit/", views.edit_view, name="edit"),
]
