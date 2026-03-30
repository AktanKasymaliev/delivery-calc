from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from apps.calculator.services import CalculationValidationError


@dataclass(frozen=True)
class CalculationInput:
    from_city_id: int
    to_city_id: int
    weight: Decimal
    volume: Decimal


def validate_calculation_input(data: dict) -> CalculationInput:
    from_city_id = _parse_positive_int(data.get("from_city_id"), "Выберите город отправки")
    to_city_id = _parse_positive_int(data.get("to_city_id"), "Выберите город доставки")

    if from_city_id == to_city_id:
        raise CalculationValidationError(
            "Город отправки и доставки не могут совпадать"
        )

    weight = _parse_positive_decimal(data.get("weight"), "Введите вес")
    volume = _parse_positive_decimal(data.get("volume"), "Введите объём")

    return CalculationInput(
        from_city_id=from_city_id,
        to_city_id=to_city_id,
        weight=weight,
        volume=volume,
    )


def _parse_positive_int(value: object, error_message: str) -> int:
    if value is None:
        raise CalculationValidationError(error_message)
    try:
        parsed = int(value)
    except (ValueError, TypeError):
        raise CalculationValidationError(error_message)
    if parsed <= 0:
        raise CalculationValidationError(error_message)
    return parsed


def _parse_positive_decimal(value: object, error_message: str) -> Decimal:
    if value is None:
        raise CalculationValidationError(error_message)
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, TypeError):
        raise CalculationValidationError(error_message)
    if parsed <= 0:
        raise CalculationValidationError(error_message)
    return parsed
