from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render

from .models import AuditLog


@login_required
def log_list(request):
    logs = AuditLog.objects.select_related("user").all()
    paginator = Paginator(logs, 50)
    page = paginator.get_page(request.GET.get("page"))
    rows = [
        {
            "cells": [
                l.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                l.username or "-",
                l.action,
                l.module,
                l.model or "-",
                l.record_id or "-",
                l.ip_address or "-",
            ]
        }
        for l in page.object_list
    ]
    return render(
        request,
        "audit/list_page.html",
        {
            "page_title": "Audit Log",
            "columns": ["Timestamp", "User", "Action", "Module", "Model", "Record ID", "IP"],
            "rows": rows,
            "pagination": True,
            "page_obj": page,
        },
    )
