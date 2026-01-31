"""Custom template filters for raffle templates."""

from django import template

register = template.Library()


@register.filter
def get_item(mapping, key):
    # Retrieve a mapping item safely.
    try:
        return mapping.get(key)
    except Exception:
        return None


ROOM_DISPLAY_NAMES = {
    "SCN": "Sala Central Necochea",
    "SCC": "Sala Castelli",
    "SSP": "Sala Saenz Peña",
    "SBQ": "Sala Barranqueras",
    "SFO": "Sala Fontana",
    "SGU": "Sala Guemes",
    "R11": "Sala Ruta 11",
}


@register.filter
def room_display_name(room_name):
    # Render a friendly room name without altering stored values.
    return ROOM_DISPLAY_NAMES.get(room_name, room_name)
