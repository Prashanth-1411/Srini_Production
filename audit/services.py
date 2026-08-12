import json
import logging

logger = logging.getLogger("app")

try:
    from .models import AuditLog
except Exception:  # pragma: no cover - before first migration
    AuditLog = None


def get_client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _serialize(value):
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, default=str)
    return str(value)


def log_action(request, action, module, record_id, old=None, new=None,
               model="", user=None):
    if AuditLog is None:
        return None
    try:
        entry = AuditLog.objects.create(
            user=user if user is not None else getattr(request, "user", None),
            username=getattr(request, "user", None).username if hasattr(request, "user") else "",
            ip_address=get_client_ip(request) if request is not None else None,
            module=module,
            action=action,
            model=model,
            record_id=str(record_id) if record_id is not None else "",
            old_value=_serialize(old),
            new_value=_serialize(new),
        )
        return entry
    except Exception as exc:
        logger.warning("Audit log write failed: %s", exc)
        return None
