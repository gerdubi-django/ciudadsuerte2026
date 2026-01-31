"""Unit tests for voucher validation service."""

from __future__ import annotations

import json
from contextlib import contextmanager
from types import SimpleNamespace
from unittest import mock

from django.test import SimpleTestCase

from raffle.services import voucher_validation


@contextmanager
def stubbed_response(body: str):
    """Yield a fake HTTP response object with a fixed body."""

    class _Stub:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            return False

        def read(self):
            return body.encode("utf-8")

    yield _Stub()


class VoucherValidationTests(SimpleTestCase):
    """Validate ordering and responses from voucher validation."""

    def setUp(self):
        self.room = SimpleNamespace(room_ip="127.0.0.1")

    def test_validation_success_flow(self):
        """Validation returns success when remote marks voucher valid."""

        payload = json.dumps({"error": False, "message": "OK"})
        with mock.patch.object(voucher_validation.RoomDirectory, "get", return_value=self.room):
            with mock.patch.object(voucher_validation.request, "urlopen") as urlopen_mock:
                urlopen_mock.return_value = stubbed_response(payload)
                result = voucher_validation.validate_voucher_code("ABC", room_id=1)

        self.assertTrue(result.is_valid)
        self.assertEqual(result.message, "OK")

    def test_validation_handles_empty_response(self):
        """Validation fails with timeout message when API returns nothing."""

        with mock.patch.object(voucher_validation.RoomDirectory, "get", return_value=self.room):
            with mock.patch.object(voucher_validation.request, "urlopen") as urlopen_mock:
                urlopen_mock.return_value = stubbed_response("")
                result = voucher_validation.validate_voucher_code("ABC", room_id=1)

        self.assertFalse(result.is_valid)
        self.assertEqual(result.message, "Tiempo de espera de la API excedido.")

    def test_validation_handles_remote_error(self):
        """Validation fails when remote endpoint returns error payload."""

        payload = json.dumps({"error": True, "message": "Cupón No Pertenece a la Sala"})
        with mock.patch.object(voucher_validation.RoomDirectory, "get", return_value=self.room):
            with mock.patch.object(voucher_validation.request, "urlopen") as urlopen_mock:
                urlopen_mock.return_value = stubbed_response(payload)
                result = voucher_validation.validate_voucher_code("ABC", room_id=1)

        self.assertFalse(result.is_valid)
        self.assertEqual(result.message, "Cupón No Pertenece a la Sala")
