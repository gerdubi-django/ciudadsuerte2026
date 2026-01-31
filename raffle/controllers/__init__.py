from .admin import (
    admin_clear_database,
    admin_configuration,
    admin_configuration_printers,
    admin_normalize_participants,
    admin_coupons,
    admin_dashboard,
    admin_login,
    admin_logout,
    admin_print_coupon,
    configure_terminal,
    room_dashboard,
    staff_register,
)
from .auth import admin_required, user_is_administrator
from .public import entry, home, person_lookup, register, validate_entry_voucher

__all__ = [
    "admin_clear_database",
    "admin_configuration",
    "admin_configuration_printers",
    "admin_normalize_participants",
    "admin_coupons",
    "admin_dashboard",
    "admin_login",
    "admin_logout",
    "admin_print_coupon",
    "configure_terminal",
    "room_dashboard",
    "staff_register",
    "admin_required",
    "entry",
    "home",
    "person_lookup",
    "register",
    "validate_entry_voucher",
    "user_is_administrator",
]


def __getattr__(name):
    """Lazy fallback to ensure public views remain importable."""

    if name == "validate_entry_voucher":
        from .public import validate_entry_voucher as view

        return view
    raise AttributeError(name)
