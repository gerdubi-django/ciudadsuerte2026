"""Room directory utilities backed by the database when available."""

from dataclasses import dataclass
from typing import Dict, Iterable, Tuple

from django.apps import apps
from django.db import DatabaseError, OperationalError, ProgrammingError, connection


@dataclass(frozen=True)
class Room:
    """Data structure representing a room."""

    id: int
    name: str
    room_ip: str = ""


class RoomDirectory:
    """Directory that resolves room identifiers."""

    _DEFAULT_ROOMS: Dict[int, Room] = {
        1: Room(id=1, name="SCN", room_ip="10.32.51.18"),
        2: Room(id=2, name="SSP", room_ip="10.32.53.18"),
        3: Room(id=3, name="SCC", room_ip="10.32.51.18"),
        4: Room(id=4, name="R11", room_ip="10.32.52.18"),
        5: Room(id=5, name="SGU", room_ip="10.32.54.18"),
        6: Room(id=6, name="SFO", room_ip="10.32.57.18"),
        7: Room(id=7, name="SBQ", room_ip="10.32.56.18"),
        8: Room(id=8, name="ERAY", room_ip="10.32.58.18"),
    }

    @classmethod
    def _room_model(cls):
        """Return the Django model used to persist rooms."""

        return apps.get_model("raffle", "Room")

    @classmethod
    def _load_from_db(cls) -> Dict[int, Room]:
        """Return rooms stored in the database or fall back to defaults."""

        def _query_rooms() -> Dict[int, Room]:
            model = cls._room_model()
            entries = model.objects.order_by("id")
            if not entries.exists():
                return cls._DEFAULT_ROOMS
            return {
                entry.id: Room(id=entry.id, name=entry.name, room_ip=entry.room_ip)
                for entry in entries
            }

        try:
            return _query_rooms()
        except DatabaseError:
            connection.close()  # Retry once after closing a potentially stale connection.
            try:
                return _query_rooms()
            except DatabaseError:
                return cls._DEFAULT_ROOMS
        except (LookupError, ProgrammingError, OperationalError):
            return cls._DEFAULT_ROOMS

    @classmethod
    def all(cls) -> Iterable[Room]:
        """Yield every registered room."""

        return cls._load_from_db().values()

    @classmethod
    def get(cls, room_id: int) -> Room:
        """Return the room that matches the identifier."""

        rooms = cls._load_from_db()
        return rooms[room_id]

    @classmethod
    def choices(cls) -> Tuple[Tuple[int, str], ...]:
        """Return choices for Django model and form fields."""

        rooms = cls._load_from_db().values()
        return tuple((room.id, room.name) for room in rooms)

    @classmethod
    def default_room_id(cls) -> int:
        """Return the default room identifier."""

        return next(iter(cls._load_from_db()))
