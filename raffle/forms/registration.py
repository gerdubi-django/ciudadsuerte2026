from datetime import date

from django import forms

from ..models import Person
from ..rooms import RoomDirectory


class RegistrationForm(forms.ModelForm):
    room_id = forms.ChoiceField(
        label="SALA",
        choices=RoomDirectory.choices(),
        initial=RoomDirectory.default_room_id(),
        widget=forms.HiddenInput(),
    )

    class Meta:
        model = Person
        fields = (
            "first_name",
            "last_name",
            "id_number",
            "email",
            "phone",
            "birth_date",
        )
        labels = {
            "first_name": "NOMBRE",
            "last_name": "APELLIDO",
            "id_number": "DNI",
            "email": "EMAIL",
            "phone": "TELÉFONO",
            "birth_date": "FECHA DE NACIMIENTO",
        }
        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "admin-input", "placeholder": "Nombre"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "admin-input", "placeholder": "Apellido"}
            ),
            "id_number": forms.TextInput(
                attrs={"class": "admin-input", "placeholder": "DNI"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "admin-input", "placeholder": "Correo"}
            ),
            "phone": forms.TextInput(
                attrs={"class": "admin-input", "placeholder": "Teléfono"}
            ),
            "birth_date": forms.DateInput(
                attrs={"class": "admin-input", "type": "date"}
            ),
        }

    def clean_room_id(self) -> int:
        """Validate and convert the selected room identifier."""

        return int(self.cleaned_data["room_id"])

    def clean_id_number(self) -> str:
        """Ensure the document number is unique."""

        id_number = self.cleaned_data["id_number"].strip()
        if Person.objects.filter(id_number=id_number).exists():
            raise forms.ValidationError("Ya existe un participante con ese DNI.")
        return id_number

    def clean_email(self) -> str:
        """Normalize the email address before persisting it."""

        return self.cleaned_data["email"].strip().lower()

    def clean_birth_date(self):
        """Validate the age is over eighteen years."""

        birth_date = self.cleaned_data["birth_date"]
        today = date.today()
        age = today.year - birth_date.year - (
            (today.month, today.day) < (birth_date.month, birth_date.day)
        )
        if age < 18:
            raise forms.ValidationError("El participante debe ser mayor de 18 años.")
        return birth_date
