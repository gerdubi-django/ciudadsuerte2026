import logging
from typing import List

from ..models import Coupon, PrinterConfiguration
from ..utils.terminal import DEFAULT_PRINTER_NAME, DEFAULT_PRINTER_PORT, get_terminal_config
from utils.printers import (
    USBPrinterError,
    build_escpos_bytes,
    list_usb_printers,
    pyusb_available,
    raw_print_usb,
    raw_print_windows,
)

LOGGER = logging.getLogger(__name__)


def get_or_create_printer_configuration() -> PrinterConfiguration:
    """Return the latest printer configuration or create a default one."""

    configuration = PrinterConfiguration.objects.order_by("-updated_at").first()
    if configuration is None:
        configuration = PrinterConfiguration.objects.create()
    return configuration


def print_coupon_backend(coupon: Coupon) -> None:
    """Print a coupon using the configured printer backends."""

    configuration = get_or_create_printer_configuration()
    terminal_config = get_terminal_config()
    printer_name = configuration.queue_name or DEFAULT_PRINTER_NAME
    printer_port = DEFAULT_PRINTER_PORT

    if terminal_config:
        printer_name = terminal_config.get("printer_name") or printer_name
        printer_port = terminal_config.get("printer_port") or printer_port

    payload = build_escpos_bytes(coupon)
    errors: List[str] = []
    try:
        vendor_id, product_id = configuration.usb_identifiers()
    except (TypeError, ValueError):
        vendor_id = product_id = None
    if vendor_id is not None and product_id is not None:
        try:
            raw_print_usb(vendor_id, product_id, payload)
            return
        except USBPrinterError as exc:  # pragma: no cover
            errors.append(f"USB printer error: {exc}")
        except Exception as exc:  # pragma: no cover
            errors.append(f"Unexpected USB error: {exc}")
    if printer_name:
        try:
            raw_print_windows(printer_name, payload)
            return
        except Exception as exc:  # pragma: no cover
            errors.append(f"Windows spooler error on {printer_port}: {exc}")
    if errors:  # pragma: no cover
        LOGGER.error("Coupon printing failed: %s", "; ".join(errors))


def available_printers():
    """Expose helper utilities required by admin views."""

    try:
        usb_devices = list_usb_printers()
    except NotImplementedError:
        usb_devices = []
    except Exception:  # pragma: no cover - hardware dependent
        usb_devices = []
    return {
        "usb_devices": usb_devices,
        "pyusb_available": pyusb_available(),
    }
