from django import forms
from django import forms
from django.contrib.auth import authenticate

from ..rooms import RoomDirectory
from ..services import validate_voucher_code


class AdminLoginForm(forms.Form):
    username = forms.CharField(label="USUARIO", max_length=150)
    password = forms.CharField(label="CLAVE", widget=forms.PasswordInput())
    room_id = forms.ChoiceField(
        label="SALA ACTUAL",
        choices=(),
        widget=forms.Select(attrs={"class": "admin-select"}),
    )

    error_messages = {
        "invalid_login": "Usuario o clave incorrectos.",
        "inactive": "La cuenta se encuentra deshabilitada.",
    }

    def __init__(self, request=None, *args, **kwargs):
        # Keep request reference to authenticate against the current backend.
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)
        self.fields["room_id"].choices = RoomDirectory.choices()

    def clean(self):
        # Validate the provided credentials.
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")
        if username and password:
            self.user_cache = authenticate(
                self.request, username=username, password=password
            )
            if self.user_cache is None:
                raise forms.ValidationError(self.error_messages["invalid_login"])
            if not self.user_cache.is_active:
                raise forms.ValidationError(self.error_messages["inactive"])
        return cleaned_data

    def clean_room_id(self) -> int:
        # Validate and normalize selected room identifier.
        room_id = int(self.cleaned_data.get("room_id", 0))
        valid_rooms = {room[0] for room in RoomDirectory.choices()}
        if room_id not in valid_rooms:
            raise forms.ValidationError("Seleccione una sala válida.")
        return room_id

    def get_user(self):
        # Expose the authenticated user instance.
        return self.user_cache


class VoucherAPITestForm(forms.Form):
    voucher_code = forms.CharField(label="Voucher", max_length=255)
    room_id = forms.ChoiceField(
        label="Sala",
        choices=(),
        widget=forms.Select(attrs={"class": "admin-select"}),
    )

    def __init__(self, *args, **kwargs):
        # Populate room choices with configured rooms.
        super().__init__(*args, **kwargs)
        self.fields["room_id"].choices = RoomDirectory.choices()

    def clean_voucher_code(self) -> str:
        # Normalize voucher input and require a value.
        code = self.cleaned_data.get("voucher_code", "").strip().upper()
        if not code:
            raise forms.ValidationError("Ingrese un voucher válido.")
        return code

    def clean_room_id(self) -> int:
        # Ensure selected room exists in directory.
        room_id = int(self.cleaned_data.get("room_id", 0))
        valid_rooms = {room[0] for room in RoomDirectory.choices()}
        if room_id not in valid_rooms:
            raise forms.ValidationError("Seleccione una sala válida.")
        return room_id

    def validate_remote(self):
        # Execute remote validation and return result.
        code = self.cleaned_data["voucher_code"]
        room_id = self.cleaned_data["room_id"]
        return validate_voucher_code(code, room_id)
