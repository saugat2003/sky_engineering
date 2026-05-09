"""Tests for department app views and permissions.

Author: Rupesh Dahal"""

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from department.models import Department


class DepartmentCreateTests(TestCase):
    def setUp(self):
        """Create users for department creation tests."""
        self.staff_user = User.objects.create_user(
            username="admin",
            password="pass",
            is_staff=True,
        )
        self.regular_user = User.objects.create_user(
            username="engineer",
            password="pass",
        )

    def test_staff_user_can_create_department(self):
        """Verify staff users can create a department."""
        self.client.login(username="admin", password="pass")

        response = self.client.post(reverse("department_create"), {
            "name": "Platform Engineering",
            "description": "Shared platform services.",
            "specialisation": "Infrastructure and developer tooling.",
            "is_active": "on",
        })

        department = Department.objects.get(name="Platform Engineering")
        self.assertRedirects(response, reverse("depertment_detail", kwargs={"id": department.id}))
        self.assertTrue(department.is_active)

    def test_regular_user_cannot_access_create_department(self):
        """Verify non-staff users cannot access department creation."""
        self.client.login(username="engineer", password="pass")

        response = self.client.get(reverse("department_create"))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Department.objects.exists())
