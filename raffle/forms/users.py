from django import forms
from django.contrib.auth import get_user_model


UserModel = get_user_model()


class AdminUserForm(forms.ModelForm):
    password = forms.CharField(
        label="CLAVE",
        required=False,
        widget=forms.PasswordInput(),
        help_text="Deje en blanco para mantener la clave actual.",
    )

    class Meta:
        model = UserModel
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "is_active",
        )
        labels = {
            "username": "USUARIO",
            "first_name": "NOMBRE",
            "last_name": "APELLIDO",
            "email": "EMAIL",
            "role": "ROL",
            "is_active": "ESTADO",
        }
        widgets = {
            "username": forms.TextInput(attrs={"class": "admin-input"}),
            "first_name": forms.TextInput(attrs={"class": "admin-input"}),
            "last_name": forms.TextInput(attrs={"class": "admin-input"}),
            "email": forms.EmailInput(attrs={"class": "admin-input"}),
            "role": forms.Select(attrs={"class": "admin-select"}),
            "is_active": forms.CheckboxInput(attrs={"class": "admin-checkbox__input"}),
        }

    def __init__(self, *args, **kwargs):
        # Avoid rendering password for superusers to keep parity with admin site.
        super().__init__(*args, **kwargs)
        self.fields["password"].widget.attrs.update({"class": "admin-input"})
        if self.instance and self.instance.is_superuser:
            self.fields["role"].disabled = True
            self.fields["is_active"].disabled = True

    def clean_password(self):
        # Only enforce password on create operations.
        password = self.cleaned_data.get("password")
        if not self.instance.pk and not password:
            raise forms.ValidationError("La clave es obligatoria para nuevos usuarios.")
        return password

    def save(self, commit=True):
        # Persist the user and refresh password when provided.
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


class AdminUserDeleteForm(forms.Form):
    user_id = forms.IntegerField(min_value=1)

