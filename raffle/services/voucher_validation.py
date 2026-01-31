"""Voucher validation helpers for room-specific endpoints."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from urllib import error, request

from ..rooms import RoomDirectory
from ..utils.terminal import get_terminal_ip


@dataclass
class VoucherValidationResult:
    """Simple DTO representing a validation attempt."""

    is_valid: bool
    message: str


VALIDATION_ENABLED = os.getenv("VOUCHER_VALIDATION_ENABLED", "1") == "1"
VALIDATION_TIMEOUT = float(os.getenv("VOUCHER_VALIDATION_TIMEOUT", "5"))
VALIDATION_ACTION = os.getenv("VOUCHER_VALIDATION_ACTION", "getTicket")


def validate_voucher_code(code: str, room_id: int, room_ip: str | None = None) -> VoucherValidationResult:
    """Validate a voucher against the room-specific endpoint."""

    if not VALIDATION_ENABLED:
        return VoucherValidationResult(True, "Validación deshabilitada.")

    selected_ip = room_ip or get_terminal_ip() or RoomDirectory.get(room_id).room_ip
    if not selected_ip:
        return VoucherValidationResult(True, "Sala sin endpoint configurado.")

    url = f"http://{selected_ip}/api_app.php"
    payload = json.dumps({"strAction": VALIDATION_ACTION, "validCode": code}).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    request_obj = request.Request(url, data=payload, headers=headers, method="POST")

    try:
        with request.urlopen(request_obj, timeout=VALIDATION_TIMEOUT) as response:
            body = response.read().decode("utf-8")
        data = json.loads(body)
    except (error.URLError, json.JSONDecodeError, ValueError):
        return VoucherValidationResult(False, "Tiempo de espera de la API excedido.")

    is_valid = not bool(data.get("error"))
    message = (
        data.get("message")
        or ("Cupón Generado Correctamente" if is_valid else "Cupón No Pertenece a la Sala")
    )
    return VoucherValidationResult(is_valid, message)
