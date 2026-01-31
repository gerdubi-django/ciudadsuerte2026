"""Models for system-level configuration."""

from django.db import models

from ..rooms import RoomDirectory


def default_operational_hours() -> list[dict]:
    # Provide an empty schedule to avoid mutable defaults.
    return []


class SystemSettings(models.Model):
    class ThemePreference(models.TextChoices):
        LIGHT = "light", "Tema claro"
        DARK = "dark", "Tema oscuro"

    terminal_identifier = models.CharField(max_length=120, unique=True, default="default-terminal")
    terminal_name = models.CharField(max_length=120, default="Terminal principal")
    current_room_id = models.PositiveSmallIntegerField(
        default=RoomDirectory.default_room_id
    )
    theme_preference = models.CharField(
        max_length=10,
        choices=ThemePreference.choices,
        default=ThemePreference.LIGHT,
    )
    company_name = models.CharField(max_length=120, default="Casinos Gala")
    coupon_legend = models.TextField(
        default=(
            "El Juego Compulsivo es Perjudicial para la Salud y Produce Adicción ley 6169"
        )
    )
    operational_hours = models.JSONField(default=default_operational_hours, blank=True)
    terms_text = models.TextField(
        default="Al registrarse, acepta los términos y condiciones del sorteo."
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at",)

    def __str__(self) -> str:
        return f"{self.terminal_name} [{self.terminal_identifier}] (Sala {self.current_room_id})"

    @property
    def room_name(self) -> str:
        # Resolve the human-readable room name from the directory.
        return RoomDirectory.get(self.current_room_id).name
