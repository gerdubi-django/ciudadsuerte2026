"""Helpers for tracking coupon reprints."""

from django.db import IntegrityError, transaction

from ..models import Coupon, CouponReprint, CouponReprintLog


def register_reprint(coupon: Coupon, user) -> tuple[bool, str]:
    """Persist a reprint attempt and prevent duplicates."""

    try:
        with transaction.atomic():
            coupon = Coupon.objects.select_for_update().get(pk=coupon.pk)
            if coupon.reprint_count >= 1:
                return False, "El cupón ya fue reimpreso previamente."

            coupon.reprint_count += 1
            coupon.save(update_fields=["reprint_count"])

            CouponReprint.objects.get_or_create(
                coupon=coupon, user=user, defaults={"room_id": coupon.room_id}
            )
            CouponReprintLog.objects.create(
                coupon=coupon,
                user=user,
                room_id=coupon.room_id,
                reprint_number=coupon.reprint_count,
            )
    except IntegrityError:
        return False, "El cupón ya fue reimpreso previamente."
    return True, "Reimpresión registrada."
