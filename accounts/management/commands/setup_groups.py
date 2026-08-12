from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

GROUPS = [
    "ADMIN",
    "STORES",
    "PRODUCTION",
    "GRINDING",
    "HEAT_TREATMENT",
    "QC",
    "DISPATCH",
    "MANAGEMENT",
]

# Per group: codename prefixes of permissions to grant on every model.
# "view" is always granted. "delete" is deliberately NOT granted for
# production/traceability data.
GROUP_PERMISSIONS = {
    "ADMIN": ["view", "add", "change", "delete"],
    "MANAGEMENT": ["view"],
    "STORES": ["view", "add", "change"],
    "PRODUCTION": ["view", "add", "change"],
    "GRINDING": ["view", "add", "change"],
    "HEAT_TREATMENT": ["view", "add", "change"],
    "QC": ["view", "add", "change"],
    "DISPATCH": ["view", "add", "change"],
}


class Command(BaseCommand):
    help = "Create default groups and assign permissions based on role."

    def handle(self, *args, **options):
        content_types = ContentType.objects.all()
        groups = {}

        for name in GROUPS:
            group, created = Group.objects.get_or_create(name=name)
            groups[name] = group
            self.stdout.write(
                "{} group '{}'".format("Created" if created else "Found", name)
            )

        perm_cache = {}
        for ct in content_types:
            perms = Permission.objects.filter(content_type=ct)
            for group_name, prefixes in GROUP_PERMISSIONS.items():
                allowed = [
                    p for p in perms
                    if any(p.codename.startswith(f"{prefix}_") for prefix in prefixes)
                ]
                groups[group_name].permissions.add(*allowed)

        self.stdout.write(self.style.SUCCESS("Groups and permissions configured."))
