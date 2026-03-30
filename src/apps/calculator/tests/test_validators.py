from decimal import Decimal

from django.test import TestCase

from apps.calculator.services import CalculationValidationError
from apps.calculator.validators import validate_calculation_input


class ValidateCalculationInputTest(TestCase):
    def test_valid_input(self):
        result = validate_calculation_input({
            "from_city_id": 1,
            "to_city_id": 2,
            "weight": 10.5,
            "volume": 1.2,
        })
        self.assertEqual(result.from_city_id, 1)
        self.assertEqual(result.to_city_id, 2)
        self.assertEqual(result.weight, Decimal("10.5"))
        self.assertEqual(result.volume, Decimal("1.2"))

    def test_missing_from_city_id(self):
        with self.assertRaises(CalculationValidationError):
            validate_calculation_input({
                "to_city_id": 2,
                "weight": 10,
                "volume": 1,
            })

    def test_missing_to_city_id(self):
        with self.assertRaises(CalculationValidationError):
            validate_calculation_input({
                "from_city_id": 1,
                "weight": 10,
                "volume": 1,
            })

    def test_missing_weight(self):
        with self.assertRaises(CalculationValidationError):
            validate_calculation_input({
                "from_city_id": 1,
                "to_city_id": 2,
                "volume": 1,
            })

    def test_missing_volume(self):
        with self.assertRaises(CalculationValidationError):
            validate_calculation_input({
                "from_city_id": 1,
                "to_city_id": 2,
                "weight": 10,
            })

    def test_negative_weight(self):
        with self.assertRaises(CalculationValidationError):
            validate_calculation_input({
                "from_city_id": 1,
                "to_city_id": 2,
                "weight": -5,
                "volume": 1,
            })

    def test_zero_volume(self):
        with self.assertRaises(CalculationValidationError):
            validate_calculation_input({
                "from_city_id": 1,
                "to_city_id": 2,
                "weight": 10,
                "volume": 0,
            })

    def test_same_cities(self):
        with self.assertRaises(CalculationValidationError):
            validate_calculation_input({
                "from_city_id": 1,
                "to_city_id": 1,
                "weight": 10,
                "volume": 1,
            })

    def test_invalid_types(self):
        with self.assertRaises(CalculationValidationError):
            validate_calculation_input({
                "from_city_id": "abc",
                "to_city_id": 2,
                "weight": 10,
                "volume": 1,
            })
