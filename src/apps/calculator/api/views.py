import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from apps.calculator.models import City, Route
from apps.calculator.services import (
    CalculationValidationError,
    RouteNotFoundError,
    TariffNotFoundError,
)
from apps.calculator.services.engine import calculate_delivery_cost
from apps.calculator.validators import validate_calculation_input


@require_GET
def cities_list(request):
    cities = City.objects.active().values("id", "name", "country")
    return JsonResponse({"success": True, "data": list(cities)})


@require_GET
def routes_list(request):
    routes = (
        Route.objects.active()
        .select_related("from_city", "to_city")
        .values(
            "id",
            "from_city__id",
            "from_city__name",
            "to_city__id",
            "to_city__name",
            "delivery_days_from",
            "delivery_days_to",
            "calculation_type",
            "currency",
        )
    )
    data = [
        {
            "id": route["id"],
            "from_city": {
                "id": route["from_city__id"],
                "name": route["from_city__name"],
            },
            "to_city": {
                "id": route["to_city__id"],
                "name": route["to_city__name"],
            },
            "delivery_days_from": route["delivery_days_from"],
            "delivery_days_to": route["delivery_days_to"],
            "calculation_type": route["calculation_type"],
            "currency": route["currency"],
        }
        for route in routes
    ]
    return JsonResponse({"success": True, "data": data})


@csrf_exempt
@require_POST
def calculate(request):
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse(
            {"success": False, "message": "Неверный формат запроса"},
            status=400,
        )

    try:
        parsed = validate_calculation_input(body)
    except CalculationValidationError as exc:
        return JsonResponse(
            {"success": False, "message": str(exc)},
            status=400,
        )

    try:
        result = calculate_delivery_cost(
            from_city_id=parsed.from_city_id,
            to_city_id=parsed.to_city_id,
            weight=parsed.weight,
            volume=parsed.volume,
        )
    except (RouteNotFoundError, TariffNotFoundError) as exc:
        return JsonResponse(
            {"success": False, "message": str(exc)},
            status=400,
        )

    return JsonResponse({
        "success": True,
        "data": {
            "price_per_kg": str(result.price_per_kg),
            "total_price": str(result.total_price),
            "delivery_time_from": result.delivery_time_from,
            "delivery_time_to": result.delivery_time_to,
            "currency": result.currency,
            "calculation_type": result.calculation_type,
        },
    })
