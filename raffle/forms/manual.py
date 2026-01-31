from django import forms

from ..rooms import RoomDirectory


class ManualCouponForm(forms.Form):
    id_number = forms.CharField(
        label="DNI",
        max_length=20,
        widget=forms.TextInput(
            attrs={"class": "admin-input", "placeholder": "Ingrese DNI"}
        ),
    )

    def clean_id_number(self) -> str:
        # Standardize the provided id number.
        return self.cleaned_data["id_number"].strip()


class ManualPendingFilterForm(forms.Form):
    room_id = forms.ChoiceField(
        label="Sala",
        choices=(),
        widget=forms.Select(attrs={"class": "admin-select"}),
    )

    def __init__(self, *args, **kwargs):
        # Load room choices dynamically.
        super().__init__(*args, **kwargs)
        self.fields["room_id"].choices = RoomDirectory.choices()

    def clean_room_id(self) -> int:
        # Ensure the selected room is valid.
        value = int(self.cleaned_data.get("room_id", 0))
        valid_rooms = {room[0] for room in RoomDirectory.choices()}
        if value not in valid_rooms:
            raise forms.ValidationError("Seleccione una sala válida.")
        return value
