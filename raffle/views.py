"""Entry points for raffle views delegated to controllers."""

from .controllers import (
    admin_clear_database,
    admin_configuration,
    admin_configuration_printers,
    admin_coupons,
    admin_dashboard,
    admin_login,
    admin_logout,
    admin_print_coupon,
    configure_terminal,
    entry,
    home,
    person_lookup,
    register,
    validate_entry_voucher,
)

__all__ = [
    "admin_clear_database",
    "admin_configuration",
    "admin_configuration_printers",
    "admin_coupons",
    "admin_dashboard",
    "admin_login",
    "admin_logout",
    "admin_print_coupon",
    "configure_terminal",
    "entry",
    "home",
    "person_lookup",
    "register",
    "validate_entry_voucher",
]
