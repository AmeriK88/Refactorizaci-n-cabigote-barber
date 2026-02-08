from django import forms
from django.contrib.auth.models import User


class ProfileDataForm(forms.Form):
    first_name = forms.CharField(
        label="Nombre",
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={"autocomplete": "given-name"}),
    )
    last_name = forms.CharField(
        label="Apellido",
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={"autocomplete": "family-name"}),
    )
    email = forms.EmailField(
        label="Correo electrónico",
        required=False,
        widget=forms.EmailInput(attrs={"autocomplete": "email", "id": "user-email"}),
    )
    telefono = forms.CharField(
        label="Teléfono",
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={"autocomplete": "tel"}),
    )

    def __init__(self, *, user, initial=None, **kwargs):
        self.user = user
        super().__init__(initial=initial, **kwargs)

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip()
        if not email:
            return email

        if User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("Este email ya está en uso por otro usuario.")
        return email
