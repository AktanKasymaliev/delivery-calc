from decimal import ROUND_HALF_UP, Decimal

from apps.calculator.models.tariff import MarginType, RouteTariff


def apply_margin(base_cost: Decimal, tariff: RouteTariff) -> Decimal:
    if tariff.margin_type == MarginType.FIXED:
        return base_cost + tariff.margin_value
    return base_cost * (1 + tariff.margin_value / Decimal("100"))


def enforce_minimum_price(total: Decimal, minimum_price: Decimal) -> Decimal:
    return max(total, minimum_price)


def round_price(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
