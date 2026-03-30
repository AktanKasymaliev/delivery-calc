from decimal import Decimal

from django.test import TestCase

from apps.calculator.models import City, Route, RouteTariff
from apps.calculator.services import RouteNotFoundError, TariffNotFoundError
from apps.calculator.services.engine import calculate_delivery_cost


class CalculateDeliveryCostTest(TestCase):
    def setUp(self):
        self.origin = City.objects.create(name="Гуанчжоу", country="Китай")
        self.destination = City.objects.create(name="Бишкек", country="Кыргызстан")
        self.route = Route.objects.create(
            from_city=self.origin,
            to_city=self.destination,
            delivery_days_from=18,
            delivery_days_to=20,
            calculation_type="weight",
            currency="USD",
        )
        self.tariff = RouteTariff.objects.create(
            route=self.route,
            min_weight=Decimal("0"),
            max_weight=Decimal("100"),
            min_volume=Decimal("0"),
            max_volume=Decimal("100"),
            price_per_kg=Decimal("180"),
            price_per_m3=Decimal("200"),
            margin_type="fixed",
            margin_value=Decimal("10"),
            priority=0,
        )

    def test_spec_example_weight_calculation(self):
        result = calculate_delivery_cost(
            self.origin.id, self.destination.id,
            weight=Decimal("1"), volume=Decimal("1"),
        )
        self.assertEqual(result.total_price, Decimal("190.00"))
        self.assertEqual(result.price_per_kg, Decimal("190.00"))
        self.assertEqual(result.delivery_time_from, 18)
        self.assertEqual(result.delivery_time_to, 20)
        self.assertEqual(result.currency, "USD")
        self.assertEqual(result.calculation_type, "weight")

    def test_weight_calculation_10kg(self):
        result = calculate_delivery_cost(
            self.origin.id, self.destination.id,
            weight=Decimal("10"), volume=Decimal("1"),
        )
        self.assertEqual(result.total_price, Decimal("1810.00"))
        self.assertEqual(result.price_per_kg, Decimal("181.00"))

    def test_volume_calculation(self):
        self.route.calculation_type = "volume"
        self.route.save()
        result = calculate_delivery_cost(
            self.origin.id, self.destination.id,
            weight=Decimal("1"), volume=Decimal("2"),
        )
        self.assertEqual(result.total_price, Decimal("410.00"))

    def test_max_value_calculation_weight_greater(self):
        self.route.calculation_type = "max_value"
        self.route.save()
        result = calculate_delivery_cost(
            self.origin.id, self.destination.id,
            weight=Decimal("10"), volume=Decimal("1"),
        )
        self.assertEqual(result.total_price, Decimal("1810.00"))

    def test_max_value_calculation_volume_greater(self):
        self.route.calculation_type = "max_value"
        self.route.save()
        result = calculate_delivery_cost(
            self.origin.id, self.destination.id,
            weight=Decimal("1"), volume=Decimal("10"),
        )
        self.assertEqual(result.total_price, Decimal("2010.00"))

    def test_mixed_calculation(self):
        self.route.calculation_type = "mixed"
        self.route.save()
        result = calculate_delivery_cost(
            self.origin.id, self.destination.id,
            weight=Decimal("1"), volume=Decimal("1"),
        )
        self.assertEqual(result.total_price, Decimal("390.00"))

    def test_percentage_margin(self):
        self.tariff.margin_type = "percentage"
        self.tariff.margin_value = Decimal("10")
        self.tariff.save()
        result = calculate_delivery_cost(
            self.origin.id, self.destination.id,
            weight=Decimal("1"), volume=Decimal("1"),
        )
        self.assertEqual(result.total_price, Decimal("198.00"))

    def test_minimum_price_enforcement(self):
        self.tariff.minimum_price = Decimal("500")
        self.tariff.save()
        result = calculate_delivery_cost(
            self.origin.id, self.destination.id,
            weight=Decimal("1"), volume=Decimal("1"),
        )
        self.assertEqual(result.total_price, Decimal("500.00"))

    def test_fixed_surcharge(self):
        self.tariff.fixed_surcharge = Decimal("20")
        self.tariff.save()
        result = calculate_delivery_cost(
            self.origin.id, self.destination.id,
            weight=Decimal("1"), volume=Decimal("1"),
        )
        self.assertEqual(result.total_price, Decimal("210.00"))

    def test_route_not_found(self):
        other_city = City.objects.create(name="Москва", country="Россия")
        with self.assertRaises(RouteNotFoundError):
            calculate_delivery_cost(
                self.origin.id, other_city.id,
                weight=Decimal("1"), volume=Decimal("1"),
            )

    def test_inactive_route_not_found(self):
        self.route.is_active = False
        self.route.save()
        with self.assertRaises(RouteNotFoundError):
            calculate_delivery_cost(
                self.origin.id, self.destination.id,
                weight=Decimal("1"), volume=Decimal("1"),
            )

    def test_tariff_not_found_out_of_range(self):
        with self.assertRaises(TariffNotFoundError):
            calculate_delivery_cost(
                self.origin.id, self.destination.id,
                weight=Decimal("150"), volume=Decimal("1"),
            )

    def test_weight_coefficient(self):
        self.tariff.weight_coefficient = Decimal("1.5")
        self.tariff.save()
        result = calculate_delivery_cost(
            self.origin.id, self.destination.id,
            weight=Decimal("1"), volume=Decimal("1"),
        )
        self.assertEqual(result.total_price, Decimal("280.00"))
