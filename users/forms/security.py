from django.contrib.auth.forms import PasswordChangeForm


class PasswordChangeFormSafe(PasswordChangeForm):
    """
    Wrapper por si luego quieres añadir requisitos/validaciones sin tocar las views.
    """
    pass
