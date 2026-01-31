from django import forms

from ..models import Room
from ..utils.terminal import DEFAULT_PRINTER_NAME, DEFAULT_PRINTER_PORT


class TerminalConfigForm(forms.Form):
    terminal_id = forms.CharField(
        label="Número de terminal",
        max_length=120,
        widget=forms.TextInput(attrs={"class": "admin-input", "placeholder": "Ej: T01"}),
    )
    room_id = forms.ModelChoiceField(
        label="Sala",
        queryset=Room.objects.none(),
        widget=forms.Select(attrs={"class": "admin-select"}),
    )
    room_ip = forms.CharField(
        label="IP de la sala",
        max_length=120,
        widget=forms.TextInput(attrs={"class": "admin-input", "placeholder": "10.x.x.x"}),
    )
    printer_name = forms.CharField(
        label="Nombre de impresora",
        max_length=128,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "admin-input", "placeholder": DEFAULT_PRINTER_NAME}
        ),
    )
    printer_port = forms.CharField(
        label="Puerto de impresora",
        max_length=64,
        required=False,
        widget=forms.TextInput(attrs={"class": "admin-input", "placeholder": DEFAULT_PRINTER_PORT}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["room_id"].queryset = Room.objects.all().order_by("id")
        self.fields["printer_name"].initial = (
            self.initial.get("printer_name") or DEFAULT_PRINTER_NAME
        )
        self.fields["printer_port"].initial = (
            self.initial.get("printer_port") or DEFAULT_PRINTER_PORT
        )
