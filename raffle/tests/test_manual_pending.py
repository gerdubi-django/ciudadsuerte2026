from datetime import date
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from raffle.models import Coupon, Person


class CashierManualPendingTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.cashier = user_model.objects.create_user(
            username="cashier_one",
            password="secret",
            role=user_model.Role.CASHIER,
        )
        self.other_cashier = user_model.objects.create_user(
            username="cashier_two",
            password="secret",
            role=user_model.Role.CASHIER,
        )
        self.client.force_login(self.cashier)

    def test_cashier_register_creates_unprinted_coupons_for_current_user(self):
        payload = {
            "first_name": "Ana",
            "last_name": "Perez",
            "id_number": "30000001",
            "email": "ana@example.com",
            "phone": "5551234",
            "birth_date": "1990-01-01",
            "room_id": "1",
        }

        with patch("raffle.controllers.admin.print_coupon_backend") as print_mock:
            response = self.client.post(reverse("raffle_admin:cashier_register"), data=payload)

        self.assertEqual(response.status_code, 302)
        coupons = Coupon.objects.filter(person__id_number="30000001", source=Coupon.REGISTER)
        self.assertEqual(coupons.count(), 5)
        self.assertEqual(coupons.first().person.email, "ana@example.com")
        self.assertEqual(coupons.first().person.phone, "5551234")
        self.assertTrue(all(coupon.created_by_id == self.cashier.id for coupon in coupons))
        self.assertTrue(all(not coupon.printed for coupon in coupons))
        print_mock.assert_not_called()

    def test_manual_list_for_cashier_includes_pending_register_and_manual_from_user(self):
        person_one = Person.objects.create(
            first_name="A",
            last_name="One",
            id_number="40000001",
            phone="111",
            birth_date=date(1990, 1, 1),
        )
        person_two = Person.objects.create(
            first_name="B",
            last_name="Two",
            id_number="40000002",
            phone="222",
            birth_date=date(1991, 1, 1),
        )

        own_register = Coupon.objects.create(
            person=person_one,
            code="OWN-REGISTER-001",
            source=Coupon.REGISTER,
            room_id=2,
            created_by=self.cashier,
            printed=False,
        )
        own_manual = Coupon.objects.create(
            person=person_one,
            code="OWN-MANUAL-001",
            source=Coupon.MANUAL,
            room_id=3,
            created_by=self.cashier,
            printed=False,
        )
        Coupon.objects.create(
            person=person_two,
            code="OTHER-REGISTER-001",
            source=Coupon.REGISTER,
            room_id=1,
            created_by=self.other_cashier,
            printed=False,
        )

        response = self.client.get(reverse("raffle_admin:manual_list"))

        self.assertEqual(response.status_code, 200)
        coupons = list(response.context["coupons"])
        self.assertEqual({coupon.id for coupon in coupons}, {own_register.id, own_manual.id})

    def test_manual_list_shows_latest_ten_coupons_sorted_desc(self):
        person = Person.objects.create(
            first_name="Bulk",
            last_name="Coupons",
            id_number="40000999",
            phone="999",
            birth_date=date(1990, 1, 1),
        )
        base_time = timezone.now()
        created_ids = []

        for index in range(12):
            coupon = Coupon.objects.create(
                person=person,
                code=f"BULK-{index:03d}",
                source=Coupon.MANUAL,
                room_id=1,
                created_by=self.cashier,
                printed=False,
                scanned_at=base_time + timezone.timedelta(minutes=index),
            )
            created_ids.append(coupon.id)

        response = self.client.get(reverse("raffle_admin:manual_list"))

        self.assertEqual(response.status_code, 200)
        coupons = list(response.context["coupons"])
        self.assertEqual(len(coupons), 10)
        self.assertEqual([coupon.id for coupon in coupons], list(reversed(created_ids[-10:])))


class StaffManualRegisterAccessTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.admin_user = user_model.objects.create_user(
            username="admin_one",
            password="secret",
            role=user_model.Role.ADMIN,
        )
        self.manager_user = user_model.objects.create_user(
            username="manager_one",
            password="secret",
            role=user_model.Role.FLOOR_MANAGER,
            first_name="Floor",
            last_name="Manager",
        )

    def test_admin_can_access_manual_register_screen(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("raffle_admin:cashier_register"))

        self.assertEqual(response.status_code, 200)

    def test_manager_can_access_manual_register_screen(self):
        self.client.force_login(self.manager_user)

        response = self.client.get(reverse("raffle_admin:cashier_register"))

        self.assertEqual(response.status_code, 200)

    def test_manager_summary_uses_full_name(self):
        cashier = get_user_model().objects.create_user(
            username="cashier_summary",
            password="secret",
            role=get_user_model().Role.CASHIER,
            first_name="Ana",
            last_name="Gomez",
        )
        person = Person.objects.create(
            first_name="Client",
            last_name="One",
            id_number="49000001",
            phone="333",
            birth_date=date(1991, 1, 1),
        )
        Coupon.objects.create(
            person=person,
            code="SUMMARY-001",
            source=Coupon.MANUAL,
            room_id=1,
            created_by=cashier,
            printed=False,
        )

        self.client.force_login(self.manager_user)
        response = self.client.get(reverse("raffle_admin:manual_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ana Gomez")
