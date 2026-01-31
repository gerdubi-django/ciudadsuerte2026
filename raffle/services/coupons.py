"""Utility services for raffle coupon generation."""

from __future__ import annotations

from datetime import datetime
import re
from typing import List

from django.db import transaction
from django.utils import timezone

from ..models import (
    Coupon,
    CouponSequence,
    ManualCouponSequence,
    Person,
    SystemSettings,
)
from ..rooms import RoomDirectory
from .system import get_or_create_system_settings
from ..utils.terminal import get_terminal_config, get_terminal_room


def _sanitize_identifier(value: str) -> str:
    """Normalize identifiers by removing whitespace and symbols."""

    return re.sub(r"[^A-Za-z0-9]+", "", value or "").strip()


def generate_coupon_code(room_id: int, terminal_name: str) -> str:
    """Generate the next sequential coupon code for the room and terminal."""

    room_name = RoomDirectory.get(room_id).name
    cleaned_room = _sanitize_identifier(room_name) or f"ROOM{room_id}"
    cleaned_terminal = _sanitize_identifier(terminal_name) or "TERMINAL"
    with transaction.atomic():
        sequence, _ = CouponSequence.objects.select_for_update().get_or_create(
            room_id=room_id, terminal_name=terminal_name, defaults={"last_number": 0}
        )
        sequence.last_number += 1
        sequence.save(update_fields=["last_number"])
        return f"{cleaned_room}{cleaned_terminal}-{sequence.last_number:06d}"


def generate_manual_coupon_code(room_id: int) -> str:
    """Generate the manual code scoped by room using an atomic sequence."""

    room_name = RoomDirectory.get(room_id).name
    cleaned_room = _sanitize_identifier(room_name) or f"ROOM{room_id}"
    with transaction.atomic():
        sequence, _ = ManualCouponSequence.objects.select_for_update().get_or_create(
            room_id=room_id, defaults={"last_number": 0}
        )
        sequence.last_number += 1
        sequence.save(update_fields=["last_number"])
        return f"MN{cleaned_room}-{sequence.last_number:06d}"


def create_coupons(
    person: Person,
    quantity: int,
    source: str,
    room_id: int | None,
    terminal_name: str | None = None,
    system_settings: SystemSettings | None = None,
    created_by_user: bool = False,
) -> List[Coupon]:
    """Create the desired amount of coupons for a person."""

    settings, _ = (
        get_or_create_system_settings() if system_settings is None else (system_settings, False)
    )
    config = get_terminal_config()
    active_room_id = room_id or get_terminal_room() or settings.current_room_id
    terminal_label = terminal_name or (config or {}).get("terminal_id") or settings.terminal_name
    multiplier = _get_entry_multiplier(settings) if source == Coupon.ENTRY else 1
    effective_quantity = max(1, quantity) * multiplier
    entry_flag = created_by_user if source == Coupon.ENTRY else False
    coupons: List[Coupon] = []
    for _ in range(effective_quantity):
        coupon = Coupon.objects.create(
            person=person,
            code=generate_coupon_code(active_room_id, terminal_label),
            scanned_at=timezone.now(),
            source=source,
            created_by_user=entry_flag,
            room_id=active_room_id,
            terminal_name=terminal_label,
        )
        coupons.append(coupon)
    return coupons


def calculate_entry_coupon_quantity(
    system_settings: SystemSettings, requested_quantity: int = 1
) -> int:
    """Return the effective number of coupons that will be generated for an entry."""

    multiplier = _get_entry_multiplier(system_settings)
    return max(1, requested_quantity) * multiplier


def create_manual_coupon(person: Person, user, room_id: int) -> Coupon:
    """Create a manual coupon linked to the generator user and room."""

    code = generate_manual_coupon_code(room_id)
    terminal_name = getattr(user, "username", "")
    coupon = Coupon.objects.create(
        person=person,
        code=code,
        scanned_at=timezone.now(),
        source=Coupon.MANUAL,
        created_by=user,
        created_by_user=True,
        room_id=room_id,
        terminal_name=terminal_name,
        printed=False,
    )
    return coupon


def _get_entry_multiplier(settings: SystemSettings) -> int:
    # Determine the active multiplier based on the configured operational hours.
    schedule = settings.operational_hours or []
    now_reference = (
        timezone.localtime()
        if timezone.is_aware(timezone.now())
        else datetime.now()
    )
    now_time = now_reference.time()
    for slot in schedule:
        try:
            start_time = datetime.strptime(str(slot.get("start")), "%H:%M").time()
            end_time = datetime.strptime(str(slot.get("end")), "%H:%M").time()
            multiplier = int(slot.get("multiplier", 1))
        except (TypeError, ValueError):
            continue
        if start_time <= now_time <= end_time:
            return max(1, multiplier)
    return 1
