from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from .views import dashboard

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", dashboard, name="dashboard"),
    path("accounts/", include("accounts.urls")),
    path("traceability/", include("traceability.urls")),
    path("reports/", include("reports.urls")),
    path("masters/", include("masters.urls")),
    path("materials/", include("materials.urls")),
    path("production/", include("production.urls")),
    path("processes/", include("processes.urls")),
    path("heat-treatment/", include("heat_treatment.urls")),
    path("quality/", include("quality.urls")),
    path("dispatch/", include("dispatch.urls")),
    path("audit/", include("audit.urls")),
    path("documents/", include("documents.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
