from django.db import models

from apps.core.models import TimeStampedModel


class MarginType(models.TextChoices):
    FIXED = "fixed", "Фиксированная"
    PERCENTAGE = "percentage", "Процент"


class TariffQuerySet(models.QuerySet):
    def active(self) -> "TariffQuerySet":
        return self.filter(is_active=True)

    def for_route(self, route_id: int) -> "TariffQuerySet":
        return self.filter(route_id=route_id)


class RouteTariff(TimeStampedModel):
    route = models.ForeignKey(
        "calculator.Route",
        on_delete=models.CASCADE,
        related_name="tariffs",
        verbose_name="Маршрут",
    )
    min_weight = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Мин. вес (кг)"
    )
    max_weight = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Макс. вес (кг)"
    )
    min_volume = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Мин. объём (м³)"
    )
    max_volume = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Макс. объём (м³)"
    )
    price_per_kg = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Тариф за кг"
    )
    price_per_m3 = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Тариф за м³"
    )
    margin_type = models.CharField(
        max_length=20,
        choices=MarginType.choices,
        default=MarginType.FIXED,
        verbose_name="Тип маржи",
    )
    margin_value = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Значение маржи"
    )
    fixed_surcharge = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Фикс. надбавка"
    )
    minimum_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Мин. стоимость"
    )
    weight_coefficient = models.DecimalField(
        max_digits=10, decimal_places=4, default=1, verbose_name="Коэфф. веса"
    )
    volume_coefficient = models.DecimalField(
        max_digits=10, decimal_places=4, default=1, verbose_name="Коэфф. объёма"
    )
    priority = models.IntegerField(default=0, verbose_name="Приоритет")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    objects = TariffQuerySet.as_manager()

    class Meta:
        db_table = "route_tariffs"
        ordering = ["-priority"]
        verbose_name = "Тариф"
        verbose_name_plural = "Тарифы"

    def __str__(self) -> str:
        return f"{self.route} | {self.min_weight}-{self.max_weight} кг"
