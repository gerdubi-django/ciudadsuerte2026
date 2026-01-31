from django import forms

from ..models import PrinterConfiguration
from ..utils.terminal import DEFAULT_PRINTER_NAME, DEFAULT_PRINTER_PORT


class PrinterConfigurationForm(forms.ModelForm):
    PORT_CHOICES = (
        ("USB001", "USB001"),
        ("USB002", "USB002"),
        ("COM1", "COM1"),
        ("COM2", "COM2"),
        ("COM3", "COM3"),
    )
    PAPER_WIDTH_CHOICES = ((80, "80 mm"),)

    manufacturer = forms.CharField(
        label="FABRICANTE",
        max_length=120,
        widget=forms.TextInput(attrs={"class": "admin-input"}),
    )
    model = forms.CharField(
        label="MODELO",
        max_length=120,
        widget=forms.TextInput(attrs={"class": "admin-input"}),
    )
    port = forms.ChoiceField(
        label="PUERTO",
        choices=PORT_CHOICES,
        widget=forms.Select(attrs={"class": "admin-select"}),
    )
    vendor_id = forms.CharField(
        label="VID",
        max_length=8,
        widget=forms.TextInput(attrs={"class": "admin-input"}),
    )
    product_id = forms.CharField(
        label="PID",
        max_length=8,
        widget=forms.TextInput(attrs={"class": "admin-input"}),
    )
    queue_name = forms.CharField(
        label="COLA",
        max_length=128,
        required=False,
        widget=forms.TextInput(attrs={"class": "admin-input"}),
    )
    paper_width_mm = forms.ChoiceField(
        label="ANCHO DEL PAPEL",
        choices=PAPER_WIDTH_CHOICES,
        widget=forms.Select(attrs={"class": "admin-select"}),
    )
    theme_preference = forms.ChoiceField(
        label="TEMA DEL PANEL",
        choices=PrinterConfiguration.ThemePreference.choices,
        widget=forms.Select(
            attrs={"class": "admin-select", "data-theme-select": "true"}
        ),
    )

    class Meta:
        model = PrinterConfiguration
        fields = (
            "manufacturer",
            "model",
            "port",
            "vendor_id",
            "product_id",
            "queue_name",
            "paper_width_mm",
            "theme_preference",
        )

    def __init__(self, *args, **kwargs):
        # Make sure the current port appears in the available choices.
        super().__init__(*args, **kwargs)
        current_port = self.instance.port if self.instance else None
        if current_port and current_port not in dict(self.fields["port"].choices):
            self.fields["port"].choices += ((current_port, current_port),)

    def clean_paper_width_mm(self) -> int:
        # Convert the selected paper width to integer.
        return int(self.cleaned_data["paper_width_mm"])

    def clean_vendor_id(self) -> str:
        # Normalize the vendor identifier representation.
        return self._normalize_identifier("vendor_id")

    def clean_product_id(self) -> str:
        # Normalize the product identifier representation.
        return self._normalize_identifier("product_id")

    def _normalize_identifier(self, field_name: str) -> str:
        # Convert USB identifiers to hexadecimal uppercase strings.
        value = self.cleaned_data[field_name].strip()
        try:
            parsed = int(value, 16 if value.lower().startswith("0x") else 10)
        except ValueError as exc:
            raise forms.ValidationError("Ingrese un identificador válido.") from exc
        return f"0x{parsed:04X}"


class LocalPrinterConfigForm(forms.Form):
    printer_name = forms.CharField(
        label="Nombre de impresora local",
        max_length=128,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "admin-input", "placeholder": DEFAULT_PRINTER_NAME}
        ),
    )
    printer_port = forms.ChoiceField(
        label="Puerto de impresora local",
        choices=PrinterConfigurationForm.PORT_CHOICES,
        widget=forms.Select(attrs={"class": "admin-select"}),
        initial=DEFAULT_PRINTER_PORT,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        current_port = (self.initial.get("printer_port") or DEFAULT_PRINTER_PORT).strip()
        if current_port and current_port not in dict(self.fields["printer_port"].choices):
            self.fields["printer_port"].choices += ((current_port, current_port),)

    def clean_printer_name(self) -> str:
        # Normalize the printer name and fallback to default when missing.
        value = (self.cleaned_data.get("printer_name") or "").strip()
        return value or DEFAULT_PRINTER_NAME
