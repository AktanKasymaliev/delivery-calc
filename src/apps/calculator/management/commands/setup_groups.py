from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from apps.calculator.models import AuditLog, City, Route, RouteTariff

ROLE_PERMISSIONS = {
    "Администратор": {
        City: ["add", "change", "delete", "view"],
        Route: ["add", "change", "delete", "view"],
        RouteTariff: ["add", "change", "delete", "view"],
        AuditLog: ["view"],
    },
    "Менеджер": {
        City: ["view"],
        Route: ["view"],
        RouteTariff: ["change", "view"],
        AuditLog: ["view"],
    },
    "Наблюдатель": {
        City: ["view"],
        Route: ["view"],
        RouteTariff: ["view"],
        AuditLog: ["view"],
    },
}


class Command(BaseCommand):
    help = "Создает группы пользователей с правами доступа"

    def handle(self, *args, **options):
        for group_name, model_permissions in ROLE_PERMISSIONS.items():
            group, created = Group.objects.get_or_create(name=group_name)
            group.permissions.clear()

            for model_class, actions in model_permissions.items():
                content_type = ContentType.objects.get_for_model(model_class)
                for action in actions:
                    codename = f"{action}_{model_class._meta.model_name}"
                    permission = Permission.objects.get(
                        codename=codename, content_type=content_type
                    )
                    group.permissions.add(permission)

            status = "создана" if created else "обновлена"
            self.stdout.write(
                self.style.SUCCESS(f"Группа «{group_name}» {status}")
            )
