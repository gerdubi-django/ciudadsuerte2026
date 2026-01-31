"""Forms for system configuration management."""

from datetime import datetime, time

from django import forms

from ..models import SystemSettings
from ..rooms import RoomDirectory


class SystemSettingsForm(forms.ModelForm):
    terminal_name = forms.CharField(
        label="NOMBRE DEL TERMINAL",
        max_length=120,
        widget=forms.TextInput(attrs={"class": "admin-input"}),
    )
    company_name = forms.CharField(
        label="NOMBRE DE EMPRESA",
        max_length=120,
        widget=forms.TextInput(attrs={"class": "admin-input"}),
    )
    current_room_id = forms.ChoiceField(
        label="SALA ACTUAL",
        choices=(),
        widget=forms.Select(attrs={"class": "admin-select"}),
    )
    theme_preference = forms.ChoiceField(
        label="TEMA DEL PANEL",
        choices=SystemSettings.ThemePreference.choices,
        widget=forms.Select(attrs={"class": "admin-select", "data-theme-select": "true"}),
    )
    entry_hours_start = forms.TimeField(
        label="Hora de inicio",
        required=False,
        widget=forms.TimeInput(attrs={"class": "admin-input", "type": "time"}),
        help_text="Inicio del horario operativo para aplicar multiplicador a ingresos.",
    )
    entry_hours_end = forms.TimeField(
        label="Hora de fin",
        required=False,
        widget=forms.TimeInput(attrs={"class": "admin-input", "type": "time"}),
        help_text="Fin del horario operativo para aplicar multiplicador a ingresos.",
    )
    entry_multiplier = forms.IntegerField(
        label="Multiplicador",
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={"class": "admin-input", "min": 1}),
        help_text="Cantidad de cupones por ingreso dentro del horario operativo.",
    )
    operational_hours = forms.JSONField(
        required=False,
        widget=forms.HiddenInput(),
    )
    coupon_legend = forms.CharField(
        label="LEYENDA PARA CUPONES",
        widget=forms.Textarea(attrs={"class": "admin-textarea", "rows": 2}),
    )
    terms_text = forms.CharField(
        label="TÉRMINOS Y CONDICIONES",
        widget=forms.Textarea(attrs={"class": "admin-textarea", "rows": 4}),
    )

    class Meta:
        model = SystemSettings
        fields = (
            "terminal_name",
            "company_name",
            "current_room_id",
            "theme_preference",
            "operational_hours",
            "coupon_legend",
            "terms_text",
        )

    def __init__(self, *args, **kwargs):
        # Populate the simple operational hour fields from the stored schedule.
        super().__init__(*args, **kwargs)
        self.fields["current_room_id"].choices = RoomDirectory.choices()
        schedule = self.instance.operational_hours or []
        if schedule:
            first_slot = schedule[0]
            self.fields["entry_hours_start"].initial = self._parse_time_value(
                first_slot.get("start")
            )
            self.fields["entry_hours_end"].initial = self._parse_time_value(
                first_slot.get("end")
            )
            self.fields["entry_multiplier"].initial = first_slot.get("multiplier")

    @staticmethod
    def _parse_time_value(value: str | None) -> time | None:
        # Convert a HH:MM string into a time object for the form.
        if not value:
            return None
        try:
            return datetime.strptime(str(value), "%H:%M").time()
        except ValueError:
            return None

    def clean_current_room_id(self) -> int:
        # Ensure the selected room identifier is valid.
        room_id = int(self.cleaned_data["current_room_id"])
        valid_rooms = {room[0] for room in RoomDirectory.choices()}
        if room_id not in valid_rooms:
            raise forms.ValidationError("Seleccione una sala válida.")
        return room_id

    def clean(self):
        # Consolidate the operational schedule into a single range payload.
        cleaned_data = super().clean()
        start_time = cleaned_data.get("entry_hours_start")
        end_time = cleaned_data.get("entry_hours_end")
        multiplier = cleaned_data.get("entry_multiplier")

        if any([start_time, end_time, multiplier]):
            if not start_time or not end_time or multiplier is None:
                raise forms.ValidationError(
                    "Debe completar inicio, fin y multiplicador para los horarios operativos."
                )
            if isinstance(start_time, str):
                start_time = datetime.strptime(start_time, "%H:%M").time()
            if isinstance(end_time, str):
                end_time = datetime.strptime(end_time, "%H:%M").time()
            if start_time >= end_time:
                raise forms.ValidationError(
                    "La hora de inicio debe ser anterior a la hora de fin."
                )
            cleaned_data["operational_hours"] = [
                {
                    "start": start_time.strftime("%H:%M"),
                    "end": end_time.strftime("%H:%M"),
                    "multiplier": int(multiplier),
                }
            ]
        else:
            cleaned_data["operational_hours"] = []
        return cleaned_data
