from typing import Any, Optional

from django.contrib.auth.models import AbstractUser
from django.forms.models import model_to_dict

from apps.calculator.models import AuditLog


def snapshot_instance(instance: Any) -> dict:
    data = model_to_dict(instance)
    return {
        key: str(value) if not isinstance(value, (str, int, float, bool, type(None)))
        else value
        for key, value in data.items()
    }


def log_change(
    entity_type: str,
    entity_id: int,
    action: str,
    old_value: Optional[dict] = None,
    new_value: Optional[dict] = None,
    user: Optional[AbstractUser] = None,
) -> AuditLog:
    return AuditLog.objects.create(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        old_value=old_value,
        new_value=new_value,
        changed_by=user,
    )
