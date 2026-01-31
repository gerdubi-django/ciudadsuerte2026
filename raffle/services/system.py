"""Services for handling persistent system settings."""

from __future__ import annotations

import re
import socket
import uuid
from pathlib import Path

from django.conf import settings
from django.db import transaction

from ..models import SystemSettings
from ..rooms import RoomDirectory

LOCAL_IDENTIFIER_FILE = Path(settings.BASE_DIR) / ".terminal_identifier"


def _sanitize_identifier(value: str) -> str:
    """Normalize identifiers by removing symbols and trimming length."""

    return re.sub(r"[^A-Za-z0-9_-]+", "", value or "").strip()[:120] or "terminal"


def _read_local_identifier() -> str:
    """Return the cached terminal identifier or generate and persist a new one."""

    if LOCAL_IDENTIFIER_FILE.exists():
        cached = _sanitize_identifier(LOCAL_IDENTIFIER_FILE.read_text())
        if cached:
            return cached

    hostname = _sanitize_identifier(socket.gethostname())
    generated = _sanitize_identifier(f"{hostname or 'terminal'}-{uuid.uuid4().hex[:8]}")
    LOCAL_IDENTIFIER_FILE.write_text(generated)
    return generated


def get_or_create_system_settings():
    """Return the per-terminal SystemSettings instance without prompting the user."""

    identifier = _read_local_identifier()
    fallback_theme = SystemSettings.ThemePreference.LIGHT

    try:
        from ..models import PrinterConfiguration

        printer_theme = (
            PrinterConfiguration.objects.order_by("-updated_at")
            .values_list("theme_preference", flat=True)
            .first()
        )
        if printer_theme in dict(SystemSettings.ThemePreference.choices):
            fallback_theme = printer_theme
    except Exception:
        fallback_theme = SystemSettings.ThemePreference.LIGHT

    defaults = {
        "terminal_name": f"Terminal {identifier[-6:]}",
        "current_room_id": RoomDirectory.default_room_id(),
        "company_name": "Casinos Gala",
        "coupon_legend": (
            "El Juego Compulsivo es Perjudicial para la Salud y Produce Adicción ley 6169"
        ),
        "theme_preference": fallback_theme,
    }

    with transaction.atomic():
        settings_instance = SystemSettings.objects.filter(terminal_identifier=identifier).first()
        if settings_instance:
            if not settings_instance.theme_preference:
                settings_instance.theme_preference = fallback_theme
                settings_instance.save(update_fields=["theme_preference"])
            return settings_instance, False

        legacy_settings = SystemSettings.objects.order_by("id").first()
        if legacy_settings and legacy_settings.terminal_identifier == "default-terminal":
            legacy_settings.terminal_identifier = identifier
            legacy_settings.save(update_fields=["terminal_identifier"])
            return legacy_settings, False

        settings_instance, created = SystemSettings.objects.get_or_create(
            terminal_identifier=identifier, defaults=defaults
        )
        return settings_instance, created
