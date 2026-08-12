from django.urls import path

from . import views

app_name = "documents"

urlpatterns = [
    path("", views.index, name="index"),
    path("list/", views.document_list, name="list"),
    path("upload/", views.document_upload, name="upload"),
    path("<int:pk>/", views.document_detail, name="detail"),
    path("<int:pk>/edit/", views.document_edit, name="edit"),
    path("<int:pk>/delete/", views.document_delete, name="delete"),
    path("<int:pk>/view/", views.document_view, name="view"),
    path("<int:pk>/download/", views.document_download, name="download"),
]
