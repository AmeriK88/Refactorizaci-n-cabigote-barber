# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import transaction
from django_recaptcha.fields import ReCaptchaField
from django.conf import settings
from .models import UserProfile


class CustomUserCreationForm(UserCreationForm):
    """Registro de usuario con campos extra y ReCAPTCHA."""

    # EXTRA FIELDS FOR AUTOCOMPLETE
    email    = forms.EmailField(label='Correo electrónico',
                widget=forms.EmailInput(attrs={
                    'class': 'form-control form-control-lg',
                    'autocomplete': 'email'
                }))
    phone    = forms.CharField(label='Teléfono', max_length=15,
                widget=forms.TextInput(attrs={
                    'class': 'form-control form-control-lg',
                    'autocomplete': 'tel'
                }))
    nombre   = forms.CharField(label='Nombre', max_length=30,
                widget=forms.TextInput(attrs={
                    'class': 'form-control form-control-lg',
                    'autocomplete': 'given-name'
                }))
    apellido = forms.CharField(label='Apellido', max_length=30,
                widget=forms.TextInput(attrs={
                    'class': 'form-control form-control-lg',
                    'autocomplete': 'family-name'
                }))
    captcha  = ReCaptchaField()

    class Meta(UserCreationForm.Meta): # type: ignore[attr-defined]
        model  = User
        fields = ("username", "email", "phone", "nombre",
                  "apellido", "password1", "password2")
        

    # ---------- INNIT FIELDS -------------------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'autocomplete': 'username'
        })
        for pwd in ('password1', 'password2'):
            self.fields[pwd].widget.attrs.update({
                'class': 'form-control form-control-lg',
                'autocomplete': 'new-password'
            })

    # ---------- VALIDATIONS ---------------------------------
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este email ya está registrado.")
        return email

    def clean_password2(self):
        pw1 = self.cleaned_data.get('password1')
        pw2 = self.cleaned_data.get('password2')
        if pw1 and pw2 and pw1 != pw2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return pw2

    def clean_username(self):
        username = self.cleaned_data['username']
        if username == 'admin':
            raise forms.ValidationError("El nombre de usuario 'admin' está prohibido.")
        if username in settings.BLACKLISTED_USERNAMES:
            raise forms.ValidationError(f"El nombre '{username}' está prohibido.")
        return username

    # ---------- ATOMIC SAVE -----------------------------
    def save(self, commit=True):
        with transaction.atomic():
            user = super().save(commit=False)
            user.email      = self.cleaned_data['email']
            user.first_name = self.cleaned_data['nombre']
            user.last_name  = self.cleaned_data['apellido']
            if commit:
                user.save()
                UserProfile.objects.create(
                    user      = user,
                    telefono  = self.cleaned_data['phone'],
                    email     = user.email,
                    nombre    = self.cleaned_data['nombre'],
                    apellido  = self.cleaned_data['apellido'],
                )
        return user

# ---------- AUTHENTICATION FORM -----------------------------
class CustomAuthenticationForm(AuthenticationForm):
    captcha = ReCaptchaField()


class UserProfileForm(forms.ModelForm):
    class Meta:
        model   = UserProfile
        fields  = ['email', 'telefono']
        widgets = {
            'email':    forms.EmailInput(attrs={'autocomplete': 'email'}),
            'telefono': forms.TextInput(attrs={'autocomplete': 'tel'}),
        }


class UserForm(forms.ModelForm):
    class Meta:
        model   = User
        fields  = ['email']
        widgets = {
            'email': forms.EmailInput(
                attrs={'autocomplete': 'email', 'id': 'user-email'}
            ),
        }




