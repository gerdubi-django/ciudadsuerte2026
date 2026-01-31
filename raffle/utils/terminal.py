"""Terminal-scoped configuration helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from django.conf import settings

TERMINAL_CONFIG_FILENAME = "terminal_config.json"
TERMINAL_CONFIG_PATH = Path(settings.BASE_DIR) / TERMINAL_CONFIG_FILENAME
DEFAULT_PRINTER_NAME = "POS-80"
DEFAULT_PRINTER_PORT = "USB002"


def get_terminal_config_path() -> Path:
    """Return the absolute path to the local terminal configuration file."""

    return TERMINAL_CONFIG_PATH


def get_terminal_config() -> Optional[Dict[str, Any]]:
    """Load the terminal configuration from disk when available."""

    path = get_terminal_config_path()
    if not path.exists():
        return None

    try:
        raw_data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return None

    try:
        room_id = int(raw_data.get("room_id"))
    except (TypeError, ValueError):
        room_id = None

    terminal_id = str(raw_data.get("terminal_id", "")).strip()
    room_ip = str(raw_data.get("room_ip", "")).strip()
    printer_name = str(raw_data.get("printer_name") or DEFAULT_PRINTER_NAME).strip()
    printer_port = str(raw_data.get("printer_port") or DEFAULT_PRINTER_PORT).strip()

    if room_id is None or not terminal_id or not room_ip:
        return None

    return {
        "terminal_id": terminal_id,
        "room_id": room_id,
        "room_ip": room_ip,
        "printer_name": printer_name or DEFAULT_PRINTER_NAME,
        "printer_port": printer_port or DEFAULT_PRINTER_PORT,
    }


def save_terminal_config(
    terminal_id: Optional[str] = None,
    room_id: Optional[int] = None,
    room_ip: Optional[str] = None,
    printer_name: Optional[str] = None,
    printer_port: Optional[str] = None,
) -> Dict[str, Any]:
    """Persist the provided configuration to the local file."""

    existing_config = get_terminal_config() or {}
    payload = {
        "terminal_id": str(terminal_id or existing_config.get("terminal_id", "")).strip(),
        "room_id": int(room_id or existing_config.get("room_id", 0)),
        "room_ip": str(room_ip or existing_config.get("room_ip", "")).strip(),
        "printer_name": str(printer_name or existing_config.get("printer_name") or DEFAULT_PRINTER_NAME).strip(),
        "printer_port": str(printer_port or existing_config.get("printer_port") or DEFAULT_PRINTER_PORT).strip(),
    }

    if not payload["terminal_id"] or not payload["room_ip"] or not payload["room_id"]:
        raise ValueError("Terminal ID, room ID, and room IP are required to save configuration.")

    path = get_terminal_config_path()
    path.write_text(json.dumps(payload, indent=4), encoding="utf-8")
    return payload


def get_terminal_room() -> Optional[int]:
    """Return only the configured room identifier."""

    config = get_terminal_config()
    return None if config is None else config.get("room_id")


def get_terminal_ip() -> Optional[str]:
    """Return only the configured room IP address."""

    config = get_terminal_config()
    return None if config is None else config.get("room_ip")
