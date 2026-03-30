from django.contrib import admin

from apps.calculator.admin.tariff_admin import RouteTariffInline
from apps.calculator.models import Route, RouteTariff
from apps.calculator.services.logger import log_change, snapshot_instance


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = [
        "from_city", "to_city", "calculation_type",
        "delivery_days_from", "delivery_days_to",
        "currency", "is_active",
    ]
    list_filter = [
        "is_active", "calculation_type", "currency",
        "from_city", "to_city",
    ]
    search_fields = ["from_city__name", "to_city__name", "comment"]
    inlines = [RouteTariffInline]
    ordering = ["from_city__name", "to_city__name"]

    def save_model(self, request, obj, form, change):
        old_value = snapshot_instance(Route.objects.get(pk=obj.pk)) if change else None
        super().save_model(request, obj, form, change)
        log_change(
            entity_type="Route",
            entity_id=obj.pk,
            action="update" if change else "create",
            old_value=old_value,
            new_value=snapshot_instance(obj),
            user=request.user,
        )

    def save_formset(self, request, form, formset, change):
        if formset.model != RouteTariff:
            super().save_formset(request, form, formset, change)
            return

        existing_tariffs = {
            t.pk: snapshot_instance(t)
            for t in RouteTariff.objects.filter(
                pk__in=[f.instance.pk for f in formset.forms if f.instance.pk]
            )
        }

        instances = formset.save()
        for instance in instances:
            old_value = existing_tariffs.get(instance.pk)
            log_change(
                entity_type="RouteTariff",
                entity_id=instance.pk,
                action="update" if old_value else "create",
                old_value=old_value,
                new_value=snapshot_instance(instance),
                user=request.user,
            )

        for obj in formset.deleted_objects:
            log_change(
                entity_type="RouteTariff",
                entity_id=obj.pk,
                action="delete",
                old_value=existing_tariffs.get(obj.pk),
                user=request.user,
            )

    def delete_model(self, request, obj):
        old_value = snapshot_instance(obj)
        entity_id = obj.pk
        super().delete_model(request, obj)
        log_change(
            entity_type="Route",
            entity_id=entity_id,
            action="delete",
            old_value=old_value,
            user=request.user,
        )
