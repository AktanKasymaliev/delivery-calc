import json
from decimal import Decimal

from django.test import Client, TestCase

from apps.calculator.models import City, Route, RouteTariff


class CitiesListApiTest(TestCase):
    def setUp(self):
        self.client = Client()
        City.objects.create(name="Гуанчжоу", country="Китай", is_active=True)
        City.objects.create(name="Закрытый", country="Тест", is_active=False)

    def test_returns_only_active_cities(self):
        response = self.client.get("/calculator/api/cities/")
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(len(data["data"]), 1)
        self.assertEqual(data["data"][0]["name"], "Гуанчжоу")

    def test_post_not_allowed(self):
        response = self.client.post("/calculator/api/cities/")
        self.assertEqual(response.status_code, 405)


class RoutesListApiTest(TestCase):
    def setUp(self):
        self.client = Client()
        origin = City.objects.create(name="Гуанчжоу", country="Китай")
        destination = City.objects.create(name="Бишкек", country="Кыргызстан")
        Route.objects.create(
            from_city=origin, to_city=destination,
            delivery_days_from=18, delivery_days_to=20,
            calculation_type="weight", is_active=True,
        )

    def test_returns_active_routes_with_city_details(self):
        response = self.client.get("/calculator/api/routes/")
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(len(data["data"]), 1)
        route = data["data"][0]
        self.assertEqual(route["from_city"]["name"], "Гуанчжоу")
        self.assertEqual(route["to_city"]["name"], "Бишкек")


class CalculateApiTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.origin = City.objects.create(name="Гуанчжоу", country="Китай")
        self.destination = City.objects.create(name="Бишкек", country="Кыргызстан")
        self.route = Route.objects.create(
            from_city=self.origin, to_city=self.destination,
            delivery_days_from=18, delivery_days_to=20,
            calculation_type="weight", currency="USD",
        )
        RouteTariff.objects.create(
            route=self.route,
            min_weight=Decimal("0"), max_weight=Decimal("100"),
            min_volume=Decimal("0"), max_volume=Decimal("100"),
            price_per_kg=Decimal("180"), margin_type="fixed",
            margin_value=Decimal("10"), priority=0,
        )

    def test_successful_calculation(self):
        response = self.client.post(
            "/calculator/api/calculate/",
            data=json.dumps({
                "from_city_id": self.origin.id,
                "to_city_id": self.destination.id,
                "weight": 1, "volume": 1,
            }),
            content_type="application/json",
        )
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["total_price"], "190.00")
        self.assertEqual(data["data"]["currency"], "USD")

    def test_missing_route_returns_error(self):
        other = City.objects.create(name="Москва", country="Россия")
        response = self.client.post(
            "/calculator/api/calculate/",
            data=json.dumps({
                "from_city_id": self.origin.id,
                "to_city_id": other.id,
                "weight": 1, "volume": 1,
            }),
            content_type="application/json",
        )
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(data["success"])

    def test_invalid_json_returns_400(self):
        response = self.client.post(
            "/calculator/api/calculate/",
            data="not json",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_missing_fields_returns_validation_error(self):
        response = self.client.post(
            "/calculator/api/calculate/",
            data=json.dumps({"from_city_id": 1}),
            content_type="application/json",
        )
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(data["success"])

    def test_get_not_allowed(self):
        response = self.client.get("/calculator/api/calculate/")
        self.assertEqual(response.status_code, 405)
