from dataclasses import dataclass
from decimal import Decimal

from apps.calculator.models import Route, RouteTariff
from apps.calculator.models.route import CalculationType
from apps.calculator.selectors import select_tariff
from apps.calculator.services import RouteNotFoundError
from apps.calculator.services.pricing import (
    apply_margin,
    enforce_minimum_price,
    round_price,
)


@dataclass(frozen=True)
class CalculationResult:
    price_per_kg: Decimal
    total_price: Decimal
    delivery_time_from: int
    delivery_time_to: int
    currency: str
    calculation_type: str


def _compute_weight_cost(
    weight: Decimal, tariff: RouteTariff
) -> Decimal:
    return weight * tariff.price_per_kg * tariff.weight_coefficient


def _compute_volume_cost(
    volume: Decimal, tariff: RouteTariff
) -> Decimal:
    return volume * tariff.price_per_m3 * tariff.volume_coefficient


def _compute_base_cost(
    calculation_type: str,
    weight: Decimal,
    volume: Decimal,
    tariff: RouteTariff,
) -> Decimal:
    weight_cost = _compute_weight_cost(weight, tariff)
    volume_cost = _compute_volume_cost(volume, tariff)

    if calculation_type == CalculationType.WEIGHT:
        return weight_cost
    if calculation_type == CalculationType.VOLUME:
        return volume_cost
    if calculation_type == CalculationType.MAX_VALUE:
        return max(weight_cost, volume_cost)
    return weight_cost + volume_cost


def calculate_delivery_cost(
    from_city_id: int,
    to_city_id: int,
    weight: Decimal,
    volume: Decimal,
) -> CalculationResult:
    route = (
        Route.objects.active()
        .select_related("from_city", "to_city")
        .filter(from_city_id=from_city_id, to_city_id=to_city_id)
        .first()
    )
    if route is None:
        raise RouteNotFoundError("Маршрут временно недоступен")

    tariff = select_tariff(route.id, weight, volume)

    base_cost = _compute_base_cost(
        route.calculation_type, weight, volume, tariff
    )

    cost_with_margin = apply_margin(base_cost, tariff)
    cost_with_surcharge = cost_with_margin + tariff.fixed_surcharge
    total_price = enforce_minimum_price(cost_with_surcharge, tariff.minimum_price)
    total_price = round_price(total_price)

    price_per_kg = round_price(total_price / weight) if weight > 0 else Decimal("0")

    return CalculationResult(
        price_per_kg=price_per_kg,
        total_price=total_price,
        delivery_time_from=route.delivery_days_from,
        delivery_time_to=route.delivery_days_to,
        currency=route.currency,
        calculation_type=route.calculation_type,
    )
