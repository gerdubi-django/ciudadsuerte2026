"""Launch the development server after ensuring terminal configuration."""

from __future__ import annotations

from django.core.management.base import CommandError
from django.core.management.commands.runserver import Command as RunserverCommand

from raffle.utils.terminal import get_terminal_config, save_terminal_config


class Command(RunserverCommand):
    help = "Run the server using a local terminal configuration."  # noqa: A003

    def handle(self, *args, **options):  # type: ignore[override]
        config = get_terminal_config()
        if config is None:
            terminal_id = input("Ingrese número de terminal: ").strip()
            room_id_raw = input("Ingrese ID de sala (Room.id): ").strip()
            room_ip = input("Ingrese IP de la sala: ").strip()

            if not terminal_id:
                raise CommandError("El número de terminal es obligatorio.")

            try:
                room_id = int(room_id_raw)
            except ValueError as exc:
                raise CommandError("El ID de sala debe ser numérico.") from exc

            if not room_ip:
                raise CommandError("La IP de la sala es obligatoria.")

            config = save_terminal_config(terminal_id=terminal_id, room_id=room_id, room_ip=room_ip)
            self.stdout.write(self.style.SUCCESS("Configuración de terminal guardada."))
        else:
            self.stdout.write("Usando configuración de terminal existente.")

        super().handle(*args, **options)
