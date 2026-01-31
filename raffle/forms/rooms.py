"""Forms for managing room names."""

from django import forms

from ..models import Room


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ("name", "room_ip")
        labels = {"name": "Nombre de la sala", "room_ip": "IP de la sala"}
        widgets = {
            "name": forms.TextInput(attrs={"class": "admin-input"}),
            "room_ip": forms.TextInput(
                attrs={"class": "admin-input", "placeholder": "10.5.32.82"}
            ),
        }

    def clean_room_ip(self) -> str:
        # Validate the provided IP address format.
        value = (self.cleaned_data.get("room_ip") or "").strip()
        if not value:
            return ""
        octets = value.split(".")
        if len(octets) != 4:
            raise forms.ValidationError("Ingrese una IP válida en formato A.B.C.D")
        for octet in octets:
            if not octet.isdigit() or not 0 <= int(octet) <= 255:
                raise forms.ValidationError("Cada segmento de la IP debe ser numérico entre 0 y 255")
        return value
