from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Administrador"
        CASHIER = "cambista", "Cambista"
        FLOOR_MANAGER = "jefesala", "Jefe de sala"
        USER = "user", "Operador (legado)"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CASHIER)

    def is_admin(self) -> bool:
        # Check whether the user has administrator role.
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_cashier(self) -> bool:
        # Determine whether the user can operate as cashier.
        return self.role in {self.Role.CASHIER, self.Role.USER}

    @property
    def is_cashier_only(self) -> bool:
        # Confirm the user is strictly a cashier without legacy permissions.
        return self.role == self.Role.CASHIER

    @property
    def is_floor_manager(self) -> bool:
        # Determine whether the user supervises the room.
        return self.role == self.Role.FLOOR_MANAGER

    @property
    def has_operator_access(self) -> bool:
        # Confirm whether the user can access staff features.
        return self.is_admin() or self.is_cashier or self.is_floor_manager

    @property
    def has_reprint_access(self) -> bool:
        # Allow reprints only for administrators or floor managers.
        return self.is_admin() or self.is_floor_manager

    @property
    def has_manual_access(self) -> bool:
        # Allow manual coupon workflows for authorized operators.
        return self.is_admin() or self.is_cashier or self.is_floor_manager

    @property
    def display_name(self) -> str:
        # Provide a readable representation for the UI.
        full_name = self.get_full_name().strip()
        return full_name or self.username
