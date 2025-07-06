from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile
from django_recaptcha.fields import ReCaptchaField
from django.conf import settings
from django.db import transaction

# Formulario de creación de usuario personalizado
class CustomUserCreationForm(UserCreationForm):
    email    = forms.EmailField(label="Correo",    widget=forms.EmailInput(
                 attrs={"class": "form-control form-control-lg", "autocomplete": "email"}))
    phone    = forms.CharField(label="Teléfono",   widget=forms.TextInput(
                 attrs={"class": "form-control form-control-lg", "autocomplete": "tel"}))
    nombre   = forms.CharField(label="Nombre",     widget=forms.TextInput(
                 attrs={"class": "form-control form-control-lg", "autocomplete": "given-name"}))
    apellido = forms.CharField(label="Apellido",   widget=forms.TextInput(
                 attrs={"class": "form-control form-control-lg", "autocomplete": "family-name"}))
    captcha  = ReCaptchaField()

    class Meta(UserCreationForm.Meta):
        model  = User
        fields = ("username", "email", "phone", "nombre", "apellido", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Añadimos clase y autocomplete a los campos heredados:
        self.fields["username"].widget.attrs.update(
            {"class": "form-control form-control-lg", "autocomplete": "username"})
        self.fields["password1"].widget.attrs.update(
            {"class": "form-control form-control-lg", "autocomplete": "new-password"})
        self.fields["password2"].widget.attrs.update(
            {"class": "form-control form-control-lg", "autocomplete": "new-password"})


    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este email ya está registrado.")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return password2

    def save(self, commit=True):
        """Crea User y su UserProfile en una transacción."""
        with transaction.atomic():
            user = super().save(commit=False)
            user.email      = self.cleaned_data["email"]
            user.first_name = self.cleaned_data["nombre"]
            user.last_name  = self.cleaned_data["apellido"]

            if commit:
                user.save()
                UserProfile.objects.create(
                    user=user,
                    telefono=self.cleaned_data["phone"],
                    email=user.email,
                    nombre=self.cleaned_data["nombre"],
                    apellido=self.cleaned_data["apellido"],
                )
        return user

    def clean_username(self):
        username = self.cleaned_data.get('username')

        # Verificar si el nombre de usuario está en la lista negra
        if username == 'admin' and not self.instance.is_superuser:
            raise forms.ValidationError(f"El nombre de usuario '{username}' está prohibido.")
    
        if username in settings.BLACKLISTED_USERNAMES:
            raise forms.ValidationError(f"El nombre de usuario '{username}' está prohibido.")

        return username

# Formulario de autenticación personalizado
class CustomAuthenticationForm(AuthenticationForm):
    captcha = ReCaptchaField()

# Formulario de perfil de usuario
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['email', 'telefono']
        widgets = {
            'email': forms.EmailInput(attrs={'autocomplete': 'email'}),
            'telefono': forms.TextInput(attrs={'autocomplete': 'tel'}),
        }

# Formulario de actualización de email
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'autocomplete': 'email', 'id': 'user-email'}),
        }
