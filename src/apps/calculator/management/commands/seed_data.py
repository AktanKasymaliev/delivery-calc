from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.calculator.models import City, Route, RouteTariff


CITIES = [
    {"name": "Гуанчжоу", "country": "Китай"},
    {"name": "Бишкек", "country": "Кыргызстан"},
    {"name": "Москва", "country": "Россия"},
    {"name": "Алматы", "country": "Казахстан"},
]

ROUTES = [
    {
        "from": "Гуанчжоу", "to": "Бишкек",
        "days_from": 18, "days_to": 20,
        "calc_type": "weight", "currency": "USD",
    },
    {
        "from": "Гуанчжоу", "to": "Москва",
        "days_from": 25, "days_to": 30,
        "calc_type": "max_value", "currency": "USD",
    },
    {
        "from": "Гуанчжоу", "to": "Алматы",
        "days_from": 20, "days_to": 25,
        "calc_type": "mixed", "currency": "USD",
    },
    {
        "from": "Бишкек", "to": "Москва",
        "days_from": 5, "days_to": 7,
        "calc_type": "weight", "currency": "USD",
    },
    {
        "from": "Бишкек", "to": "Алматы",
        "days_from": 1, "days_to": 2,
        "calc_type": "weight", "currency": "USD",
    },
    {
        "from": "Москва", "to": "Бишкек",
        "days_from": 7, "days_to": 10,
        "calc_type": "volume", "currency": "USD",
    },
    {
        "from": "Москва", "to": "Алматы",
        "days_from": 5, "days_to": 8,
        "calc_type": "weight", "currency": "USD",
    },
    {
        "from": "Алматы", "to": "Бишкек",
        "days_from": 1, "days_to": 2,
        "calc_type": "weight", "currency": "USD",
    },
]


def _create_default_tariff(route, price_per_kg, price_per_m3, margin_value):
    RouteTariff.objects.get_or_create(
        route=route,
        min_weight=Decimal("0"),
        max_weight=Decimal("10000"),
        defaults={
            "min_volume": Decimal("0"),
            "max_volume": Decimal("10000"),
            "price_per_kg": Decimal(str(price_per_kg)),
            "price_per_m3": Decimal(str(price_per_m3)),
            "margin_type": "fixed",
            "margin_value": Decimal(str(margin_value)),
            "minimum_price": Decimal("0"),
            "priority": 0,
        },
    )


class Command(BaseCommand):
    help = "Заполняет базу тестовыми данными из ТЗ"

    def handle(self, *args, **options):
        cities = {}
        for city_data in CITIES:
            city, _ = City.objects.get_or_create(
                name=city_data["name"],
                defaults={"country": city_data["country"]},
            )
            cities[city_data["name"]] = city

        routes = {}
        for route_data in ROUTES:
            key = f"{route_data['from']}_{route_data['to']}"
            route, _ = Route.objects.get_or_create(
                from_city=cities[route_data["from"]],
                to_city=cities[route_data["to"]],
                defaults={
                    "delivery_days_from": route_data["days_from"],
                    "delivery_days_to": route_data["days_to"],
                    "calculation_type": route_data["calc_type"],
                    "currency": route_data["currency"],
                },
            )
            routes[key] = route

        gz_bk = routes["Гуанчжоу_Бишкек"]
        tariffs_gz_bk = [
            {"min_w": "0", "max_w": "10", "pkg": "180", "margin": "10", "prio": 2},
            {"min_w": "10", "max_w": "50", "pkg": "170", "margin": "10", "prio": 1},
            {"min_w": "50", "max_w": "10000", "pkg": "160", "margin": "10", "prio": 0},
        ]
        for t in tariffs_gz_bk:
            RouteTariff.objects.get_or_create(
                route=gz_bk,
                min_weight=Decimal(t["min_w"]),
                max_weight=Decimal(t["max_w"]),
                defaults={
                    "min_volume": Decimal("0"),
                    "max_volume": Decimal("10000"),
                    "price_per_kg": Decimal(t["pkg"]),
                    "price_per_m3": Decimal("200"),
                    "margin_type": "fixed",
                    "margin_value": Decimal(t["margin"]),
                    "minimum_price": Decimal("120"),
                    "priority": t["prio"],
                },
            )

        _create_default_tariff(routes["Гуанчжоу_Москва"], 150, 250, 15)
        _create_default_tariff(routes["Гуанчжоу_Алматы"], 160, 220, 15)
        _create_default_tariff(routes["Бишкек_Москва"], 120, 180, 10)
        _create_default_tariff(routes["Бишкек_Алматы"], 80, 100, 5)
        _create_default_tariff(routes["Москва_Бишкек"], 130, 200, 12)
        _create_default_tariff(routes["Москва_Алматы"], 110, 170, 10)
        _create_default_tariff(routes["Алматы_Бишкек"], 70, 90, 5)

        self.stdout.write(self.style.SUCCESS("Тестовые данные загружены"))
