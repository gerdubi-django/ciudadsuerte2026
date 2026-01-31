from django import forms

from ..rooms import RoomDirectory


class EntryForm(forms.Form):
    id_number = forms.CharField(
        label="DNI",
        max_length=20,
        widget=forms.TextInput(
            attrs={"class": "admin-input", "placeholder": "Ingrese DNI"}
        ),
    )
    room_id = forms.ChoiceField(
        label="SALA",
        choices=RoomDirectory.choices(),
        initial=RoomDirectory.default_room_id(),
        widget=forms.HiddenInput(),
    )
    voucher_code = forms.CharField(required=True, widget=forms.HiddenInput())

    def clean_room_id(self) -> int:
        """Validate and convert the selected room identifier."""

        return int(self.cleaned_data["room_id"])

    def clean_voucher_code(self) -> str:
        """Normalize the captured voucher code."""

        code = self.cleaned_data["voucher_code"].strip()
        if not code:
            raise forms.ValidationError("Escanee un voucher válido.")
        return code.upper()
