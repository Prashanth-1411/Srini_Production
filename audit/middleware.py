from django.contrib.auth import logout
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

from .services import log_action


class AuditMiddleware(MiddlewareMixin):
    """Logs logouts and adds a reference to the request object."""

    def process_view(self, request, view_func, view_args, view_kwargs):
        request._audit = True
        return None
