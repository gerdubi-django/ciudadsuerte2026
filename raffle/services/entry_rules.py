"""Validation helpers for entry workflows."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from django.utils import timezone

from ..models import Coupon, VoucherScan
from .coupons import calculate_entry_coupon_quantity


DAILY_ENTRY_LIMIT = 10


@dataclass
class EntryValidationResult:
    """Simple DTO for entry validation responses."""

    is_valid: bool
    message: str = ""


class EntryValidationError(Exception):
    """Raised when an entry attempt violates business rules."""


def validate_entry_rules(person, system_settings, lock_rows: bool = False) -> EntryValidationResult:
    """Validate whether a person can scan a voucher in the entry flow."""

    scan_qs = VoucherScan.objects.all()
    coupon_qs = Coupon.objects.filter(person=person, source=Coupon.ENTRY)
    if lock_rows:
        scan_qs = scan_qs.select_for_update()
        coupon_qs = coupon_qs.select_for_update()

    last_scan = scan_qs.filter(person=person).order_by("-scanned_at").first()
    if last_scan:
        cutoff = timezone.now() - timedelta(hours=2)
        if last_scan.scanned_at >= cutoff:
            return EntryValidationResult(
                False, "Solo puedes escanear un ticket cada dos horas."
            )

    now_value = timezone.now()
    today = timezone.localdate(now_value) if timezone.is_aware(now_value) else now_value.date()
    existing_coupons = coupon_qs.filter(scanned_at__date=today).count()
    projected_coupons = existing_coupons + calculate_entry_coupon_quantity(
        system_settings, requested_quantity=1
    )
    if projected_coupons > DAILY_ENTRY_LIMIT:
        return EntryValidationResult(
            False, "Se alcanzó el límite diario de 10 cupones para esta persona."
        )

    return EntryValidationResult(True, "")
