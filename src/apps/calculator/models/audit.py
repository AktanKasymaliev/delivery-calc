from django.conf import settings
from django.db import models


class AuditAction(models.TextChoices):
    CREATE = "create", "Создание"
    UPDATE = "update", "Изменение"
    DELETE = "delete", "Удаление"


class AuditLog(models.Model):
    entity_type = models.CharField(max_length=100, verbose_name="Тип сущности")
    entity_id = models.PositiveIntegerField(verbose_name="ID сущности")
    action = models.CharField(
        max_length=20, choices=AuditAction.choices, verbose_name="Действие"
    )
    old_value = models.JSONField(null=True, blank=True, verbose_name="Старое значение")
    new_value = models.JSONField(null=True, blank=True, verbose_name="Новое значение")
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Кем изменено",
    )
    changed_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата изменения")

    class Meta:
        db_table = "audit_log"
        ordering = ["-changed_at"]
        verbose_name = "Запись журнала"
        verbose_name_plural = "Журнал изменений"

    def __str__(self) -> str:
        return f"{self.entity_type} #{self.entity_id} — {self.action}"
