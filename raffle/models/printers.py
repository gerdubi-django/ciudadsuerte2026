from django.db import models


class PrinterConfiguration(models.Model):
    class ThemePreference(models.TextChoices):
        LIGHT = "light", "Tema claro"
        DARK = "dark", "Tema oscuro"

    manufacturer = models.CharField(max_length=120, default="3nStar")
    model = models.CharField(max_length=120, default="RPT006")
    port = models.CharField(max_length=120, default="USB001")
    vendor_id = models.CharField(max_length=8, default="0x0416")
    product_id = models.CharField(max_length=8, default="0x5011")
    queue_name = models.CharField(max_length=128, blank=True, default="POS-80")
    paper_width_mm = models.PositiveSmallIntegerField(default=80)
    theme_preference = models.CharField(
        max_length=10,
        choices=ThemePreference.choices,
        default=ThemePreference.LIGHT,
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at",)

    def __str__(self) -> str:
        return f"{self.manufacturer} {self.model} @ {self.port} ({self.paper_width_mm}mm)"

    def usb_identifiers(self) -> tuple[int, int]:
        """Return vendor and product identifiers parsed as integers."""

        def parse_identifier(raw_value: str) -> int:
            """Parse a string identifier handling hex and decimal values."""

            value = raw_value.strip()
            base = 16 if value.lower().startswith("0x") else 10
            return int(value, base)

        return parse_identifier(self.vendor_id), parse_identifier(self.product_id)
