from django.db.models import Count, QuerySet

from ..models import Coupon
from ..rooms import RoomDirectory


def get_coupon_room_summary(queryset: QuerySet | None = None):
    """Build a list with coupon quantities per room."""

    coupon_qs = queryset or Coupon.objects.all()
    summary = []
    for item in coupon_qs.values("room_id").annotate(total=Count("id")).order_by("room_id"):
        room = RoomDirectory.get(item["room_id"])
        summary.append({"room": room, "total": item["total"]})
    return summary
