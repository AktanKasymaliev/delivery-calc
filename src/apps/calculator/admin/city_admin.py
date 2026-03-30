from django.contrib import admin

from apps.calculator.models import City
from apps.calculator.services.logger import log_change, snapshot_instance


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ["name", "country", "is_active", "created_at"]
    list_filter = ["is_active", "country"]
    search_fields = ["name", "country"]
    list_editable = ["is_active"]
    ordering = ["name"]

    def save_model(self, request, obj, form, change):
        old_value = snapshot_instance(City.objects.get(pk=obj.pk)) if change else None
        super().save_model(request, obj, form, change)
        log_change(
            entity_type="City",
            entity_id=obj.pk,
            action="update" if change else "create",
            old_value=old_value,
            new_value=snapshot_instance(obj),
            user=request.user,
        )

    def delete_model(self, request, obj):
        old_value = snapshot_instance(obj)
        entity_id = obj.pk
        super().delete_model(request, obj)
        log_change(
            entity_type="City",
            entity_id=entity_id,
            action="delete",
            old_value=old_value,
            user=request.user,
        )
