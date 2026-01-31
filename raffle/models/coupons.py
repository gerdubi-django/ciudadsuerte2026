from django.conf import settings
from django.db import models
from django.utils import timezone

# Importamos RoomDirectory pero no lo ejecutamos al declarar modelos
from ..rooms import RoomDirectory


class Coupon(models.Model):
    ENTRY = "entry"
    REGISTER = "register"
    MANUAL = "manual"
    SOURCE_CHOICES = (
        (ENTRY, "Cargó Voucher"),
        (REGISTER, "Registro"),
        (MANUAL, "Ingreso manual"),
    )

    person = models.ForeignKey("raffle.Person", related_name="coupons", on_delete=models.CASCADE)
    code = models.CharField(max_length=120, unique=True)
    scanned_at = models.DateTimeField(default=timezone.now)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    created_by_user = models.BooleanField(default=False)
    reprint_count = models.PositiveSmallIntegerField(default=0)
    terminal_name = models.CharField(max_length=120, default="")
    printed = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="generated_coupons",
        on_delete=models.SET_NULL,
    )

    # FIX: no ejecutar RoomDirectory.choices() en tiempo de importación
    room_id = models.PositiveSmallIntegerField(
        choices=[],         # choices dinámicas se cargan en formularios, NO aquí
        default=1           # valor por defecto seguro
    )

    class Meta:
        ordering = ("-scanned_at",)

    def __str__(self) -> str:
        return f"{self.code} - {self.person}"

    @property
    def room(self):
        """Return the room dataclass for this coupon."""
        return RoomDirectory.get(self.room_id)

    @property
    def room_name(self) -> str:
        return self.room.name


class CouponSequence(models.Model):
    room_id = models.PositiveSmallIntegerField()
    terminal_name = models.CharField(max_length=120)
    last_number = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("room_id", "terminal_name")
        ordering = ("room_id", "terminal_name")

    def __str__(self) -> str:
        return f"{self.room_id}-{self.terminal_name}: {self.last_number}"


class ManualCouponSequence(models.Model):
    room_id = models.PositiveSmallIntegerField()
    last_number = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("room_id",)
        ordering = ("room_id",)

    def __str__(self) -> str:
        return f"MN-{self.room_id}: {self.last_number}"


class VoucherScan(models.Model):
    code = models.CharField(max_length=64, unique=True)
    person = models.ForeignKey("raffle.Person", related_name="voucher_scans", on_delete=models.CASCADE)

    terminal_name = models.CharField(max_length=120, default="")

    # FIX igual que Coupon
    room_id = models.PositiveSmallIntegerField(
        choices=[],
        default=1
    )

    source = models.CharField(max_length=20, choices=Coupon.SOURCE_CHOICES)
    scanned_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ("-scanned_at",)

    def __str__(self) -> str:
        return f"{self.code} - {self.person}"

    @property
    def room(self):
        return RoomDirectory.get(self.room_id)

    @property
    def room_name(self) -> str:
        return self.room.name


class CouponReprint(models.Model):
    coupon = models.OneToOneField(
        Coupon, related_name="reprint", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="coupon_reprints", on_delete=models.CASCADE
    )

    # FIX igual que en los otros
    room_id = models.PositiveSmallIntegerField(
        choices=[],
        default=1
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"Reprint {self.coupon.code} by {self.user}"


class CouponReprintLog(models.Model):
    coupon = models.ForeignKey(
        Coupon, related_name="reprint_logs", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="coupon_reprint_logs", on_delete=models.CASCADE
    )
    room_id = models.PositiveSmallIntegerField(default=1)
    reprint_number = models.PositiveSmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"Log {self.reprint_number} for {self.coupon.code} by {self.user}"
