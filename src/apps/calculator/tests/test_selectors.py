from decimal import Decimal

from django.test import TestCase

from apps.calculator.models import City, Route, RouteTariff
from apps.calculator.selectors import select_tariff
from apps.calculator.services import TariffNotFoundError


class SelectTariffTest(TestCase):
    def setUp(self):
        self.origin = City.objects.create(name="Гуанчжоу", country="Китай")
        self.destination = City.objects.create(name="Бишкек", country="Кыргызстан")
        self.route = Route.objects.create(
            from_city=self.origin,
            to_city=self.destination,
            delivery_days_from=18,
            delivery_days_to=20,
            calculation_type="weight",
        )
        self.tariff = RouteTariff.objects.create(
            route=self.route,
            min_weight=Decimal("0"),
            max_weight=Decimal("10"),
            min_volume=Decimal("0"),
            max_volume=Decimal("10"),
            price_per_kg=Decimal("180"),
            price_per_m3=Decimal("200"),
            margin_type="fixed",
            margin_value=Decimal("10"),
            priority=0,
        )

    def test_single_matching_tariff(self):
        result = select_tariff(self.route.id, Decimal("5"), Decimal("1"))
        self.assertEqual(result.id, self.tariff.id)

    def test_boundary_values_inclusive(self):
        result = select_tariff(self.route.id, Decimal("0"), Decimal("0"))
        self.assertEqual(result.id, self.tariff.id)

        result = select_tariff(self.route.id, Decimal("10"), Decimal("10"))
        self.assertEqual(result.id, self.tariff.id)

    def test_no_matching_tariff(self):
        with self.assertRaises(TariffNotFoundError):
            select_tariff(self.route.id, Decimal("15"), Decimal("1"))

    def test_inactive_tariff_excluded(self):
        self.tariff.is_active = False
        self.tariff.save()
        with self.assertRaises(TariffNotFoundError):
            select_tariff(self.route.id, Decimal("5"), Decimal("1"))

    def test_priority_selection(self):
        higher_priority_tariff = RouteTariff.objects.create(
            route=self.route,
            min_weight=Decimal("0"),
            max_weight=Decimal("10"),
            min_volume=Decimal("0"),
            max_volume=Decimal("10"),
            price_per_kg=Decimal("170"),
            price_per_m3=Decimal("190"),
            margin_type="fixed",
            margin_value=Decimal("5"),
            priority=10,
        )
        result = select_tariff(self.route.id, Decimal("5"), Decimal("1"))
        self.assertEqual(result.id, higher_priority_tariff.id)

    def test_wrong_route_no_match(self):
        other_city = City.objects.create(name="Москва", country="Россия")
        other_route = Route.objects.create(
            from_city=self.origin,
            to_city=other_city,
            delivery_days_from=5,
            delivery_days_to=7,
            calculation_type="weight",
        )
        with self.assertRaises(TariffNotFoundError):
            select_tariff(other_route.id, Decimal("5"), Decimal("1"))
