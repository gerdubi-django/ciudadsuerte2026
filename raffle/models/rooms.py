"""Models for configurable rooms."""

from django.db import models


class Room(models.Model):
    name = models.CharField(max_length=120)
    room_ip = models.CharField(max_length=120, blank=True, default="")

    class Meta:
        ordering = ("id",)

    def __str__(self) -> str:
        return f"Sala {self.name}" if not self.name.lower().startswith("sala") else self.name
