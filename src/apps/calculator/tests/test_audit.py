from django.contrib.auth.models import User
from django.test import TestCase

from apps.calculator.models import AuditLog, City
from apps.calculator.services.logger import log_change, snapshot_instance


class LogChangeTest(TestCase):
    def test_creates_audit_entry(self):
        entry = log_change(
            entity_type="City",
            entity_id=1,
            action="create",
            new_value={"name": "Бишкек"},
        )
        self.assertEqual(AuditLog.objects.count(), 1)
        self.assertEqual(entry.entity_type, "City")
        self.assertEqual(entry.action, "create")

    def test_with_user(self):
        user = User.objects.create_user(username="admin", password="test")
        entry = log_change(
            entity_type="Route",
            entity_id=1,
            action="update",
            old_value={"is_active": True},
            new_value={"is_active": False},
            user=user,
        )
        self.assertEqual(entry.changed_by, user)


class SnapshotInstanceTest(TestCase):
    def test_snapshot_city(self):
        city = City.objects.create(name="Бишкек", country="Кыргызстан")
        snapshot = snapshot_instance(city)
        self.assertEqual(snapshot["name"], "Бишкек")
        self.assertEqual(snapshot["country"], "Кыргызстан")
        self.assertIn("is_active", snapshot)
