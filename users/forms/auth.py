from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django_recaptcha.fields import ReCaptchaField

from users.services.auth import register_user


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={"class": "form-control form-control-lg", "autocomplete": "email"}),
    )
    phone = forms.CharField(
        label="Teléfono",
        max_length=15,
        widget=forms.TextInput(attrs={"class": "form-control form-control-lg", "autocomplete": "tel"}),
    )
    nombre = forms.CharField(
        label="Nombre",
        max_length=30,
        widget=forms.TextInput(attrs={"class": "form-control form-control-lg", "autocomplete": "given-name"}),
    )
    apellido = forms.CharField(
        label="Apellido",
        max_length=30,
        widget=forms.TextInput(attrs={"class": "form-control form-control-lg", "autocomplete": "family-name"}),
    )
    captcha = ReCaptchaField()

    class Meta(UserCreationForm.Meta):  # type: ignore[attr-defined]
        model = User
        fields = ("username", "email", "phone", "nombre", "apellido", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "form-control form-control-lg", "autocomplete": "username"})
        for pwd in ("password1", "password2"):
            self.fields[pwd].widget.attrs.update({"class": "form-control form-control-lg", "autocomplete": "new-password"})

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este email ya está registrado.")
        return email

    def clean_username(self):
        username = self.cleaned_data["username"]
        if username == "admin":
            raise forms.ValidationError("El nombre de usuario 'admin' está prohibido.")
        if username in getattr(settings, "BLACKLISTED_USERNAMES", []):
            raise forms.ValidationError(f"El nombre '{username}' está prohibido.")
        return username

    def save(self, commit=True):
        """
        Delegamos a service para que el form no tenga lógica de negocio.
        """
        return register_user(
            username=self.cleaned_data["username"],
            password=self.cleaned_data["password1"],
            email=self.cleaned_data["email"],
            first_name=self.cleaned_data["nombre"],
            last_name=self.cleaned_data["apellido"],
            phone=self.cleaned_data["phone"],
        )


class CustomAuthenticationForm(AuthenticationForm):
    captcha = ReCaptchaField()
