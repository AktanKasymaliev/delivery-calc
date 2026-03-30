from django.contrib import admin

from apps.calculator.models import RouteTariff
from apps.calculator.services.logger import log_change, snapshot_instance


class RouteTariffInline(admin.TabularInline):
    model = RouteTariff
    extra = 1
    fields = [
        "min_weight", "max_weight", "min_volume", "max_volume",
        "price_per_kg", "price_per_m3", "margin_type", "margin_value",
        "fixed_surcharge", "minimum_price", "priority", "is_active",
    ]


@admin.register(RouteTariff)
class RouteTariffAdmin(admin.ModelAdmin):
    list_display = [
        "route", "min_weight", "max_weight", "min_volume", "max_volume",
        "price_per_kg", "price_per_m3", "margin_type", "margin_value",
        "priority", "is_active",
    ]
    list_filter = [
        "is_active", "margin_type",
        "route__from_city", "route__to_city",
        "route__calculation_type",
    ]
    search_fields = ["route__from_city__name", "route__to_city__name"]
    list_editable = ["is_active", "priority"]
    ordering = ["route", "-priority"]

    def save_model(self, request, obj, form, change):
        old_value = (
            snapshot_instance(RouteTariff.objects.get(pk=obj.pk)) if change else None
        )
        super().save_model(request, obj, form, change)
        log_change(
            entity_type="RouteTariff",
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
            entity_type="RouteTariff",
            entity_id=entity_id,
            action="delete",
            old_value=old_value,
            user=request.user,
        )
