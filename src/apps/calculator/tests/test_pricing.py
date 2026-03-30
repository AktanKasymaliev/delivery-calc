from decimal import Decimal

from django.test import TestCase

from apps.calculator.models import City, Route, RouteTariff
from apps.calculator.services.pricing import (
    apply_margin,
    enforce_minimum_price,
    round_price,
)


class ApplyMarginTest(TestCase):
    def setUp(self):
        origin = City.objects.create(name="A", country="X")
        destination = City.objects.create(name="B", country="Y")
        route = Route.objects.create(
            from_city=origin,
            to_city=destination,
            delivery_days_from=1,
            delivery_days_to=2,
        )
        self.tariff = RouteTariff.objects.create(
            route=route,
            min_weight=0, max_weight=100,
            min_volume=0, max_volume=100,
            price_per_kg=100,
            margin_type="fixed",
            margin_value=Decimal("20"),
        )

    def test_fixed_margin(self):
        result = apply_margin(Decimal("180"), self.tariff)
        self.assertEqual(result, Decimal("200"))

    def test_percentage_margin(self):
        self.tariff.margin_type = "percentage"
        self.tariff.margin_value = Decimal("12")
        self.tariff.save()
        result = apply_margin(Decimal("100"), self.tariff)
        self.assertEqual(result, Decimal("112"))


class EnforceMinimumPriceTest(TestCase):
    def test_below_minimum(self):
        result = enforce_minimum_price(Decimal("95"), Decimal("120"))
        self.assertEqual(result, Decimal("120"))

    def test_above_minimum(self):
        result = enforce_minimum_price(Decimal("200"), Decimal("120"))
        self.assertEqual(result, Decimal("200"))

    def test_equal_to_minimum(self):
        result = enforce_minimum_price(Decimal("120"), Decimal("120"))
        self.assertEqual(result, Decimal("120"))


class RoundPriceTest(TestCase):
    def test_round_up(self):
        self.assertEqual(round_price(Decimal("10.555")), Decimal("10.56"))

    def test_round_down(self):
        self.assertEqual(round_price(Decimal("10.554")), Decimal("10.55"))

    def test_exact(self):
        self.assertEqual(round_price(Decimal("10.50")), Decimal("10.50"))
