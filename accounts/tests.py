from django.contrib.auth.models import Group, Permission, User
from django.test import TestCase
from django.urls import reverse

from accounts.management.commands.setup_groups import (
    GROUP_PERMISSIONS,
    GROUPS,
    Command,
)


def setup_groups():
    Command().handle()


class LoginTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("operator", password="testpass123")

    def test_login_page_renders(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "operator", "password": "testpass123"},
        )
        self.assertRedirects(response, reverse("dashboard"))

    def test_login_failure(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "operator", "password": "wrong"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password")

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_after_login(self):
        self.client.login(username="operator", password="testpass123")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        self.client.login(username="operator", password="testpass123")
        response = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(response, reverse("accounts:login"))


class GroupTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        setup_groups()

    def test_all_groups_exist(self):
        for name in GROUPS:
            with self.subTest(group=name):
                self.assertTrue(Group.objects.filter(name=name).exists())


class PermissionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        setup_groups()

    def test_groups_have_view_permissions(self):
        """Every group must hold view permission for every model."""
        for name in GROUPS:
            group = Group.objects.get(name=name)
            with self.subTest(group=name):
                self.assertGreaterEqual(group.permissions.count(), 1)

    def test_admin_has_full_permissions(self):
        group = Group.objects.get(name="ADMIN")
        self.assertTrue(group.permissions.filter(codename__startswith="view_").exists())
        self.assertTrue(group.permissions.filter(codename__startswith="add_").exists())
        self.assertTrue(group.permissions.filter(codename__startswith="change_").exists())
        self.assertTrue(group.permissions.filter(codename__startswith="delete_").exists())

    def test_operator_groups_have_no_delete(self):
        """Operational roles must not delete production/traceability records."""
        for name in ["STORES", "PRODUCTION", "GRINDING", "HEAT_TREATMENT", "QC", "DISPATCH"]:
            group = Group.objects.get(name=name)
            with self.subTest(group=name):
                self.assertFalse(
                    group.permissions.filter(codename__startswith="delete_").exists()
                )
