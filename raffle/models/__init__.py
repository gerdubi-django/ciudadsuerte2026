# Import each model explicitly so Django registers them correctly.
from .rooms import Room
from .people import Person
from .printers import PrinterConfiguration
from .system import SystemSettings
from .coupons import (
    Coupon,
    CouponSequence,
    ManualCouponSequence,
    VoucherScan,
    CouponReprint,
    CouponReprintLog,
)

__all__ = [
    "Room",
    "Person",
    "PrinterConfiguration",
    "SystemSettings",
    "Coupon",
    "CouponSequence",
    "ManualCouponSequence",
    "VoucherScan",
    "CouponReprint",
    "CouponReprintLog",
]
