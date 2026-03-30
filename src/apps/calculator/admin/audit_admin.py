from django.contrib import admin

from apps.calculator.models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["entity_type", "entity_id", "action", "changed_by", "changed_at"]
    list_filter = ["entity_type", "action", "changed_at"]
    search_fields = ["entity_type", "changed_by__username"]
    readonly_fields = [
        "entity_type", "entity_id", "action",
        "old_value", "new_value", "changed_by", "changed_at",
    ]
    ordering = ["-changed_at"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
