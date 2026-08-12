from django.urls import path

from . import views

app_name = "dispatch"

urlpatterns = [
    path("", views.index, name="index"),
    path("list/", views.list_view, name="list"),
    path("add/", views.add_view, name="add"),
    path("<int:pk>/", views.detail_view, name="detail"),
    path("<int:pk>/edit/", views.edit_view, name="edit"),
]
