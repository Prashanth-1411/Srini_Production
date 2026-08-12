from django.urls import path

from . import views

app_name = "production"

urlpatterns = [
    path("", views.index, name="index"),
    path("jobs/", views.job_list, name="job_list"),
    path("jobs/add/", views.job_add, name="job_add"),
    path("jobs/<int:pk>/", views.job_detail, name="job_detail"),
    path("jobs/<int:pk>/edit/", views.job_edit, name="job_edit"),
    path("lots/", views.lot_list, name="lot_list"),
    path("lots/add/", views.lot_add, name="lot_add"),
    path("lots/<int:pk>/", views.lot_detail, name="lot_detail"),
    path("lots/<int:pk>/edit/", views.lot_edit, name="lot_edit"),
]
