from datetime import date
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from .models import Coupon, Person, VoucherScan
from utils.printers import build_escpos_bytes


class VoucherScanModelTests(TestCase):
    def test_room_name_property_returns_human_readable_name(self):
        """Ensure the voucher scan exposes the readable room name."""

        person = Person.objects.create(
            first_name="Test",
            last_name="User",
            id_number="12345678",
            phone="5551234",
            birth_date=date(1990, 1, 1),
        )
        scan = VoucherScan.objects.create(
            code="VOUCHER-001",
            person=person,
            room_id=1,
            source=Coupon.ENTRY,
        )

        self.assertEqual(scan.room_name, "Sala A")


class EntryViewTests(TestCase):
    def setUp(self):
        self.person = Person.objects.create(
            first_name="Sample",
            last_name="User",
            id_number="87654321",
            phone="5559876",
            birth_date=date(1990, 5, 17),
        )

    def test_entry_scan_generates_coupon_and_triggers_print(self):
        """Ensure scanning a voucher generates a coupon and prints it."""

        payload = {
            "id_number": self.person.id_number,
            "room_id": "1",
            "voucher_code": "scan-001",
        }
        with patch("raffle.controllers.public.print_coupon_backend") as mock_print:
            response = self.client.post(reverse("raffle:entry"), data=payload)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("raffle:home"))

        scan_exists = VoucherScan.objects.filter(code="SCAN-001", person=self.person).exists()
        self.assertTrue(scan_exists)

        coupons = Coupon.objects.filter(person=self.person, source=Coupon.ENTRY)
        self.assertEqual(coupons.count(), 1)
        mock_print.assert_called_once()
        printed_coupon = mock_print.call_args[0][0]
        self.assertEqual(printed_coupon.id, coupons.first().id)


class CouponPrintingTests(TestCase):
    def test_coupon_payload_contains_trailing_blank_lines(self):
        """Ensure coupon printing includes trailing blank lines before cutting."""

        person = Person.objects.create(
            first_name="Print",
            last_name="Tester",
            id_number="11112222",
            phone="5554444",
            birth_date=date(1985, 7, 1),
        )
        coupon = Coupon.objects.create(
            person=person,
            code="PRINT-001",
            source=Coupon.ENTRY,
            room_id=1,
        )

        payload = build_escpos_bytes(coupon)
        self.assertTrue(payload.endswith(b"\n\n\n\n\n\x1d\x56\x00"))
