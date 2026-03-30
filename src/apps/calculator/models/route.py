from django.db import models

from apps.core.models import TimeStampedModel


class CalculationType(models.TextChoices):
    WEIGHT = "weight", "По весу"
    VOLUME = "volume", "По объёму"
    MAX_VALUE = "max_value", "По наибольшему значению"
    MIXED = "mixed", "Смешанный"


class RouteQuerySet(models.QuerySet):
    def active(self) -> "RouteQuerySet":
        return self.filter(is_active=True)


class Route(TimeStampedModel):
    from_city = models.ForeignKey(
        "calculator.City",
        on_delete=models.PROTECT,
        related_name="routes_from",
        verbose_name="Город отправки",
    )
    to_city = models.ForeignKey(
        "calculator.City",
        on_delete=models.PROTECT,
        related_name="routes_to",
        verbose_name="Город доставки",
    )
    delivery_days_from = models.PositiveIntegerField(verbose_name="Срок от (дней)")
    delivery_days_to = models.PositiveIntegerField(verbose_name="Срок до (дней)")
    calculation_type = models.CharField(
        max_length=20,
        choices=CalculationType.choices,
        default=CalculationType.WEIGHT,
        verbose_name="Тип расчёта",
    )
    currency = models.CharField(max_length=10, default="USD", verbose_name="Валюта")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    comment = models.TextField(blank=True, default="", verbose_name="Комментарий")

    objects = RouteQuerySet.as_manager()

    class Meta:
        db_table = "routes"
        unique_together = [("from_city", "to_city")]
        verbose_name = "Маршрут"
        verbose_name_plural = "Маршруты"

    def __str__(self) -> str:
        return f"{self.from_city} → {self.to_city}"
