from django.db import models

from apps.core.models import TimeStampedModel


class CityQuerySet(models.QuerySet):
    def active(self) -> "CityQuerySet":
        return self.filter(is_active=True)


class City(TimeStampedModel):
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    objects = CityQuerySet.as_manager()

    class Meta:
        db_table = "cities"
        ordering = ["name"]
        verbose_name = "Город"
        verbose_name_plural = "Города"

    def __str__(self) -> str:
        return f"{self.name}, {self.country}"
