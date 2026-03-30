from decimal import Decimal

from apps.calculator.models import RouteTariff
from apps.calculator.services import TariffNotFoundError


def select_tariff(route_id: int, weight: Decimal, volume: Decimal) -> RouteTariff:
    tariff = (
        RouteTariff.objects.active()
        .for_route(route_id)
        .filter(
            min_weight__lte=weight,
            max_weight__gte=weight,
            min_volume__lte=volume,
            max_volume__gte=volume,
        )
        .first()
    )
    if tariff is None:
        raise TariffNotFoundError("Для данного направления нет активного тарифа")
    return tariff
