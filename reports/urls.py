from django.urls import path

from . import views

app_name = "reports"

urlpatterns = [
    path("", views.index, name="index"),
    path("stock/", views.stock, name="stock"),
    path("production/", views.production, name="production"),
    path("quality/", views.quality, name="quality"),
    path("dispatch/", views.dispatch, name="dispatch"),
    path("export/<str:kind>/xlsx/", views.export_xlsx_view, name="export_xlsx"),
    path("export/<str:kind>/pdf/", views.export_pdf_view, name="export_pdf"),
]
