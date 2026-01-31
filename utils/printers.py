from __future__ import annotations

from typing import TYPE_CHECKING
import textwrap

try:
    import win32print
except ImportError:  # pragma: no cover
    win32print = None

try:  # pragma: no cover - platform dependent
    import usb.core
    import usb.util
    from usb.core import USBError
except ImportError:  # pragma: no cover
    usb = None
    usb_util = None
    USBError = Exception
else:  # pragma: no cover
    usb = usb.core
    usb_util = usb.util

if TYPE_CHECKING:  # pragma: no cover - type checking only
    from raffle.models import Coupon

MAX_LINE_LENGTH = 48
LABEL_WIDTH = 14
SEPARATOR_LINE = "=" * 40


class USBPrinterError(RuntimeError):
    """Raised when a USB printer cannot be accessed."""


def pyusb_available() -> bool:
    """Return whether pyusb is available in the current environment."""

    return usb is not None and usb_util is not None


def raw_print_windows(printer_name: str, payload: bytes):
    if win32print is None:
        raise RuntimeError("win32print is not available on this platform.")
    h = win32print.OpenPrinter(printer_name)
    try:
        win32print.StartDocPrinter(h, 1, ("Cupon", None, "RAW"))
        win32print.StartPagePrinter(h)
        win32print.WritePrinter(h, payload)
        win32print.EndPagePrinter(h)
        win32print.EndDocPrinter(h)
    finally:
        win32print.ClosePrinter(h)


def raw_print_usb(vendor_id: int, product_id: int, payload: bytes) -> None:
    if not pyusb_available():
        raise USBPrinterError("pyusb is not available in this environment.")
    device = usb.find(idVendor=vendor_id, idProduct=product_id)
    if device is None:
        raise USBPrinterError("USB printer not found for the provided identifiers.")
    try:
        device.set_configuration()
        configuration = device.get_active_configuration()
        endpoint = None
        selected_interface = None
        for interface in configuration:
            endpoint = usb_util.find_descriptor(
                interface,
                custom_match=lambda e: usb_util.endpoint_direction(e.bEndpointAddress)
                == usb_util.ENDPOINT_OUT,
            )
            if endpoint is not None:
                selected_interface = interface
                break
        if endpoint is None or selected_interface is None:
            raise USBPrinterError("USB printer endpoint not found.")
        interface_number = selected_interface.bInterfaceNumber
        kernel_detached = False
        try:
            if device.is_kernel_driver_active(interface_number):  # pragma: no cover
                device.detach_kernel_driver(interface_number)
                kernel_detached = True
        except (NotImplementedError, USBError):  # pragma: no cover
            pass
        usb_util.claim_interface(device, interface_number)
        try:
            endpoint.write(payload)
        finally:
            usb_util.release_interface(device, interface_number)
    finally:
        usb_util.dispose_resources(device)
        if "kernel_detached" in locals() and kernel_detached:  # pragma: no cover
            try:
                device.attach_kernel_driver(interface_number)
            except USBError:
                pass


def list_usb_printers() -> list[dict[str, str]]:
    if not pyusb_available():
        return []
    devices = []
    try:
        iterator = usb.find(find_all=True)
    except NotImplementedError:  # pragma: no cover - platform dependent
        return []
    for device in iterator:
        vendor_id = f"0x{device.idVendor:04X}"
        product_id = f"0x{device.idProduct:04X}"
        try:
            name = usb_util.get_string(device, device.iProduct) or "Unknown"
        except USBError:  # pragma: no cover
            name = "Unknown"
        try:
            manufacturer = usb_util.get_string(device, device.iManufacturer) or "Unknown"
        except USBError:  # pragma: no cover
            manufacturer = "Unknown"
        devices.append(
            {
                "vendor_id": vendor_id,
                "product_id": product_id,
                "name": name,
                "manufacturer": manufacturer,
            }
        )
    return devices


def build_coupon_text(coupon: "Coupon") -> str:
    """Return the standardized coupon text for ESC/POS printers."""

    def truncate(line: str) -> str:
        return line[:MAX_LINE_LENGTH]

    def center_header(text: str) -> str:
        return truncate(text.center(len(SEPARATOR_LINE)))

    def format_field(label: str, value: str) -> str:
        label_text = f"{label}:"
        return truncate(f"{label_text:<{LABEL_WIDTH}} {value}")

    person = getattr(coupon, "person", None)
    full_name = ""
    id_number = ""
    phone = ""

    if person is not None:
        names = [getattr(person, "first_name", ""), getattr(person, "last_name", "")]
        full_name = " ".join(part for part in names if part).strip()
        id_number = getattr(person, "id_number", "")
        phone = getattr(person, "phone", "")

    full_name = full_name or "-"
    id_number = id_number or "-"
    phone = phone or "-"
    coupon_code = getattr(coupon, "code", "-")
    room_name = getattr(coupon, "room_name", "-")
    scanned_at = getattr(coupon, "scanned_at", None)
    formatted_date = "-"

    if scanned_at is not None:
        formatted_date = scanned_at.strftime("%d/%m/%Y %H:%M")

    try:
        from raffle.services import get_or_create_system_settings
        settings_instance, _ = get_or_create_system_settings()
    except Exception:
        settings_instance = None

    company_name = getattr(settings_instance, "company_name", "Casinos Gala")
    coupon_legend = getattr(
        settings_instance,
        "coupon_legend",
        "El Juego Compulsivo es Perjudicial para la Salud y Produce Adicción ley 6169",
    )

    # --- CUERPO PRINCIPAL ---
    lines = [
        "",
        SEPARATOR_LINE,
        center_header(company_name.upper()),
        center_header("CIUDAD DE LA SUERTE"),
        SEPARATOR_LINE,
        format_field("Nombre", full_name),
        format_field("DNI", id_number),
        format_field("Teléfono", phone),
        "",
        format_field("Código cupón", coupon_code),
        format_field("Fecha", formatted_date),
        format_field("Sala", room_name),
        "",
        # SEPARADOR antes de la leyenda
        SEPARATOR_LINE,
    ]

    # --- LEYENDA ENVUELTA ---
    wrapped_legend = textwrap.wrap(coupon_legend, MAX_LINE_LENGTH) or [coupon_legend]
    lines.extend(wrapped_legend)

    # SEPARADOR debajo de la leyenda
    lines.append(SEPARATOR_LINE)

    # 2 líneas extra en blanco
    lines.append("")
    lines.append("")

    return "\n".join(lines)


def build_escpos_bytes(coupon):
    # Assemble the ESC/POS bytes, including initialization and cut commands.
    text = build_coupon_text(coupon)
    padding = b"\n" * 5
    return b"".join(
        [b"\x1b\x40", text.encode("cp858", "ignore"), padding, b"\x1d\x56\x00"]
    )
